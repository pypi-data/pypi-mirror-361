# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
"""This module contains the objects used in discovering GVR's in the cluster"""

import warnings

from kubernetes_lite.client.resource import DynamicResource
from kubernetes_lite.errors import wrap_kube_error
from kubernetes_lite.wrapper.client import (
    WrappedDynamicClient,
)


class Discoverer:
    """Discoverer is used to discover resource kinds/apiVersions and generate the
    corresponding DynamicResource
    """

    def __init__(self, client: WrappedDynamicClient):
        """Initialize the Discoverer with a provided client

        Args:
            client (WrappedDynamicClient): The client to use for interacting with the cluster
        """
        self._client = client

    @wrap_kube_error
    def get(self, api_version: str, kind: str) -> DynamicResource:
        """Return a DynamicResource for the given api_version and kind. This
        DynamicResource can then be used to interact with the cluster.

        Args:
            api_version (str): The api_version for the resource handle
            kind (str): The kind for the resource handle

        Returns:
            DynamicResource: The DynamicResource handle for the requested type
        """
        kind = kind.lower()
        return DynamicResource(self._client.Resource(api_version, kind))

    def search(self, **kwargs) -> DynamicResource:
        """See get for arguments/returns"""
        warnings.warn(
            "The search method on resources/Discoverer is deprecated. Use the get method instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.get(**kwargs)
