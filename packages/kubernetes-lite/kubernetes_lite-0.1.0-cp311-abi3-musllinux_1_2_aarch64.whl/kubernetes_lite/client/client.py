# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
"""This module contains the implementation of the top level dynamic client"""

import datetime
from functools import cached_property
from io import BytesIO

from kubernetes_lite.client.discovery import Discoverer
from kubernetes_lite.client.resource import DynamicResource
from kubernetes_lite.serialization import serialize_to_go
from kubernetes_lite.wrapper.client import (
    NewWrappedDynamicClient,
    NewWrappedDynamicClientWithConfig,
)


class DynamicClient:
    """DynamicClient is the top level client and generic controls settings like authentication,
    rate limiting, and timeouts. Use the .resource method to create a DynamicResource which
    can be used to interact with the cluster.
    """

    def __init__(
        self,
        config: bytes | BytesIO | None = None,
        qps: float = -1,
        burst: int = 100,
        timeout: datetime.timedelta | str = "",
        **kwargs,
    ):
        """Initialize the dynamic client with optional overrides

        Args:
            config (bytes | BytesIO | None, optional): The raw kube_config data to initialize the client with. Defaults
                to controller-runtime's GetConfig.
                See https://pkg.go.dev/sigs.k8s.io/controller-runtime/pkg/client/config#GetConfig for more information.
            qps (float, optional): QPS to set for the client. See https://pkg.go.dev/k8s.io/client-go/rest#Config
                for more information. Defaults to -1 which means rate-limiting is disabled.
            burst (int, optional): How many requests can the client burst to. See https://pkg.go.dev/k8s.io/client-go/rest#Config
                for more information. Defaults to 100.
            timeout (datetime.timedelta | str, optional): Timeout value for the client. If a string is provided check
                https://pkg.go.dev/time#ParseDuration for parsing information. Defaults to "" or no timeout.
            **kwargs: Unused kwargs for backwards compatibility with kubernetes library
        """
        # Parse timeout into a string
        if isinstance(timeout, datetime.timedelta):
            timeout = f"{timeout.total_seconds()}s"

        # Setup the common client arguments
        client_args = [qps, burst, timeout]
        if config:
            self.client = NewWrappedDynamicClientWithConfig(serialize_to_go(config), *client_args)
        else:
            self.client = NewWrappedDynamicClient(*client_args)

    @cached_property
    def resources(self) -> Discoverer:
        """Return the client's Discover object. It's preferred to use the resource()
        function instead of accessing this directly

        Returns:
            Discoverer: The discover used in created DynamicResources
        """
        return Discoverer(self.client)

    def resource(self, api_version: str, kind: str) -> DynamicResource:
        """Return a DynamicResource for the given api_version and kind. This
        DynamicResource can then be used to interact with the cluster.

        Args:
            api_version (str): The api_version for the resource handle
            kind (str): The kind for the resource handle

        Returns:
            DynamicResource: The DynamicResource handle for the requested type
        """
        return self.resources.get(api_version, kind)
