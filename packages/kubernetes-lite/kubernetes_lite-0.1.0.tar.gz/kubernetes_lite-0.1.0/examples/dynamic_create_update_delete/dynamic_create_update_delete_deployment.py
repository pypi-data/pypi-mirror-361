# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
# Assisted by watsonx Code Assistant
"""This example program demonstrates the fundamental operations for
managing on Deployment resources, such as Create, List, Update and Delete
using kubernetes_lites dynamic package.
"""

import argparse
import time
from collections.abc import Callable
from pathlib import Path

from kubernetes_lite.client import DynamicClient
from kubernetes_lite.errors import ConflictError


def exponential_retry(
    func: Callable, caught_exception: Exception, max_attempts: int, initial_delay: float, max_delay: float
):
    """Helper function to exponentially retry a function call for certain exceptions. This
    isn't explicitly needed for the example but it aligns with the client-go example

    Args:
        func (Callable): The function to call/retry
        caught_exception (Exception): The exception to catch for retries
        max_attempts (int): How many times to retry
        initial_delay (float): What the initial exponential delay is
        max_delay (float): Maximum time delay between retries
    """
    attempts = 0
    delay = initial_delay
    last_exception = None
    while attempts < max_attempts:
        try:
            func()
            return
        except caught_exception as exc:
            last_exception = exc

        time.sleep(delay)
        delay = min(delay * 2, max_delay)
        attempts += 1
    raise last_exception


def main(kube_config: Path | None = None, namespace: str | None = "default"):
    """_summary_

    Args:
        kube_config (Path | None, optional): _description_. Defaults to None.
        namespace (str | None, optional): _description_. Defaults to "default".
    """
    client = DynamicClient(kube_config.read_bytes()) if kube_config else DynamicClient()

    deploy_resource = client.resource("apps/v1", "deployments")

    deployment_obj = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": "demo-deployment",
        },
        "spec": {
            "replicas": 2,
            "selector": {
                "matchLabels": {
                    "app": "demo",
                },
            },
            "template": {
                "metadata": {
                    "labels": {
                        "app": "demo",
                    },
                },
                "spec": {
                    "containers": [
                        {
                            "name": "web",
                            "image": "nginx:1.12",
                            "ports": [
                                {
                                    "name": "http",
                                    "protocol": "TCP",
                                    "containerPort": 80,
                                },
                            ],
                        }
                    ],
                },
            },
        },
    }

    print("Creating deployment...")
    result = deploy_resource.create(deployment_obj, namespace=namespace)
    print(f'Created deployment "{result["metadata"]["name"]}"')

    input("-> Press Return key to continue.")

    print("Updating deployment...")

    def update_deployment():
        current_deploy_obj = deploy_resource.get(name="demo-deployment", namespace=namespace)
        current_deploy_obj["spec"]["replicas"] = 1

        current_deploy_obj["spec"]["template"]["spec"]["containers"][0]["image"] = "nginx:1.13"

        deploy_resource.update(current_deploy_obj)

    exponential_retry(update_deployment, caught_exception=ConflictError, max_attempts=5, initial_delay=1, max_delay=10)
    print("Updated deployment...")
    input("-> Press Return key to continue.")

    print(f'Listing deployments in namespace "{namespace}":')
    resources = deploy_resource.list(namespace=namespace)
    for resource in resources["items"]:
        name = resource["metadata"]["name"]
        replicas = resource["spec"]["replicas"]
        print(f" * {name} ({replicas} replicas)")

    input("-> Press Return key to continue.")

    print("Deleting deployment...")
    deploy_resource.delete(
        name="demo-deployment",
        namespace=namespace,
        propagation_policy="Foreground",
    )
    print("Deleted deployment.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-kubeconfig", help="Path to the kubeconfig file")
    parser.add_argument("-namespace", help="Namespace to use", default="default")
    args = parser.parse_args()

    kubeconfig = None
    if args.kubeconfig:
        kubeconfig = Path(args.kubeconfig)
        if not kubeconfig.is_file():
            raise argparse.ArgumentTypeError(f"kubeconfig: {kubeconfig} either does not exist or is not a file")

    main(kubeconfig, args.namespace)
