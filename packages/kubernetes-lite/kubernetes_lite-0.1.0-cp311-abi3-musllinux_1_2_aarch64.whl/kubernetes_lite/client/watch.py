# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
"""This module contains the interface for iterating over events from the
cluster
"""

from kubernetes_lite.serialization import deserialize_result
from kubernetes_lite.wrapper.client import WrappedWatchInterface


class Watch:
    """Watch is an iterator that yields events streamed from
    the cluster
    """

    interface: WrappedWatchInterface | None = None

    def __init__(self, interface: WrappedWatchInterface | None = None):
        """Initialize the Watch instance with a given wrapped interface

        Args:
            interface (WrappedWatchInterface | None, optional): The interface to yield events from. Defaults to None.
        """
        self.interface = interface

    def stop(self):
        """Stop streaming events from the cluster"""
        if not self.interface:
            raise RuntimeError("Interface must be set before calling stop/next")

        self.interface.Stop()

    def __iter__(self) -> "Watch":
        """Complete implementation of a python iterator

        Returns:
            Watch: Itself to iterate
        """
        return self

    def __next__(self) -> dict:
        """Return the next event from the cluster. These events are dictionaries in the
        format of json encoded apimachinery Events. You can find more information here:
        https://pkg.go.dev/k8s.io/apimachinery/pkg/watch#Event

        Returns:
            dict: The event data
        """
        if not self.interface:
            raise RuntimeError("Interface must be set before calling stop/next")

        # Try to get an event from the underlying interface
        try:
            event_data = self.interface.Next()
        except RuntimeError as exc:
            if "stop iteration" in str(exc):
                raise StopIteration from None

        # Return the deserialized result
        return deserialize_result(bytes(event_data))
