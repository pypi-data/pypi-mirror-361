# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
"""This module contains the helper functions used to test an interface"""

import json
import time
from contextlib import suppress
from dataclasses import dataclass, field
from pathlib import Path

from performance.interfaces import ClientInterface
from performance.utils import time_for_list, unimport_module

ROOT_FOLDER_PATH = Path(__file__).parent.parent


@dataclass
class ResourceTimingInfo:
    """ResourceTimingInfo contains the time information for functions that change based
    on the size of the input

    Attributes:
        create_times (list[float]): List of times required to create an object
        delete_times (list[float]): List of times required to delete an object
        apply_times (list[float]): List of times required to apply an object
        list_times (list[float]): List of times required to list objects
        get_times (list[float]): List of times required to get an object
    """

    create_times: list[float] = field(default_factory=list)
    delete_times: list[float] = field(default_factory=list)
    apply_times: list[float] = field(default_factory=list)
    list_times: list[float] = field(default_factory=list)
    get_times: list[float] = field(default_factory=list)


@dataclass
class TimingInfo:
    """TimingInfo contains the time information for constant fields like
    import/client_creation

    Attributes:
        import_times (list[float]): List of times for importing the module
        client_create_times (list[float]): List of times for creating the client
        resource_client_create_times (list[float]): List of times for creating the resource client
        resource_timing_info (dict[str, ResourceTimingInfo]): Mapping of timing results to the resource name
    """

    import_times: list[float] = field(default_factory=list)
    client_create_times: list[float] = field(default_factory=list)
    resource_client_create_times: list[float] = field(default_factory=list)
    resource_timing_info: dict[str, ResourceTimingInfo] = field(default_factory=dict)


def test_interface(client_interface: ClientInterface, repetitions: int = 5, namespace: str = "default") -> TimingInfo:
    """Test Interface is a helper function used to test an individual interface across multiple
    objects

    Args:
        client_interface (ClientInterface): The client interface being tested
        repetitions (int, optional): How many repetitions to do. Defaults to 5.
        namespace (str, optional): Namespace to run tests in. Defaults to "default".

    Returns:
        TimingInfo: The timing information for this client
    """
    timing_info = TimingInfo()

    print(f"{client_interface.__class__.__name__}: Testing import")

    # Time how long import takes
    modules_to_unimport = []
    for _ in range(repetitions):
        with time_for_list(timing_info.import_times):
            modules_to_unimport = client_interface.import_modules()
        for module in modules_to_unimport:
            unimport_module(module)

    # Redo the import outside of timing so the rest can use it
    client_interface.import_modules()

    print(f"{client_interface.__class__.__name__}: Testing client creation")

    # Time how long client creation takes
    for _ in range(repetitions):
        with time_for_list(timing_info.client_create_times):
            client = client_interface.create_client()

    # Setup the data and thing to test
    test_crd = json.loads((ROOT_FOLDER_PATH / Path("test_crd.json")).read_bytes())
    test_crd_kind = test_crd.get("kind")
    test_crd_api_version = test_crd.get("apiVersion")
    crd_resource_client = client_interface.create_resource_client(client, test_crd_kind, test_crd_api_version)
    client_interface.apply(crd_resource_client, test_crd)

    # Wait for CRD to take effect
    time.sleep(1)

    # Time how long client resource creation takes
    for _ in range(repetitions):
        with time_for_list(timing_info.resource_client_create_times):
            resource_client = client_interface.create_resource_client(client, test_crd_kind, test_crd_api_version)

    # For each file in the data folder try running the test
    for test_file in ROOT_FOLDER_PATH.glob("data/*.json"):
        print(f"{client_interface.__class__.__name__}: Testing file: {test_file}")
        data_to_test = json.loads(test_file.read_bytes())
        data_to_test_name = f"{data_to_test['metadata']['name']}-{client_interface.__class__.__name__}".lower()
        data_to_test_namespace = namespace
        data_to_test_kind = data_to_test.get("kind")
        data_to_test_api_version = data_to_test.get("apiVersion")

        # Update CR with unique names/namespace
        data_to_test["metadata"]["namespace"] = data_to_test_namespace
        data_to_test["metadata"]["name"] = data_to_test_name
        resource_client = client_interface.create_resource_client(client, data_to_test_kind, data_to_test_api_version)

        # Delete any existing resource incase it was accidentally created
        with suppress(Exception):
            client_interface.delete(
                resource_client, data_to_test_name, data_to_test_namespace, data_to_test_kind, data_to_test_api_version
            )

        # For the number of repetitions run the test
        resource_timing_info = ResourceTimingInfo()
        for _ in range(repetitions):
            with time_for_list(resource_timing_info.create_times):
                client_interface.create(resource_client, data_to_test)
            with time_for_list(resource_timing_info.apply_times):
                client_interface.apply(resource_client, data_to_test)
            with time_for_list(resource_timing_info.get_times):
                client_interface.get(
                    resource_client,
                    data_to_test_name,
                    data_to_test_namespace,
                )
            with time_for_list(resource_timing_info.list_times):
                client_interface.list(resource_client, data_to_test_namespace)
            with time_for_list(resource_timing_info.delete_times):
                client_interface.delete(
                    resource_client,
                    data_to_test_name,
                    data_to_test_namespace,
                )
        timing_info.resource_timing_info[test_file.name] = resource_timing_info

    # Unimport the modules for better memory tracking
    for module in modules_to_unimport:
        unimport_module(module)

    return timing_info
