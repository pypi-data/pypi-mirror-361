# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
"""This module contains a list of possible kubernetes errors and helper
functions to convert go_wrapper errors into their respective python
classes
"""

# Assisted by watsonx Code Assistant
from collections.abc import Callable
from typing import ParamSpec, TypeVar


# Copy of all kubernetes errors
class UnknownError(RuntimeError):
    """See https://pkg.go.dev/k8s.io/apimachinery/pkg/apis/meta/v1#StatusReason"""


class UnauthorizedError(RuntimeError):
    """See https://pkg.go.dev/k8s.io/apimachinery/pkg/apis/meta/v1#StatusReason"""


class ForbiddenError(RuntimeError):
    """See https://pkg.go.dev/k8s.io/apimachinery/pkg/apis/meta/v1#StatusReason"""


class NotFoundError(RuntimeError):
    """See https://pkg.go.dev/k8s.io/apimachinery/pkg/apis/meta/v1#StatusReason"""


class AlreadyExistsError(RuntimeError):
    """See https://pkg.go.dev/k8s.io/apimachinery/pkg/apis/meta/v1#StatusReason"""


class ConflictError(RuntimeError):
    """See https://pkg.go.dev/k8s.io/apimachinery/pkg/apis/meta/v1#StatusReason"""


class GoneError(RuntimeError):
    """See https://pkg.go.dev/k8s.io/apimachinery/pkg/apis/meta/v1#StatusReason"""


class InvalidError(RuntimeError):
    """See https://pkg.go.dev/k8s.io/apimachinery/pkg/apis/meta/v1#StatusReason"""


class ServerTimeoutError(RuntimeError):
    """See https://pkg.go.dev/k8s.io/apimachinery/pkg/apis/meta/v1#StatusReason"""


class StoreReadErrorError(RuntimeError):
    """See https://pkg.go.dev/k8s.io/apimachinery/pkg/apis/meta/v1#StatusReason"""


class ClientTimeoutError(RuntimeError):
    """See https://pkg.go.dev/k8s.io/apimachinery/pkg/apis/meta/v1#StatusReason.
    This class corresponds to the general TimeoutError
    """


class TooManyRequestsError(RuntimeError):
    """See https://pkg.go.dev/k8s.io/apimachinery/pkg/apis/meta/v1#StatusReason"""


class BadRequestError(RuntimeError):
    """See https://pkg.go.dev/k8s.io/apimachinery/pkg/apis/meta/v1#StatusReason"""


class MethodNotAllowedError(RuntimeError):
    """See https://pkg.go.dev/k8s.io/apimachinery/pkg/apis/meta/v1#StatusReason"""


class NotAcceptableError(RuntimeError):
    """See https://pkg.go.dev/k8s.io/apimachinery/pkg/apis/meta/v1#StatusReason"""


class RequestEntityTooLargeError(RuntimeError):
    """See https://pkg.go.dev/k8s.io/apimachinery/pkg/apis/meta/v1#StatusReason"""


class UnsupportedMediaTypeError(RuntimeError):
    """See https://pkg.go.dev/k8s.io/apimachinery/pkg/apis/meta/v1#StatusReason"""


class InternalErrorError(RuntimeError):
    """See https://pkg.go.dev/k8s.io/apimachinery/pkg/apis/meta/v1#StatusReason"""


class ExpiredError(RuntimeError):
    """See https://pkg.go.dev/k8s.io/apimachinery/pkg/apis/meta/v1#StatusReason"""


class ServiceUnavailableError(RuntimeError):
    """See https://pkg.go.dev/k8s.io/apimachinery/pkg/apis/meta/v1#StatusReason"""


# Map the kubernetes StatusReason strings to the python errors
EXCEPTION_MAPPING = {
    "Unknown": UnknownError,
    "Unauthorized": UnauthorizedError,
    "Forbidden": ForbiddenError,
    "NotFound": NotFoundError,
    "AlreadyExists": AlreadyExistsError,
    "Conflict": ConflictError,
    "Gone": GoneError,
    "Invalid": InvalidError,
    "ServerTimeout": ServerTimeoutError,
    "StoreReadError": StoreReadErrorError,
    "Timeout": ClientTimeoutError,
    "TooManyRequests": TooManyRequestsError,
    "BadRequest": BadRequestError,
    "MethodNotAllowed": MethodNotAllowedError,
    "NotAcceptable": NotAcceptableError,
    "RequestEntityTooLarge": RequestEntityTooLargeError,
    "UnsupportedMediaType": UnsupportedMediaTypeError,
    "InternalError": InternalErrorError,
    "Expired": ExpiredError,
    "ServiceUnavailable": ServiceUnavailableError,
}


# Vars used in typing the client
KUBE_RETURN_TYPE = TypeVar("KUBE_RETURN_TYPE")
KUBE_PARAM_TYPE = ParamSpec("KUBE_PARAM_TYPE")


def wrap_kube_error(func: Callable[KUBE_PARAM_TYPE, KUBE_RETURN_TYPE]) -> Callable[KUBE_PARAM_TYPE, KUBE_RETURN_TYPE]:
    """Wrap a a function so that generic gopy RuntimeErrors
    are turned into the appropriate kubernetes error type.

    Args:
        func (Callable): The function to wrap

    Returns:
        Callable: The wrapped function
    """

    def wrapped_callable(*args: KUBE_PARAM_TYPE.args, **kwargs: KUBE_PARAM_TYPE.kwargs) -> KUBE_RETURN_TYPE:
        try:
            return func(*args, **kwargs)
        except RuntimeError as exc:
            # If the error has an args attribute then try to parse it into one of
            # the above classes
            if len(exc.args) > 0:
                # Split the string at : to try to extract the message type. This is
                # defined by KubernetesErrorSep in the go code
                message = str(exc.args[0])
                split_message = message.split(":")

                # Use the first part of the message to map to the exception type
                if split_message[0] in EXCEPTION_MAPPING:
                    new_exc_type = EXCEPTION_MAPPING[split_message[0]]

                    # Recreate the unsplit message with out the parsed bit
                    exc_message = ":".join(split_message[1:])
                    raise new_exc_type(exc_message) from None
            raise exc

    return wrapped_callable
