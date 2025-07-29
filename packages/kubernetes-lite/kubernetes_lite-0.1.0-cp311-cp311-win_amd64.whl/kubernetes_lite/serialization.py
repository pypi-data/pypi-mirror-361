# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
"""This module contains helper functions to serialize python objects into
go Slice_bytes and back
"""

from io import BytesIO
from typing import Any

from kubernetes_lite.wrapper._wrapper import Slice_byte_from_bytes
from kubernetes_lite.wrapper.go import Slice_byte

import orjson


def serialize(obj: Any) -> bytes:
    """Serialize a python object using orjson into bytes

    Args:
        obj (Any): The object to serialize

    Returns:
        bytes: The return bytes data
    """
    if isinstance(obj, bytes):
        return obj
    return orjson.dumps(obj)


def serialize_to_go(obj: Any) -> Slice_byte:
    """Serialize a python object into a go object

    Args:
        obj (Any): The object to serialize

    Returns:
        Slice_byte: Pointer to the go object
    """
    if isinstance(obj, Slice_byte):
        return obj
    if isinstance(obj, BytesIO):
        obj = obj.read()
    # Don't use Slice_byte(<>) since its slow!
    handle = Slice_byte_from_bytes(serialize(obj))
    return Slice_byte(handle=handle)


def deserialize_result(obj: bytes) -> dict:
    """Deserialize an object using orjson into a python dictionary

    Args:
        obj (bytes): The bytes object to deserialize

    Returns:
        dict: The deserialized object as a dictionary
    """
    return orjson.loads(obj)


def deserialize_from_go(obj: Slice_byte) -> dict:
    """Deserialize a Slice_byte object from go into a python dictionary

    Args:
        obj (Slice_byte): The go object to deserialize

    Returns:
        dict: The deserialized object as a dictionary
    """
    return deserialize_result(bytes(obj))
