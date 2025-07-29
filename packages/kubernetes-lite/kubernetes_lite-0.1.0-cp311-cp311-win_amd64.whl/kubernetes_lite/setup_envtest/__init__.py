# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
"""This module contains functions to run setup-envtest. See
https://pkg.go.dev/sigs.k8s.io/controller-runtime/tools/setup-envtest for
more information regarding arguments
"""

from kubernetes_lite.setup_envtest.command import (
    internal_run_setup_envtest_command,
    run_setup_envtest_command,
)

__all__ = ["internal_run_setup_envtest_command", "run_setup_envtest_command"]
