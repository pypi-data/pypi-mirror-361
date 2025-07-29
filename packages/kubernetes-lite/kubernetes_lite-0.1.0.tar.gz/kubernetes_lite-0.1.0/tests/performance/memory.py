# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
"""This module contains the helper functions/threads for tracking memory
usage
"""

import ctypes
import gc
import sys
import time
from threading import Event, Lock, Thread

import psutil


def get_current_memory_usage() -> int:
    """Get the current RSS memory usage for this process

    Returns:
        int: The current memory usage in bytes
    """
    current_process = psutil.Process()
    gc.collect()
    return current_process.memory_info().rss


class BackgroundMemoryTracker(Thread):
    """BackgroundMemoryTracker is a background thread that constantly records the
    maximum memory used since starting/being reset
    """

    def __init__(self, *args, poll_time: float = 0.1, **kwargs):
        """Initialize the BackgroundMemoryTracker and all required synchronization primitives

        Args:
            poll_time (float, optional): How often to check for max memory. Defaults to 0.1.
            *args: Extra args passed to Thread __init__
            **kwargs: Extra kwargs pass to Thread __init__
        """
        super().__init__(*args, **kwargs, daemon=True)

        self.poll_time = poll_time

        self.shutdown_event = Event()
        self.memory_lock = Lock()
        self.max_mem = get_current_memory_usage()

    def run(self):
        """Constantly poll the system for max memory until the shutdown event is set"""
        while True:
            if self.shutdown_event.is_set():
                return

            with self.memory_lock:
                current_usage = get_current_memory_usage()
                self.max_mem = max(current_usage, self.max_mem)
            time.sleep(self.poll_time)

    def get_max_mem(self) -> int:
        """Get the max memory observed by this thread

        Returns:
            int: max memory since last reset/start
        """
        return self.max_mem

    def reset(self):
        """Reset the memory tracker back to the current usage"""
        with self.memory_lock:
            gc.collect()
            if sys.platform.startswith("linux"):
                libc = ctypes.CDLL("libc.so.6")
                libc.malloc_trim(0)

            self.max_mem = get_current_memory_usage()

    def shutdown(self):
        """Shutdown the background thread by setting an event flag"""
        self.shutdown_event.set()
