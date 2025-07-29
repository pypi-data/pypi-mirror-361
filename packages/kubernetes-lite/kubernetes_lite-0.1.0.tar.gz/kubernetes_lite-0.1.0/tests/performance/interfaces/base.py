# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
"""This module contains the abstract base class for all client interfaces"""

import abc
from typing import Any


class ClientInterface(abc.ABC):
    """ClientInterface is the general base class for clients. It contains the description and signature
    for all of the expected methods
    """

    @staticmethod
    @abc.abstractmethod
    def import_modules() -> list[str]:
        """Just import the modules required to use the client with no other tasks.

        Returns:
            list[str]: List of modules that were imported so they can be unimported before being reran
        """

    @staticmethod
    @abc.abstractmethod
    def create_client() -> Any:
        """Create a client object assuming that the KUBE_CONFIG variable is properly set

        Returns:
            Any: Functioning client which can be passed into create_resource_client
        """

    @staticmethod
    @abc.abstractmethod
    def create_resource_client(client: Any, kind: str, api_version: str) -> Any:
        """Create a resource specific client

        Args:
            client (Any): The client to use for connections
            kind (str): The  kind of the resource client to create
            api_version (str): The apiVersion of the resource client to create

        Returns:
            Any: The constructed resource client
        """

    @staticmethod
    @abc.abstractmethod
    def create(resource_client: Any, data: Any) -> Any:
        """Create an object with a given resource_client

        Args:
            resource_client (Any): The resource_client to use for operations
            data (Any): The data to create

        Returns:
            Any: The current object's cluster state
        """

    @staticmethod
    @abc.abstractmethod
    def apply(resource_client: Any, data: Any) -> Any:
        """Apply an object to the cluster with a given resource_client

        Args:
            resource_client (Any): The resource_client to use for operations
            data (Any): The data to create

        Returns:
            Any: The current object's cluster state
        """

    @staticmethod
    @abc.abstractmethod
    def list(resource_client: Any, namespace: str | None) -> Any:
        """List all objects in the cluster for a given namespace/resource_client

        Args:
            resource_client (Any): The resource_client to use for operations
            namespace (str): The namespace to list resources in

        Returns:
            Any: List of current resources
        """

    @staticmethod
    @abc.abstractmethod
    def get(resource_client: Any, name: str, namespace: str | None) -> Any:
        """Get an object from the cluster

        Args:
            resource_client (Any): THe resource_client to use for operations
            name (str): The name of the object to fetch
            namespace (str | None): The namespace the object lives in

        Returns:
            Any: The object from the cluster as a dictionary
        """

    @staticmethod
    @abc.abstractmethod
    def delete(resource_client: Any, name: str, namespace: str):
        """Delete an object from the cluster

        Args:
            resource_client (Any): THe resource_client to use for operations
            name (str): The name of the object to delete
            namespace (str | None): The namespace the object lives in
        """
