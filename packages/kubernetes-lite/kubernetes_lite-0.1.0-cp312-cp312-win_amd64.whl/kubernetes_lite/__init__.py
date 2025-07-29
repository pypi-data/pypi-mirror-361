# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
"""Kubernetes_lite is a lightweight wrapper around the dynamic client from k8s.io/client-go/dynamic,
the 'mock' kubernetes server from sigs.k8s.io/controller-runtime/pkg/envtest, and its helper tool
setup-envtest https://pkg.go.dev/sigs.k8s.io/controller-runtime/tools/setup-envtest
"""

try:
    # Local
    from ._version import __version__, __version_tuple__  # noqa: F401 # unused import
except ImportError:
    __version__ = "unknown"
    version_tuple = (0, 0, __version__)
