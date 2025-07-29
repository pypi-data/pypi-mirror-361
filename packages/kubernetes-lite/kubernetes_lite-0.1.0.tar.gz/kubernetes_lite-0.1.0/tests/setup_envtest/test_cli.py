# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
"""This module tests that setup-envtest functions like the go version"""

import subprocess
from pathlib import Path


def test_help():
    """Test that help text is displayed if --help is passed in"""
    proc = subprocess.run(
        ["python3", "-m", "kubernetes_lite.setup_envtest", "--help"], capture_output=True, check=False
    )
    assert proc.returncode == 2
    assert b"Usage: python3 -m kubernetes_lite.setup_envtest" in proc.stderr


def test_use():
    """Test that we can get the path from envtest"""
    proc = subprocess.run(
        ["python3", "-m", "kubernetes_lite.setup_envtest", "use", "-p", "path"], capture_output=True, check=False
    )
    assert proc.returncode == 0
    file_path = Path(proc.stdout.decode("utf-8"))
    assert file_path.exists()
    assert file_path.is_dir()
