# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
"""This module runs the setup-envtest command from python as if the user ran
setuptest-env directly
"""

import logging

from kubernetes_lite.setup_envtest import run_setup_envtest_command

# Configure logging and run the setup_envtest command
logging.basicConfig(level=logging.INFO, format="%(message)s")
run_setup_envtest_command()
