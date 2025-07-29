# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
"""This module contains helper pytest fixtures to make using EnvTest easier
in testing environments
"""

import random
import string
from collections.abc import Generator
from contextlib import contextmanager

from kubernetes_lite.client import DynamicClient
from kubernetes_lite.envtest import EnvTest

import pytest


@contextmanager
def yield_kubernetes_env() -> Generator[EnvTest, None, None]:
    """Context manager to yield a running EnvTest instance and handle
    stopping it after the fact

    Yields:
        Generator[EnvTest, None, None]: The running EnvTest instance
    """
    env = EnvTest()
    env.start()
    yield env
    env.stop()


@pytest.fixture()
def kubernetes_env() -> Generator[EnvTest, None, None]:
    """Pytest fixture for a running EnvTest instance

    Yields:
        Generator[EnvTest, None, None]: The running EnvTest instance
    """
    with yield_kubernetes_env() as env:
        yield env


@pytest.fixture(scope="session")
def session_kubernetes_env() -> Generator[EnvTest, None, None]:
    """Session scoped version of the above fixture. Returns a running
    EnvTest instance

    Yields:
        Generator[EnvTest, None, None]: The running EnvTest instance
    """
    with yield_kubernetes_env() as env:
        yield env


@pytest.fixture()
def dynamic_client(kubernetes_env: EnvTest) -> Generator[DynamicClient, None, None]:
    """A pytest fixture for a dynamic client connected to an EnvTest instance

    Args:
        kubernetes_env (EnvTest): a running EnvTest instance

    Yields:
        Generator[DynamicClient, None, None]: The dynamic client that can be used to interact
            with an EnvTest instance
    """
    yield kubernetes_env.client()


@pytest.fixture(scope="session")
def session_client(session_kubernetes_env: EnvTest) -> Generator[DynamicClient, None, None]:
    """A session scoped pytest fixture for a dynamic client connected to an EnvTest
    instance

    Args:
        session_kubernetes_env (EnvTest): a running EnvTest instance

    Yields:
        Generator[DynamicClient, None, None]: The dynamic client that can be used to interact
            with an EnvTest instance
    """
    yield session_kubernetes_env.client()


def create_random_namespace(client: DynamicClient) -> str:
    """Helper function to create a randomly named namespace from the given client

    Args:
        client (DynamicClient): The client to create namespaces with

    Returns:
        str: The randomly generated namespace name
    """
    # Randomize the namespace string
    namespace = "".join(random.choice(string.ascii_lowercase) for i in range(10))
    client.resources.get(api_version="v1", kind="Namespace").apply(
        {"metadata": {"name": namespace}, "kind": "Namespace", "apiVersion": "v1"}, fieldManager="default"
    )
    return namespace


@pytest.fixture()
def dynamic_client_namespace(dynamic_client: DynamicClient) -> Generator[tuple[DynamicClient, str], None, None]:
    """Pytest fixture to return a Dynamic Client with a fresh namespace you can apply resources to

    Args:
        dynamic_client (DynamicClient): Dynamic Client fixture

    Yields:
        Generator[tuple[DynamicClient, str], None, None]: tuple with the client and namespace name
    """
    yield dynamic_client, create_random_namespace(dynamic_client)


@pytest.fixture()
def session_client_namespace(session_client: DynamicClient) -> Generator[tuple[DynamicClient, str], None, None]:
    """Pytest session scoped fixture to return a Dynamic Client with a fresh namespace you can apply resources to

    Args:
        session_client (DynamicClient): Dynamic Client fixture

    Yields:
        Generator[tuple[DynamicClient, str], None, None]: tuple with the client and namespace name
    """
    yield session_client, create_random_namespace(session_client)
