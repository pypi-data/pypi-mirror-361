# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
"""This module contains tests for the top-level client operations"""

from datetime import datetime, timedelta

from kubernetes_lite.client import DynamicClient
from kubernetes_lite.envtest import EnvTest
from kubernetes_lite.envtest.pytest import create_random_namespace
from tests.utils import (
    OBJ_API_VERSION,
    OBJ_KIND,
    generate_test_object,
)


def test_rate_limiting(session_kubernetes_env: EnvTest):
    """Test that we can enable ratelimiting"""
    client = DynamicClient(session_kubernetes_env.config(), qps=1, burst=1)
    deployment_res = client.resource(OBJ_API_VERSION, OBJ_KIND)
    obj = generate_test_object(create_random_namespace(client))

    apply_count = 0
    stop_time = datetime.now() + timedelta(seconds=3)
    while True:
        if datetime.now() >= stop_time:
            break
        deployment_res.apply(obj, field_manager="test")
        apply_count += 1

    # Assert that in 3 seconds with a limit of 1 qps we only do a couple of applys
    assert apply_count >= 2
    assert apply_count < 5


def test_no_rate_limiting(session_kubernetes_env: EnvTest):
    """Test that the client has no-ratelimiting by default"""
    client = DynamicClient(session_kubernetes_env.config())
    deployment_res = client.resource(OBJ_API_VERSION, OBJ_KIND)
    obj = generate_test_object(create_random_namespace(client))

    apply_count = 0
    stop_time = datetime.now() + timedelta(seconds=3)
    while True:
        if datetime.now() >= stop_time:
            break
        deployment_res.apply(obj, field_manager="test")
        apply_count += 1

    # Assert that in 3 seconds with a limit of 1 qps we only do a couple of applys
    assert apply_count > 5
