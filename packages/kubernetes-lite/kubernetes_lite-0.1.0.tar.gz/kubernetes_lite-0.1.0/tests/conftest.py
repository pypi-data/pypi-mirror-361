# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
"""This module contains imports required by pytest for fixtures"""

from collections.abc import Generator

from kubernetes_lite.client import DynamicClient, DynamicResource
from kubernetes_lite.envtest.pytest import *  # noqa: F403
from tests.utils import OBJ_API_VERSION, OBJ_KIND

import pytest


@pytest.fixture
def resource_namespace(
    session_client_namespace: tuple[DynamicClient, str],
) -> Generator[tuple[DynamicResource, str], None, None]:
    """Helper fixture to return a deployment resource compatible with generate_test_object and the
    namespace to use for tests

    Args:
        session_client_namespace (tuple[DynamicClient, str]): The client and namespace to use

    Yields:
        Generator[tuple[DynamicResource, str], None, None]: Tuple of the dynamic resource and namespace
    """
    client, namespace = session_client_namespace
    yield client.resource(OBJ_API_VERSION, OBJ_KIND), namespace
