# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
"""This module contains a simple pythonic wrapper around the k8s.io/client-go/dynamic
DynamicClient.
"""

from kubernetes_lite.client.client import DynamicClient
from kubernetes_lite.client.resource import DynamicResource
from kubernetes_lite.client.sanitization import SourceObjectType
from kubernetes_lite.client.watch import Watch

__all__ = ["DynamicClient", "DynamicResource", "SourceObjectType", "Watch"]
