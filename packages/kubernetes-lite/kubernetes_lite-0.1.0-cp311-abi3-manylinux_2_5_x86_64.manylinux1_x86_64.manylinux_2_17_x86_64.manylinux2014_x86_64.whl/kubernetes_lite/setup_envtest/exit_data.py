# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
"""This module contains helper dataclasses/functions for parsing exit data
information from setupenv-test
"""

import re
from dataclasses import dataclass

# Regex for parsing the exit code and text from a string. Here is an expected text this regex
# can parse "some error message (exit code 2)"
EXIT_CODE_REGEX = re.compile(r"(?P<text>.*)\(exit code (?P<code>[0-9])\).*")


@dataclass
class ExitData:
    """ExitData dataclass contains the exit code and message for a setup-envtest
    command run

    Attributes:
        code int: The exit code that was parsed
        message (str | None): An optional string message if one was extracted
    """

    code: int
    message: str | None

    @classmethod
    def from_string(cls, error: str) -> "ExitData|None":
        """Attempt to parse a error string into a ExitData dataclass

        Returns:
            ExitData|None: The parsed ExitData or None if one couldn't
                be extracted
        """
        # Attempt to match the regex
        match = EXIT_CODE_REGEX.match(error)
        if not match:
            return

        matches = match.groupdict()
        exit_code = matches.get("code", None)
        message = matches.get("text", None).strip()
        if message:
            message = None

        if exit_code:
            try:
                exit_code = int(exit_code)
            except ValueError:
                return

        return cls(code=exit_code, message=message)
