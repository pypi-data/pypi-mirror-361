# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
"""This module contains common helpers used throughout the various
python scripts
"""

import platform
from enum import StrEnum


# Consts for platforms
class SystemTypes(StrEnum):
    """SystemTypes is a simple enum to track the parent OS"""

    LINUX = "linux"
    DARWIN = "darwin"
    WINDOWS = "windows"


class ArchTypes(StrEnum):
    """ArchTypes is a simple enum to track the processor type"""

    AMD64 = "amd64"
    X386 = "386"
    ARM64 = "arm64"
    S390 = "s390x"


# Parse the system architecture and platform
SYSTEM: SystemTypes | None = None
ARCH: ArchTypes | None = None
if platform.machine().lower() in {"x86_64", "amd64"}:
    ARCH = ArchTypes.AMD64
elif platform.machine().lower() in {"i386", "i686"}:
    ARCH = ArchTypes.X386
elif platform.machine().lower() in {"aarch64", "arm64", "armv8b", "armv8l", "aarch64_be"}:
    ARCH = ArchTypes.ARM64
elif platform.machine().lower() in {"s390x"}:
    ARCH = ArchTypes.S390
else:
    raise ValueError(f"Unknown machine platform {platform.machine()}")

if platform.system() == "Linux":
    SYSTEM = SystemTypes.LINUX
elif platform.system() == "Darwin":
    SYSTEM = SystemTypes.DARWIN
elif platform.system() == "Windows":
    SYSTEM = SystemTypes.WINDOWS
else:
    raise ValueError(f"Unknown machine system {platform.system()}")
