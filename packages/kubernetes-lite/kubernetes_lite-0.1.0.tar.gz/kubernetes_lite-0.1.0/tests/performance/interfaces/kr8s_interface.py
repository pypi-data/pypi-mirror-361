# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
"""This module contains the implementation of ClientInterface using kr8s"""

from typing import Any

from performance.interfaces.base import ClientInterface


class Kr8sInterface(ClientInterface):
    """Kr8sInterface is a client interface implementation built using the k8rs
    library provided at https://github.com/kr8s-org/kr8s
    """

    @staticmethod
    def import_modules() -> list[str]:
        """Import the kr8s module"""
        import kr8s  # noqa: F401, PLC0415

        return ["kr8s"]

    @staticmethod
    def create_client() -> Any:
        """The kr8s module acts as the client since its under the cover"""
        import kr8s  # noqa: PLC0415

        return kr8s

    @staticmethod
    def create_resource_client(client: Any, kind: str, api_version: str) -> Any:
        """Create resource client constructs a new kr8s class for the provided kind/apiVersion"""
        from kr8s.objects import new_class  # noqa: PLC0415

        namespaced = True
        if kind == "CustomResourceDefinition":
            namespaced = False
        return new_class(
            kind=kind,
            version=api_version,
            namespaced=namespaced,
        )

    @staticmethod
    def create(resource_client: Any, data: Any) -> Any:
        """Create an object using kr8s's create api"""
        res_obj = resource_client(resource=data)
        res_obj.create()
        res_obj.refresh()
        return res_obj.to_dict()

    @staticmethod
    def apply(resource_client: Any, data: Any) -> Any:
        """Apply an object using either patch/create for kr8s"""
        res_obj = resource_client(resource=data)
        if res_obj.exists():
            res_obj.patch(data)
        else:
            res_obj.create()
        res_obj.refresh()
        return res_obj.to_dict()

    @staticmethod
    def list(resource_client: Any, namespace: str) -> Any:
        """List all objects using the kr8s iterator"""
        return [res.to_dict() for res in resource_client.list(namespace=namespace)]

    @staticmethod
    def get(resource_client: Any, name: str, namespace: str) -> Any:
        """Get the object from the cluster using kr8s's get interface"""
        return resource_client.get(name=name, namespace=namespace).to_dict()

    @staticmethod
    def delete(resource_client: Any, name: str, namespace: str):
        """Delete the object from the cluster after refreshing it"""
        res = resource_client(name, namespace)
        res.delete()
