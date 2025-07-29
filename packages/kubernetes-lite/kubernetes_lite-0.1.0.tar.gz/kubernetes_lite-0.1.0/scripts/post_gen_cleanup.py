# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
"""This script is used to add kubernetes_lite specific post-processing to the
result of gopy. This includes renaming platform specific files, updating CFLAG/LDFLAGS
and deleting extra unneeded files.
"""

from pathlib import Path

from scripts.utils import SYSTEM, SystemTypes

import typer

app = typer.Typer()

CGO_CFLAGS = "#cgo CFLAGS: -Wno-error -Wno-implicit-function-declaration -Wno-int-conversion -Ofast"

CGO_LDFLAGS: str | None = None
if SYSTEM in {SystemTypes.DARWIN, SystemTypes.LINUX}:
    CGO_LDFLAGS = "#cgo LDFLAGS: -ldl"


@app.command()
def post_gen_cleanup(parent_dir: Path, wrapper_subpath: str):
    """Cleanup and update the generated wrapper

    Args:
        parent_dir (Path): The root directory of the library
        wrapper_subpath (str): The name of the wrapper directory
    """
    # Delete generated license/library files
    for del_file_name in ("LICENSE", "Makefile", "MANIFEST.in", "README.md", "setup.py"):
        del_file_path = parent_dir / del_file_name
        del_file_path.unlink(missing_ok=True)

    wrapper_dir = parent_dir / wrapper_subpath
    # Move platform specific wrapper file to generic
    if len(list(wrapper_dir.glob("_wrapper.*.h"))) > 0:
        wrapper_h_file = next(wrapper_dir.glob("_wrapper.*.h"))
        wrapper_h_file.rename(wrapper_dir / "_wrapper.h")

    # Update the CGO flags
    go_file = wrapper_dir / "wrapper.go"
    go_output_text = ""
    for line in go_file.read_text().split("\n"):
        if line.startswith("#cgo CFLAGS"):
            go_output_text += CGO_CFLAGS + "\n"
        elif CGO_LDFLAGS and line.startswith("#cgo LDFLAGS"):
            go_output_text += CGO_LDFLAGS + "\n"
        else:
            go_output_text += line + "\n"
    go_file.write_text(go_output_text)


if __name__ == "__main__":
    app()
