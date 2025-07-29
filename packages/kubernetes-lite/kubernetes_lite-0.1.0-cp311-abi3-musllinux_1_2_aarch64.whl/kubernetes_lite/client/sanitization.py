# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
"""This module contains code around sanitizing an object for deployment"""

import datetime
from dataclasses import dataclass
from typing import Any

from kubernetes_lite.serialization import serialize_to_go
from kubernetes_lite.wrapper.go import Slice_byte

# SourceObjectType are helper types to attempt to describe common objects passed to client functions. See
# sanitize_resource_for_serialization for more information
SourceObjectType = (
    float | bool | property | datetime.datetime | datetime.date | bytes | str | int | list | tuple | dict | Any | None
)
SanitizedObjectType = float | bool | bytes | str | int | list | tuple | dict | Any | None


# Stolen from kubernetes but modified for None pruning, safety, and openapi handling
# https://github.com/kubernetes-client/python/blob/d67bc8c2bdb89b29c17c1ba0edb03a48d977c0e2/kubernetes/client/api_client.py#L202
def sanitize_resource_for_serialization(obj: SourceObjectType) -> SanitizedObjectType:  # noqa: PLR0911, PLR0912
    """Sanitize an object before serializing it to bytes
    If obj is None, return None.
    If obj is str, int, long, float, bool, return directly.
    If obj is datetime.datetime, datetime.date
        convert to string in iso8601 format.
    If obj is list, sanitize each element in the list.
    If obj is dict, return the dict.
    If obj is OpenAPI model, return the properties dict.
    :param obj: The data to serialize.
    :return: The serialized form of data.
    """
    if obj is None:  # pylint: disable=no-else-return
        return None
    elif isinstance(obj, float | bool | bytes | str | int):
        return obj
    elif isinstance(obj, list):
        return [sanitize_resource_for_serialization(sub_obj) for sub_obj in obj]
    elif isinstance(obj, tuple):
        return tuple(sanitize_resource_for_serialization(sub_obj) for sub_obj in obj)
    elif isinstance(obj, datetime.datetime | datetime.date):
        return obj.isoformat()
    elif isinstance(obj, property):
        return sanitize_resource_for_serialization(obj.fget())

    if isinstance(obj, dict):
        obj_dict = obj
    elif hasattr(obj, "attribute_map"):
        # Convert model obj to dict except
        # `openapi_types` and `attribute_map`.
        # Convert attribute name to json key in
        # model definition for request.
        obj_dict = {}
        for attr, name in obj.attribute_map.items():
            if hasattr(obj, attr):
                obj_dict[name] = getattr(obj, attr)
    else:
        # Hope that the object can still be serialized by the json encoder.
        return obj

    # Prune fields which are None but keep
    # empty arrays or dictionaries
    return_dict = {}
    for key, val in obj_dict.items():
        updated_obj = sanitize_resource_for_serialization(val)
        if updated_obj is not None:
            return_dict[key] = updated_obj
    return return_dict


@dataclass
class ObjectMetadata:
    """ObjectMetadata is used to describe extracted information from an object

    Attributes:
        metadata (dict[str, Any]): Metadata extracted from the object
        name (str):  Name of the object
        namespace (str | None): Optional namespace of the object

    """

    metadata: dict[str, Any]
    name: str
    namespace: str | None


def process_input_resource(obj: SanitizedObjectType) -> tuple[Slice_byte, ObjectMetadata]:
    """Sanitize and serialize an object into go. After sanitizing extract some metadata about the
    object.

    Args:
        obj (SanitizedObjectType): The object to sanitize/serialize

    Returns:
        tuple[Slice_byte, ObjectMetadata]: The serialized go object and extracted metadata
    """
    sanitized_obj = sanitize_resource_for_serialization(obj)

    if not isinstance(sanitized_obj, dict):
        raise RuntimeError(f"can not deploy object of type {type(sanitized_obj)}")

    # Extract metadata from sanitized object
    metadata = ObjectMetadata(
        name=sanitized_obj.get("metadata", {}).get("name"),
        namespace=sanitized_obj.get("metadata", {}).get("namespace"),
        metadata=sanitized_obj.get("metadata", {}),
    )

    return (serialize_to_go(sanitized_obj), metadata)
