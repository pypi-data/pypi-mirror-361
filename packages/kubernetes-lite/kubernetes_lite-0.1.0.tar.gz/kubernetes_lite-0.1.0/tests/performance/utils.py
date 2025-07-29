# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
"""This module contains useful testing utils that can't be stored in the
test or framework modules due to circular imports
"""

import statistics
import sys
import time
from contextlib import contextmanager


def unimport_module(module_name: str):
    """Helper to un-import the given module and its parents/siblings/
    children

    Arguments:
        module_name (str): The module name to unimport
    """
    if module_name in sys.modules:
        sys.modules.pop(module_name)

    # UnImport the module and any parent/sibling/child modules so
    # controller can be reimported from the most recent sys path
    module_parts = module_name.split(".")
    for i in range(1, len(module_parts)):
        parent_module = ".".join(module_parts[:-i])
        if parent_module in sys.modules:
            sys.modules.pop(parent_module, None)

    for child_module in [mod_name for mod_name in sys.modules if mod_name.startswith(f"{module_parts[0]}.")]:
        sys.modules.pop(child_module, None)


def calculate_timing_info(timing_list: list[float]) -> tuple[float, float]:
    """Calculate the average and stddiv for a list of floats

    Args:
        timing_list (list[float]): List of floats to calculate info about

    Returns:
        tuple[float, float]: The average and stddiv for the list
    """
    if len(timing_list) < 1:
        raise ValueError("Can't calculate timing information with empty list")

    stddev = 0
    average = timing_list[0] * 1000
    if len(timing_list) > 1:
        stddev = statistics.stdev(timing_list) * 1000
        average = statistics.mean(timing_list) * 1000
    return average, stddev


@contextmanager
def time_for_list(result_list: list[float]):
    """Context manager to aid in timing a function and appending it to an existing list
    of float

    Args:
        result_list (list[float]): the list to append timing information to
    """
    start_time = time.perf_counter()
    yield
    end_time = time.perf_counter()
    result_list.append(end_time - start_time)
