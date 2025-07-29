# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
"""This module contains the main implementation of the performance command
which includes formatting the output and running the test harness
"""

import csv
import os
import time
from enum import StrEnum
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from performance.interfaces.kr8s_interface import Kr8sInterface
from performance.interfaces.kubernetes_interface import KubernetesInterface
from performance.interfaces.kubernetes_lite_interface import KubernetesLiteInterface
from performance.interfaces.run import TimingInfo, test_interface
from performance.memory import BackgroundMemoryTracker
from performance.utils import calculate_timing_info


class ClientOptions(StrEnum):
    """Enum of the currently supported clients that we can measure"""

    KUBERNETES = "kubernetes"
    KUBERNETES_LITE = "kubernetes_lite"
    KR8S = "kr8s"


# This dictionary maps the ClientOption from the CLI to the corresponding interface
CLIENT_OPTION_INTERFACE_MAP = {
    ClientOptions.KUBERNETES_LITE: KubernetesLiteInterface,
    ClientOptions.KUBERNETES: KubernetesInterface,
    ClientOptions.KR8S: Kr8sInterface,
}


def run_test(
    output: Path,
    clients: list[ClientOptions] | None = None,
    repetitions: int = 5,
    namespace: str = "default",
    memory_poll_time: float = 0.1,
):
    """Run the performance test for a given list of clients. This is the functional entrypoint
    for this module

    Args:
        output (Path): Output file to write results to
        clients (list[ClientOptions] | None, optional): List of clients to test. Defaults to None which
            means test all clients
        repetitions (int, optional): How many times the test should be ran. Defaults to 5.
        namespace (str, optional): Namespace to run test in. Defaults to "default" and should
            be unique if multiple performance tests are running at the same time
        memory_poll_time (float, optional): How often to poll the system memory.
            Defaults to 0.1.
    """
    # If no client was provided then test them all
    if not clients:
        clients = [client for client in ClientOptions]

    # Before doing anything start the memory tracker so we can track the initial
    # kubernetes_lite usage
    memory_tracker = BackgroundMemoryTracker(poll_time=memory_poll_time)
    memory_tracker.start()

    # Import env test and sleep to ensure the tracker captured some data
    time.sleep(1)
    from kubernetes_lite.envtest import EnvTest  # noqa: PLC0415

    time.sleep(1)

    # Get kubernetes_lite max mem
    kubernetes_lite_mem_usage = memory_tracker.get_max_mem()

    # Setup EnvTest server
    env_test = EnvTest()
    env_test.start()
    config = env_test.config()

    # Attempt to test the client interfaces
    try:
        # Write the envtest kube config to a temporary directory
        timing_outputs, max_mem = test_interfaces(clients, config, memory_tracker, repetitions, namespace)
    # Even if there was an error shutdown the tracker/envtest
    finally:
        memory_tracker.shutdown()
        memory_tracker.join()
        env_test.stop()

    # Update the max mem for kubernetes_lite to the value we gathered after importing EnvTest. EnvTest overall increases
    # reproducibility but it requires measuring max_mem separately
    if ClientOptions.KUBERNETES_LITE in max_mem:
        max_mem[ClientOptions.KUBERNETES_LITE] = kubernetes_lite_mem_usage
    if len(max_mem) == 1 and ClientOptions.KUBERNETES_LITE not in max_mem:
        max_mem_key = next(iter(max_mem.keys()))
        max_mem[max_mem_key] -= kubernetes_lite_mem_usage

    # After running the tests generate the CSV output
    generate_result_csv(output, timing_outputs, max_mem)


def test_interfaces(
    clients: list[ClientOptions],
    config: BytesIO,
    memory_tracker: BackgroundMemoryTracker,
    repetitions: int,
    namespace: str,
) -> tuple[dict[ClientOptions, TimingInfo], dict[ClientOptions, float]]:
    """Test and time the various selected interfaces. This is split out to simplify the
    run_test function

    Args:
        clients (list[ClientOptions]): Clients to test
        config (BytesIO): KubeConfig to use during testing
        memory_tracker (BackgroundMemoryTracker): The memory tracker running in the background
        repetitions (int): How many repetitions to perform
        namespace (str): The namespace to run the test against

    Returns:
        tuple[dict[ClientOptions, TimingInfo], dict[ClientOptions, float]]: tuple of timing information and max_memory
    """
    # Setup a tempdir with the kube config. THis is required for some of the simpler clients
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config_path = temp_path / "config"
        config_path.write_bytes(config.getvalue())
        os.environ["KUBECONFIG"] = str(config_path)

        # For each client run the tests
        timing_outputs: dict[ClientOptions, TimingInfo] = {}
        max_mem = {}
        for client in clients:
            # Fetch and construct the interface
            interface_type = CLIENT_OPTION_INTERFACE_MAP.get(client)
            interface = interface_type()

            # Reset the memory tracker before running the test
            memory_tracker.reset()
            timing_outputs[client] = test_interface(interface, repetitions, namespace)

            # Get max mem after the test
            max_mem[client] = memory_tracker.get_max_mem()

    return timing_outputs, max_mem


def generate_result_csv(output: Path, timing_outputs: dict[ClientOptions, TimingInfo], max_mem: dict[str, float]):
    """Generate a CSV document from the provided timing and memory outputs

    Args:
        output (Path): The path to write the CSV to
        timing_outputs (dict[ClientOptions, TimingInfo]): Dictionary of client types and their timing information
        max_mem (dict[str, float]): Each client's max RSS memory usage
    """
    output_csv_rows = [
        [
            "TYPE",
            "FILE",
            "METHOD",
            "AVERAGE TIME (ms)",
            "STD DIV (ms)",
        ]
    ]
    for output_type, timing_info in timing_outputs.items():
        output_csv_rows.extend(
            [
                [output_type.value, "N/A", "client_create", *calculate_timing_info(timing_info.client_create_times)],
                [
                    output_type.value,
                    "N/A",
                    "resource_client_create_times",
                    *calculate_timing_info(timing_info.resource_client_create_times),
                ],
                [output_type.value, "N/A", "import_times", *calculate_timing_info(timing_info.import_times)],
            ]
        )

        for file_name, resource_timing_info in timing_info.resource_timing_info.items():
            output_csv_rows.extend(
                [
                    [output_type.value, file_name, "apply", *calculate_timing_info(resource_timing_info.apply_times)],
                    [output_type.value, file_name, "delete", *calculate_timing_info(resource_timing_info.delete_times)],
                    [output_type.value, file_name, "create", *calculate_timing_info(resource_timing_info.create_times)],
                    [output_type.value, file_name, "list", *calculate_timing_info(resource_timing_info.list_times)],
                    [output_type.value, file_name, "get", *calculate_timing_info(resource_timing_info.get_times)],
                ]
            )

    # Add two blank lines before memory summary
    output_csv_rows.append([])
    output_csv_rows.append([])

    output_csv_rows.append(
        [
            "TYPE",
            "MAX_RSS_INCREASE",
        ]
    )
    for output_type, max_rss in max_mem.items():
        output_row = [output_type.value, max_rss]
        output_csv_rows.append(output_row)

    with output.open("w") as output_file:
        writer = csv.writer(output_file)
        writer.writerows(output_csv_rows)
