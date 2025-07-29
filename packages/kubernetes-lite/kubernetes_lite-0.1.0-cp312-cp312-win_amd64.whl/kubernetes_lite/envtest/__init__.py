# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
"""This module contains a pythonic wrapper around the https://pkg.go.dev/sigs.k8s.io/controller-runtime/pkg/envtest
EnvTest object
"""

from kubernetes_lite.envtest.envtest import EnvTest

__all__ = [
    "EnvTest",
]
