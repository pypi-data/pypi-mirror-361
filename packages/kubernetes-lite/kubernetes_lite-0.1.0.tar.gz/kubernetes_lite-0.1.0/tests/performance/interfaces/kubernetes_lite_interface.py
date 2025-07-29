# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
"""This module contains the implementation of ClientInterface using the local kubernetes-lite
package
"""

import os
from pathlib import Path
from typing import Any

from performance.interfaces.base import ClientInterface


class KubernetesLiteInterface(ClientInterface):
    """KubernetesLiteInterface is the implementation of ClientInterface using the local kubernetes-lite
    library
    """

    @staticmethod
    def import_modules() -> list[str]:
        """Import the kubernetes_lite dynamic client since that's all thats required"""
        from kubernetes_lite.client import DynamicClient  # noqa: F401, PLC0415

        return ["kubernetes_lite"]

    @staticmethod
    def create_client() -> Any:
        """Create the client using the local kube_config"""
        from kubernetes_lite.client import DynamicClient  # noqa: PLC0415

        config = None
        # Manually read in KUBECONFIG. This is required in testing because the golang runtime copies the environment
        # before we update the os.environ variable
        if os.environ.get("KUBECONFIG"):
            config = Path(os.environ.get("KUBECONFIG")).read_bytes()
        return DynamicClient(config=config)

    @staticmethod
    def create_resource_client(client: Any, kind: str, api_version: str) -> Any:
        """Create the dynamic resource client with the provided kind/apiVerison"""
        return client.resource(api_version, kind)

    @staticmethod
    def create(resource_client: Any, data: Any) -> Any:
        """Create an object in the cluster"""
        return resource_client.create(data)

    @staticmethod
    def apply(resource_client: Any, data: Any) -> Any:
        """Apply an object in the cluster"""
        return resource_client.apply(data, field_manager="python")

    @staticmethod
    def list(resource_client: Any, namespace: str) -> Any:
        """List all objects in the namespace"""
        return resource_client.list(namespace)

    @staticmethod
    def get(resource_client: Any, name: str, namespace: str) -> Any:
        """Get an single object in the cluster"""
        return resource_client.get(name=name, namespace=namespace)

    @staticmethod
    def delete(resource_client: Any, name: str, namespace: str):
        """Delete a single object in the cluster"""
        resource_client.delete(name=name, namespace=namespace)
