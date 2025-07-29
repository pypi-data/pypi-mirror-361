# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
"""This is a helper script to install the build system dependencies. For now this
just installs the correct version of golang. Due to where this is ran we can not have
any external dependencies (e.g. requests)
"""

import copy
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from enum import StrEnum
from pathlib import Path
from urllib.request import urlopen

from scripts.utils import ARCH, SYSTEM, SystemTypes

# Base settings for go/src/dest
GO_VERSION = "1.23.7"
GO_BASE_URL = "https://go.dev/dl/go{version!s}.{system!s}-{arch!s}.{archive!s}"
DEST_PATH = Path(tempfile.gettempdir())


class ArchiveType(StrEnum):
    """ArchiveType is a simple enum to track what type of archive go stores for a platform"""

    ZIP = "zip"
    TAR = "tar.gz"


archive = None
if platform.system() == "Linux" or platform.system() == "Darwin":
    archive = ArchiveType.TAR
elif platform.system() == "Windows":
    archive = ArchiveType.ZIP
else:
    raise ValueError(f"Unknown machine system {platform.system()}")

# Setup a directory to download the tar to
with tempfile.TemporaryDirectory() as temp_dir:
    temp_path = Path(temp_dir)
    archive_file = temp_path / f"go.{archive!s}"

    # Template the url and send the request
    go_url = GO_BASE_URL.format(
        version=GO_VERSION,
        arch=ARCH,
        system=SYSTEM,
        archive=archive,
    )
    print(f"Attempting to download go src from: {go_url}", file=sys.stderr)
    with urlopen(go_url) as response:
        archive_file.write_bytes(response.read())

    print(f"Attempting to extract archive to: {DEST_PATH}", file=sys.stderr)
    shutil.unpack_archive(archive_file, str(DEST_PATH))

# Print the path used for installation
go_path = DEST_PATH / "go/bin"
go_bin = go_path / "go"
print(f"Binary path for go: {go_path}", file=sys.stderr)
current_env = copy.deepcopy(os.environ)
current_env["GOBIN"] = str(go_path)

# Ensure go is usable. ! Note this requires the path be set externally
subprocess.run([f"{go_bin}", "version"], check=True, stdout=sys.stderr, env=current_env)
# ! Install the make gen dependencies
subprocess.run(
    ["pip", "install", "pybindgen", "typer"],
    check=True,
    stdout=sys.stderr,
    env=current_env,
)
subprocess.run(
    [f"{go_bin}", "install", "golang.org/x/tools/cmd/goimports@latest"],
    check=True,
    stdout=sys.stderr,
    env=current_env,
)
subprocess.run(
    [f"{go_bin}", "install", "github.com/go-python/gopy@latest"], check=True, stdout=sys.stderr, env=current_env
)


if SYSTEM in {SystemTypes.LINUX, SystemTypes.DARWIN}:
    print(f"export PATH=$PATH:{go_path}")
    print(f"export GO_INSTALL_PATH={go_path}")
else:
    print(f"SET PATH=%PATH%;{go_path}")
    print(f"SET GO_INSTALL_PATH={go_path}")
    print(f"ls {go_path}")

# System-link go binaries to a usr defined path
if SYSTEM in {SystemTypes.DARWIN, SystemTypes.LINUX}:
    print(f"ln -s {go_path}/* /usr/local/bin")
