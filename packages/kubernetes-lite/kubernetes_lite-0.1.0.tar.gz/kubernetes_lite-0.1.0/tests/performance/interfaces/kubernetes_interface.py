# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
"""This module contains the implementation of ClientInterface using official kubernetes
client
"""

from typing import Any

from performance.interfaces.base import ClientInterface

import urllib3

# Disable warning for rest to normalize ssl/non-ssl speeds
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class KubernetesInterface(ClientInterface):
    """KubernetesInterface is a client interface implementation built using the official kubernetes
    library provided at https://github.com/kubernetes-client/python/tree/master
    """

    @staticmethod
    def import_modules() -> list[str]:
        """Import the kubernetes config and dynamic objects"""
        from kubernetes.config import new_client_from_config  # noqa: F401, PLC0415
        from kubernetes.dynamic import DynamicClient  # noqa: F401, PLC0415

        return ["kubernetes"]

    @staticmethod
    def create_client() -> Any:
        """Create the client from a local config"""
        from kubernetes.config import new_client_from_config  # noqa: PLC0415
        from kubernetes.dynamic import DynamicClient  # noqa: PLC0415

        return DynamicClient(new_client_from_config())

    @staticmethod
    def create_resource_client(client: Any, kind: str, api_version: str) -> Any:
        """Create resource client gets the client for a specific resource using the discoverer"""
        return client.resources.get(kind=kind, api_version=api_version)

    @staticmethod
    def create(resource_client: Any, data: Any) -> Any:
        """Create the resource using kubernete's create api"""
        return resource_client.create(data).to_dict()

    @staticmethod
    def apply(resource_client: Any, data: Any) -> Any:
        """Apply the resource using the kubernetes server_side_apply API"""
        return resource_client.server_side_apply(data, field_manager="python").to_dict()

    @staticmethod
    def list(resource_client: Any, namespace: str) -> Any:
        """List all objects in the namespace using kubernetes's generic get(name=None) API"""
        return resource_client.get(name=None, namespace=namespace).to_dict()

    @staticmethod
    def get(resource_client: Any, name: str, namespace: str) -> Any:
        """Get an object from the cluster using the kubernetes resource client and provided name/namespace"""
        return resource_client.get(name=name, namespace=namespace).to_dict()

    @staticmethod
    def delete(resource_client: Any, name: str, namespace: str):
        """Delete an object from the cluster using the kubernetes resource client"""
        return resource_client.delete(name=name, namespace=namespace)
