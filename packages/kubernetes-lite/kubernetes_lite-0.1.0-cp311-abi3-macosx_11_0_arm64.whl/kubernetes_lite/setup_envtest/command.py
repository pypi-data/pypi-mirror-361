# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
"""This module contains functions to run setup-envtest commands"""

import copy
import logging
import select
import sys
from logging import Logger
from pathlib import Path

from kubernetes_lite.serialization import serialize_to_go
from kubernetes_lite.setup_envtest.result import SetupEnvTestResult
from kubernetes_lite.wrapper.setup import SetupEnvTest


def internal_run_setup_envtest_command(*args: list[str], stdin: bytes = b"") -> SetupEnvTestResult:
    """This function runs the underlying setup_envtest command with a provided args and stdin.

    Args:
        *args (list[str]): The arguments to pass to setup-envtest
        stdin (bytes, optional): The stdin data to send to setup-envtest. Defaults to b"".

    Returns:
        SetupEnvTestResult: A parsed dataclass containing the returned error and captured stdout/stderr
    """
    # Convert input args to go slices
    go_stdin = serialize_to_go(stdin)
    go_args = serialize_to_go(["python3 -m kubernetes_lite.setup_envtest", *args])

    # Run setup env test
    setup_result_raw = SetupEnvTest(go_stdin, go_args)

    # Deserialize the result
    return SetupEnvTestResult.from_go(setup_result_raw)


def run_setup_envtest_command(log: Logger | None = None):
    """Function to handle running the setup_envtest command as if the user ran this module
    directly. It handles reading from the process args/stdin and passing them to
    internal_run_setup_envtest_command. This function handles logging the result and
    exiting with the correct exit code

    Args:
        log (Logger | None, optional): Logger to use for printing setup_envtest messages.
            Defaults to None.
    """
    if not log:
        log = logging.getLogger("setup-envtest")

    args = copy.deepcopy(sys.argv)

    # If there are args in sys.args then check to see if the module was included. If so remove the first item
    if len(args) > 0:
        current_file_path = Path(__file__)
        if str(current_file_path.parent) in args[0]:
            args.pop(0)

    # Read stdin into a buffer
    stdin_available_list, _, _ = select.select([sys.stdin], [], [], 0.1)
    stdin_data = ""
    if len(stdin_available_list) > 0:
        stdin_byte = sys.stdin.read(1)
        stdin_data = stdin_byte
        while len(stdin_byte) > 0:
            stdin_byte = sys.stdin.read(1)
            stdin_data += stdin_byte

    setup_result = internal_run_setup_envtest_command(*args, stdin=stdin_data.encode("utf-8"))

    # Log results messages without raising the exception
    setup_result.log_and_raise(log)

    # If we parsed and exit code from the logs then exit
    if setup_result.exit_data and setup_result.exit_data.code:
        sys.exit(setup_result.exit_data.code)
