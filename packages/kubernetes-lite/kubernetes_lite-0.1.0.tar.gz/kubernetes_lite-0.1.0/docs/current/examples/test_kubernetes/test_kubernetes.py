# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
"""This script is an example of how to use envtest with the standard
kubernetes package
"""

from kubernetes_lite.envtest import EnvTest
from kubernetes_lite.envtest.pytest import session_kubernetes_env  # noqa: F401

from kubernetes import client, config
from kubernetes.dynamic import DynamicClient


def test_kubernetes_core_api(session_kubernetes_env: EnvTest):  # noqa: F811
    """Test that kubernetes core api works with envtest"""
    config.load_config(config_file=session_kubernetes_env.config())

    v1 = client.CoreV1Api()
    print("Listing pods with their IPs:")
    ret = v1.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        print(f"{i.status.pod_ip}\t{i.metadata.namespace}\t{i.metadata.name}")

    assert ret


def test_kubernetes_dynamic(session_kubernetes_env: EnvTest):  # noqa: F811
    """Test that kubernetes dynamic client works with envtest"""
    kube_config = config.new_client_from_config(config_file=session_kubernetes_env.config())
    kube_client = DynamicClient(kube_config)
    assert kube_client

    deploy_res = kube_client.resources.get(kind="Deployment", api_version="apps/v1")
    ret = deploy_res.get(name=None, namespace=None)
    for i in ret.items:
        print(f"{i.status.pod_ip}\t{i.metadata.namespace}\t{i.metadata.name}")
    assert ret
