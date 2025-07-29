# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
"""This module contains a dataclass used in processing the result from
setup-envtest
"""

from dataclasses import dataclass
from functools import cached_property
from logging import Logger

from kubernetes_lite.serialization import deserialize_from_go
from kubernetes_lite.setup_envtest.exit_data import ExitData
from kubernetes_lite.wrapper.go import Slice_byte


@dataclass
class SetupEnvTestResult:
    """SetupEnvTestResult contains information regarding the result of a setup-envtest
    run. This includes the captured stdout/stderr as well as the exit information

    Attributes:
        stderr (str | None): the captured stderr data if some was captured
        stdout (str | None): the captured stdout data if some was captured
        error (str | None): the serialized error data if one was returned
    """

    stderr: str | None = None
    stdout: str | None = None
    error: str | None = None

    @cached_property
    def exit_data(self) -> ExitData | None:
        """The parsed ExitData instance for this result

        Returns:
            ExitData | None: The ExitData object if one could be generated. Else None
        """
        if not self.error:
            return
        return ExitData.from_string(self.error)

    @cached_property
    def is_multi_output(self) -> bool:
        """Helper property used when printing the result to determine if
        multiple ==<>== header tags are needed

        Returns:
            bool: If more then one of stdout/stderr/error was provided
        """
        return (
            sum(
                [
                    bool(self.stdout),
                    bool(self.stderr),
                    bool(self.exit_data.message if self.exit_data else False),
                ]
            )
            > 1
        )

    def log_and_raise(self, log: Logger, raise_exc: bool = False):
        """Helper function to print the results to a log and raise an exception
        if the command was not successful

        Args:
            log (Logger): The logger to print result information to
            raise_exc (bool, optional): If an exception should be raised if the result was
                invalid. Defaults to False.
        """
        should_raise_exc: bool = False
        if self.exit_data and self.exit_data.message:
            if self.is_multi_output:
                log.error("==Error==")
            log.error(self.exit_data.message)
            should_raise_exc = True
        if self.stderr:
            if self.is_multi_output:
                log.info("==StdErr==")
            log.error(self.stderr)
            should_raise_exc = True
        if self.stdout:
            if self.is_multi_output:
                log.info("==StdOut==")
            log.info(self.stdout)

        if should_raise_exc and raise_exc:
            raise RuntimeError("Failed to run SetupEvTet")

    @classmethod
    def from_go(cls, raw_data: Slice_byte) -> "SetupEnvTestResult":
        """Parse a SetupEnvTestResult object from a raw golang Slice_byte object

        Args:
            raw_data (Slice_byte): The raw data from go

        Returns:
            SetupEnvTestResult: the parsed result object
        """
        result_dict = deserialize_from_go(raw_data)

        return cls(**result_dict)
