# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
"""This module tests that envtest server works with non kubernetes_lite clients"""

from kubernetes_lite.envtest import EnvTest
from kubernetes_lite.envtest.pytest import create_random_namespace
from tests.utils import (  # noqa: F401
    DEFAULT_OBJ_NAME,
    OBJ_API_VERSION,
    OBJ_KIND,
    check_object_status,
    generate_test_object,
    validate_result,
)

import kubernetes
from kubernetes.dynamic import DynamicClient


def test_envtest(kubernetes_env: EnvTest):
    """Test that envtest can work with nonkubernetes_lite libraries"""
    kube_config = kubernetes.config.new_client_from_config(config_file=kubernetes_env.config())
    kube_client = DynamicClient(kube_config)
    assert kube_client

    namespace = create_random_namespace(kubernetes_env.client())

    deploy_res = kube_client.resources.get(kind=OBJ_KIND, api_version=OBJ_API_VERSION)

    obj = generate_test_object(namespace)
    deploy_res.server_side_apply(
        obj,
        name=DEFAULT_OBJ_NAME,
        namespace=namespace,
        field_manager="tet",
    )
    check_object_status(kubernetes_env.client().resource(OBJ_API_VERSION, OBJ_KIND), expected_obj=obj)
