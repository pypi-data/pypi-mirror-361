# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import contextlib
import importlib.util
import logging
import multiprocessing
import os
import queue
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional, Protocol

from .constants import MEMORY_LOAD_LIMIT
from .progress_bar import ProgressBar
from .types import ExecutionMode, ObjectMetadata
from .utils import calculate_worker_processes_and_threads

logger = logging.getLogger(__name__)


def is_ray_available():
    return importlib.util.find_spec("ray") is not None


HAVE_RAY = is_ray_available()

if TYPE_CHECKING:
    from .client import StorageClient


class _Queue(Protocol):
    """
    Protocol defining the interface for queue-like objects.
    """

    def put(self, item: Any, block: bool = True, timeout: Optional[float] = None) -> None: ...

    def get(self, block: bool = True, timeout: Optional[float] = None) -> Any: ...


class _SyncOp(Enum):
    """Enumeration of sync operations that can be performed on files.

    This enum defines the different types of operations that can be queued
    during a synchronization process between source and target storage locations.
    """

    ADD = "add"
    DELETE = "delete"
    STOP = "stop"  # Signal to stop the thread.


class ProducerThread(threading.Thread):
    """
    A producer thread that compares source and target file listings to determine sync operations.

    This thread is responsible for iterating through both source and target storage locations,
    comparing their file listings, and queuing appropriate sync operations (ADD, DELETE, or STOP)
    for worker threads to process. It performs efficient merge-style iteration through sorted
    file listings to determine what files need to be synchronized.

    The thread compares files by their relative paths and metadata (etag, content length,
    last modified time) to determine if files need to be copied, deleted, or can be skipped.

    The thread will put tuples of (_SyncOp, ObjectMetadata) into the file_queue.
    """

    def __init__(
        self,
        source_client: "StorageClient",
        source_path: str,
        target_client: "StorageClient",
        target_path: str,
        progress: ProgressBar,
        file_queue: _Queue,
        num_workers: int,
        delete_unmatched_files: bool = False,
    ):
        super().__init__(daemon=True)
        self.source_client = source_client
        self.target_client = target_client
        self.source_path = source_path
        self.target_path = target_path
        self.progress = progress
        self.file_queue = file_queue
        self.num_workers = num_workers
        self.delete_unmatched_files = delete_unmatched_files

    def _match_file_metadata(self, source_info: ObjectMetadata, target_info: ObjectMetadata) -> bool:
        # If target and source have valid etags defined, use etag and file size to compare.
        if source_info.etag and target_info.etag:
            return source_info.etag == target_info.etag and source_info.content_length == target_info.content_length
        # Else, check file size is the same and the target's last_modified is newer than the source.
        return (
            source_info.content_length == target_info.content_length
            and source_info.last_modified <= target_info.last_modified
        )

    def run(self):
        source_iter = iter(self.source_client.list(prefix=self.source_path))
        target_iter = iter(self.target_client.list(prefix=self.target_path))
        total_count = 0

        source_file = next(source_iter, None)
        target_file = next(target_iter, None)

        while source_file or target_file:
            # Update progress and count each pair (or single) considered for syncing
            if total_count % 1000 == 0:
                self.progress.update_total(total_count)
            total_count += 1

            if source_file and target_file:
                source_key = source_file.key[len(self.source_path) :].lstrip("/")
                target_key = target_file.key[len(self.target_path) :].lstrip("/")

                if source_key < target_key:
                    self.file_queue.put((_SyncOp.ADD, source_file))
                    source_file = next(source_iter, None)
                elif source_key > target_key:
                    if self.delete_unmatched_files:
                        self.file_queue.put((_SyncOp.DELETE, target_file))
                    else:
                        self.progress.update_progress()
                    target_file = next(target_iter, None)  # Skip unmatched target file
                else:
                    # Both exist, compare metadata
                    if not self._match_file_metadata(source_file, target_file):
                        self.file_queue.put((_SyncOp.ADD, source_file))
                    else:
                        self.progress.update_progress()

                    source_file = next(source_iter, None)
                    target_file = next(target_iter, None)
            elif source_file:
                self.file_queue.put((_SyncOp.ADD, source_file))
                source_file = next(source_iter, None)
            else:
                if self.delete_unmatched_files:
                    self.file_queue.put((_SyncOp.DELETE, target_file))
                else:
                    self.progress.update_progress()
                target_file = next(target_iter, None)

        self.progress.update_total(total_count)

        for _ in range(self.num_workers):
            self.file_queue.put((_SyncOp.STOP, None))  # Signal consumers to stop


class ResultConsumerThread(threading.Thread):
    """
    A consumer thread that processes sync operation results and updates metadata.

    This thread is responsible for consuming results from worker processes/threads
    that have completed sync operations (ADD or DELETE). It updates the target
    client's metadata provider with information about the synchronized files,
    ensuring that the metadata store remains consistent with the actual file
    operations performed.
    """

    def __init__(self, target_client: "StorageClient", target_path: str, progress: ProgressBar, result_queue: _Queue):
        super().__init__(daemon=True)
        self.target_client = target_client
        self.target_path = target_path
        self.progress = progress
        self.result_queue = result_queue

    def run(self):
        # Pull from result_queue to collect pending updates from each multiprocessing worker.
        while True:
            op, target_file_path, physical_metadata = self.result_queue.get()

            if op == _SyncOp.STOP:
                break

            if self.target_client._metadata_provider:
                with self.target_client._metadata_provider_lock or contextlib.nullcontext():
                    if op == _SyncOp.ADD:
                        # Use realpath() to get physical path so metadata provider can
                        # track the logical/physical mapping.
                        phys_path, _ = self.target_client._metadata_provider.realpath(target_file_path)
                        physical_metadata.key = phys_path
                        self.target_client._metadata_provider.add_file(target_file_path, physical_metadata)
                    elif op == _SyncOp.DELETE:
                        self.target_client._metadata_provider.remove_file(target_file_path)
                    else:
                        raise RuntimeError(f"Unknown operation: {op}")
            self.progress.update_progress()


class SyncManager:
    """
    Manages the synchronization of files between two storage locations.

    This class orchestrates the entire sync process, coordinating between producer
    threads that identify files to sync, worker processes/threads that perform
    the actual file operations, and consumer threads that update metadata.
    """

    def __init__(
        self, source_client: "StorageClient", source_path: str, target_client: "StorageClient", target_path: str
    ):
        self.source_client = source_client
        self.target_client = target_client
        self.source_path = source_path.lstrip("/")
        self.target_path = target_path.lstrip("/")

        if source_client == target_client and (
            source_path.startswith(target_path) or target_path.startswith(source_path)
        ):
            raise ValueError("Source and target paths cannot overlap on same StorageClient.")

    def sync_objects(
        self,
        execution_mode: ExecutionMode = ExecutionMode.LOCAL,
        description: str = "Syncing",
        num_worker_processes: Optional[int] = None,
        delete_unmatched_files: bool = False,
    ):
        """
        Synchronize objects from source to target storage location.

        This method performs the actual synchronization by coordinating producer
        threads, worker processes/threads, and result consumer threads. It compares
        files between source and target, copying new/modified files and optionally
        deleting unmatched files from the target.

        The sync process uses file metadata (etag, size, modification time) to
        determine if files need to be copied. Files are processed in parallel
        using configurable numbers of worker processes and threads.


        :param execution_mode: Execution mode for sync operations.
        :param description: Description text shown in the progress bar.
        :param num_worker_processes: Number of worker processes to use. If None, automatically determined based on available CPU cores.
        :param delete_unmatched_files: If True, files present in target but not in source will be deleted from target.
        """
        logger.debug(f"Starting sync operation {description}")

        # Attempt to balance the number of worker processes and threads.
        num_worker_processes, num_worker_threads = calculate_worker_processes_and_threads(num_worker_processes)
        num_workers = num_worker_processes * num_worker_threads

        # Create the file and result queues.
        manager = None
        if execution_mode == ExecutionMode.LOCAL:
            if num_worker_processes == 1:
                file_queue = queue.Queue(maxsize=100000)
                result_queue = queue.Queue()
            else:
                manager = multiprocessing.Manager()
                file_queue = manager.Queue(maxsize=100000)
                result_queue = manager.Queue()
        else:
            if not HAVE_RAY:
                raise RuntimeError(
                    "Ray execution mode requested but Ray is not installed. "
                    "To use distributed sync with Ray, install it with: 'pip install ray'. "
                    "Alternatively, use ExecutionMode.LOCAL for single-machine sync operations."
                )

            from .contrib.ray.utils import SharedQueue

            file_queue = SharedQueue(maxsize=100000)
            result_queue = SharedQueue()

        # Create a progress bar to track the progress of the sync operation.
        progress = ProgressBar(desc=description, show_progress=True, total_items=0)

        # Start the producer thread to compare source and target file listings and queue sync operations.
        producer_thread = ProducerThread(
            self.source_client,
            self.source_path,
            self.target_client,
            self.target_path,
            progress,
            file_queue,
            num_workers,
            delete_unmatched_files,
        )
        producer_thread.start()

        # Start the result consumer thread to process the results of individual sync operations
        result_consumer_thread = ResultConsumerThread(
            self.target_client,
            self.target_path,
            progress,
            result_queue,
        )
        result_consumer_thread.start()

        if execution_mode == ExecutionMode.LOCAL:
            if num_worker_processes == 1:
                # Single process does not require multiprocessing.
                _sync_worker_process(
                    self.source_client,
                    self.source_path,
                    self.target_client,
                    self.target_path,
                    num_worker_threads,
                    file_queue,
                    result_queue,
                )
            else:
                with multiprocessing.Pool(processes=num_worker_processes) as pool:
                    pool.starmap(
                        _sync_worker_process,
                        [
                            (
                                self.source_client,
                                self.source_path,
                                self.target_client,
                                self.target_path,
                                num_worker_threads,
                                file_queue,
                                result_queue,
                            )
                            for _ in range(num_worker_processes)
                        ],
                    )
        elif execution_mode == ExecutionMode.RAY:
            if not HAVE_RAY:
                raise RuntimeError(
                    "Ray execution mode requested but Ray is not installed. "
                    "To use distributed sync with Ray, install it with: 'pip install ray'. "
                    "Alternatively, use ExecutionMode.LOCAL for single-machine sync operations."
                )

            import ray

            _sync_worker_process_ray = ray.remote(_sync_worker_process)

            # Start the sync worker processes.
            ray.get(
                [
                    _sync_worker_process_ray.remote(
                        self.source_client,
                        self.source_path,
                        self.target_client,
                        self.target_path,
                        num_worker_threads,
                        file_queue,
                        result_queue,
                    )
                    for _ in range(num_worker_processes)
                ]
            )

        # Wait for the producer thread to finish.
        producer_thread.join()

        # Signal the result consumer thread to stop.
        result_queue.put((_SyncOp.STOP, None, None))
        result_consumer_thread.join()

        # Commit the metadata to the target storage client.
        self.target_client.commit_metadata()

        # Clean up the multiprocessing manager if it was created
        if manager is not None:
            try:
                manager.shutdown()
            except Exception as e:
                logger.warning(f"Error shutting down multiprocessing manager: {e}")

        # Log the completion of the sync operation.
        progress.close()
        logger.debug(f"Completed sync operation {description}")


def _sync_worker_process(
    source_client: "StorageClient",
    source_path: str,
    target_client: "StorageClient",
    target_path: str,
    num_worker_threads: int,
    file_queue: _Queue,
    result_queue: Optional[_Queue],
):
    """
    Worker process that handles file synchronization operations using multiple threads.

    This function is designed to run in a separate process as part of a multiprocessing
    sync operation. It spawns multiple worker threads that consume sync operations from
    the file_queue and perform the actual file transfers (ADD) or deletions (DELETE).
    """

    def _sync_consumer() -> None:
        """Processes files from the queue and copies them."""
        while True:
            op, file_metadata = file_queue.get()
            if op == _SyncOp.STOP:
                break

            source_key = file_metadata.key[len(source_path) :].lstrip("/")
            target_file_path = os.path.join(target_path, source_key)

            if op == _SyncOp.ADD:
                logger.debug(f"sync {file_metadata.key} -> {target_file_path}")
                if file_metadata.content_length < MEMORY_LOAD_LIMIT:
                    file_content = source_client.read(file_metadata.key)
                    target_client.write(target_file_path, file_content)
                else:
                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        temp_filename = temp_file.name

                    try:
                        source_client.download_file(file_metadata.key, temp_filename)
                        target_client.upload_file(target_file_path, temp_filename)
                    finally:
                        os.remove(temp_filename)  # Ensure the temporary file is removed
            elif op == _SyncOp.DELETE:
                logger.debug(f"rm {file_metadata.key}")
                target_client.delete(file_metadata.key)
            else:
                raise ValueError(f"Unknown operation: {op}")

            if result_queue:
                if op == _SyncOp.ADD:
                    # add tuple of (virtual_path, physical_metadata) to result_queue
                    if target_client._metadata_provider:
                        physical_metadata = target_client._metadata_provider.get_object_metadata(
                            target_file_path, include_pending=True
                        )
                    else:
                        physical_metadata = None
                    result_queue.put((op, target_file_path, physical_metadata))
                elif op == _SyncOp.DELETE:
                    result_queue.put((op, target_file_path, None))
                else:
                    raise RuntimeError(f"Unknown operation: {op}")

    # Worker process that spawns threads to handle syncing.
    with ThreadPoolExecutor(max_workers=num_worker_threads) as executor:
        futures = [executor.submit(_sync_consumer) for _ in range(num_worker_threads)]
        for future in futures:
            future.result()  # Ensure all threads complete
