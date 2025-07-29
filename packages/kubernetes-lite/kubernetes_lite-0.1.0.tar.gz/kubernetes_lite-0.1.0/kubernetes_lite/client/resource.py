# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
"""This module contains the DynamicResource which is the main way to interact
with the cluster
"""

# Assisted by watsonx Code Assistant
import warnings
from typing import Any

from kubernetes_lite.client.sanitization import SourceObjectType, process_input_resource
from kubernetes_lite.client.watch import Watch
from kubernetes_lite.errors import wrap_kube_error
from kubernetes_lite.serialization import (
    deserialize_from_go,
    serialize_to_go,
)
from kubernetes_lite.wrapper.client import (
    WrappedNamespaceableResourceInterface,
)


class DynamicResource:
    """DynamicResource is the primary client for interacting with resources on the cluster. It's
    functions mirror the ResourceInterface provided by https://pkg.go.dev/k8s.io/client-go/dynamic#ResourceInterface.
    The parameters to the various functions map to the json names of the Options objects in
    https://pkg.go.dev/k8s.io/apimachinery/pkg/apis/meta/v1. For example `list()` parameter's map
    to ListOptions
    """

    def __init__(self, resource: WrappedNamespaceableResourceInterface):
        """Create a DynamicResource which points to a WrappedNamespaceableResourceInterface from go. This class
        should not be initialized directly and should instead be created by the client/discoverer

        Args:
            resource (WrappedNamespaceableResourceInterface): The WrappedNamespaceableResourceInterface to wrap
        """
        self._resource = resource

    @wrap_kube_error
    def get(
        self,
        name: str | None = None,
        namespace: str | None = None,
        resource_version: str | None = None,
        extra_options_kwargs: dict[str, Any] | None = None,
        subresources: list[str] | None = None,
        **kwargs,
    ) -> dict:
        """Get an object from the cluster. The parameters map to https://pkg.go.dev/k8s.io/apimachinery/pkg/apis/meta/v1#GetOptions

        Args:
            name (str | None, optional): The name of the resource to fetch. **None is Deprecated**. Defaults to None.
            namespace (str | None, optional): Optional namespace for the resource. Defaults to None.
            resource_version (str | None, optional): Optional resourceVersion to fetch. Defaults to None.
            extra_options_kwargs (dict[str, Any] | None, optional): Optional dictionary containing more GetOption
                parameters. Defaults to None.
            subresources (list[str] | None, optional): Subresource of an object to get. Defaults to None.
            **kwargs: Unused kwargs for compatibility

        Returns:
            dict: The object from the cluster as a dictionary
        """
        if name is None:
            warnings.warn(
                "Get with no name to list objects is deprecated. Use the list method instead",
                DeprecationWarning,
                stacklevel=2,
            )
            return self.list(namespace=namespace, resource_version=resource_version, **kwargs)

        options = {**(extra_options_kwargs or {}), **kwargs}
        if resource_version:
            options["resourceVersion"] = resource_version
        serialized_options = serialize_to_go(options)

        resource_ptr = self._resource
        if namespace:
            resource_ptr = resource_ptr.Namespace(namespace)

        subresource_options = subresources if subresources else []
        result = resource_ptr.Get(name, serialized_options, *subresource_options)
        return deserialize_from_go(result)

    @wrap_kube_error
    def create(  # noqa: PLR0917, PLR0913
        self,
        resource: SourceObjectType,
        namespace: str | None = None,
        dry_run: list[str] | None = None,
        field_manager: str | None = None,
        field_validation: str | None = None,
        extra_options_kwargs: dict[str, Any] | None = None,
        subresources: list[str] | None = None,
        **kwargs,
    ) -> dict:
        """Create an object in the cluster. The parameters map to https://pkg.go.dev/k8s.io/apimachinery/pkg/apis/meta/v1#CreateOptions

        Args:
            resource (SourceObjectType): The resource to deploy
            namespace (str | None, optional): Optional namespace for the resource. Defaults to None or namespace
                in the provided resources.
            dry_run (list[str] | None, optional): Optional List of string dryrruns to use. Valid values can be gathered
                from the golang docs. Defaults to None.
            field_manager (str | None, optional): Optional field manager string to use to manage resource fields.
                Defaults to None.
            field_validation (str | None, optional): Optional fieldValidation instructs the server on how to
                handle objects in the request containing unknown or duplicate fields. Defaults to None.
            extra_options_kwargs (dict[str, Any] | None, optional): Optional dictionary containing more CreateOption
                parameters. Defaults to None.
            subresources (list[str] | None, optional): Subresource of an object to get. Defaults to None.
            **kwargs: Unused kwargs for compatibility

        Returns:
            dict: The created object from the cluster in a dictionary
        """
        options = {**(extra_options_kwargs or {}), **kwargs}
        if dry_run:
            options["dryRun"] = dry_run
        if field_manager:
            options["fieldManager"] = field_manager
        if field_validation:
            options["fieldValidation"] = field_validation
        serialized_options = serialize_to_go(options)

        serialized_resource, resource_metadata = process_input_resource(resource)
        if not namespace and resource_metadata.namespace:
            namespace = resource_metadata.namespace
        resource_ptr = self._resource
        if namespace:
            resource_ptr = resource_ptr.Namespace(namespace)

        subresource_options = subresources if subresources else []
        result = resource_ptr.Create(serialized_resource, serialized_options, *subresource_options)
        return deserialize_from_go(result)

    @wrap_kube_error
    def update(  # noqa: PLR0917, PLR0913
        self,
        resource: SourceObjectType,
        namespace: str | None = None,
        dry_run: list[str] | None = None,
        field_manager: str | None = None,
        field_validation: str | None = None,
        extra_options_kwargs: dict[str, Any] | None = None,
        subresources: list[str] | None = None,
        **kwargs,
    ) -> dict:
        """Update an object in the cluster. The parameters map to https://pkg.go.dev/k8s.io/apimachinery/pkg/apis/meta/v1#UpdateOptions

        Args:
            resource (SourceObjectType): The resource to deploy
            namespace (str | None, optional): Optional namespace for the resource. Defaults to None or namespace
                in the provided resources.
            dry_run (list[str] | None, optional): Optional List of string dryrruns to use. Valid values can be gathered
                from the golang docs. Defaults to None.
            field_manager (str | None, optional): Optional field manager string to use to manage resource fields.
                Defaults to None.
            field_validation (str | None, optional): Optional fieldValidation instructs the server on how to
                handle objects in the request containing unknown or duplicate fields. Defaults to None.
            extra_options_kwargs (dict[str, Any] | None, optional): Optional dictionary containing more CreateOption
                parameters. Defaults to None.
            subresources (list[str] | None, optional): Subresource of an object to get. Defaults to None.
            **kwargs: Unused kwargs for compatibility

        Returns:
            dict: The updated object from the cluster in a dictionary
        """
        options = {**(extra_options_kwargs or {}), **kwargs}
        if dry_run:
            options["dryRun"] = dry_run
        if field_manager:
            options["fieldManager"] = field_manager
        if field_validation:
            options["fieldValidation"] = field_validation
        serialized_options = serialize_to_go(options)

        serialized_resource, resource_metadata = process_input_resource(resource)
        if not namespace and resource_metadata.namespace:
            namespace = resource_metadata.namespace
        resource_ptr = self._resource
        if namespace:
            resource_ptr = resource_ptr.Namespace(namespace)

        subresource_options = subresources if subresources else []
        result = resource_ptr.Update(serialized_resource, serialized_options, *subresource_options)
        return deserialize_from_go(result)

    @wrap_kube_error
    def update_status(  # noqa: PLR0917, PLR0913
        self,
        resource: SourceObjectType,
        namespace: str | None = None,
        dry_run: list[str] | None = None,
        field_manager: str | None = None,
        field_validation: str | None = None,
        extra_options_kwargs: dict[str, Any] | None = None,
        subresources: list[str] | None = None,
        **kwargs,
    ) -> dict:
        """Update the status object in the cluster. The parameters map to https://pkg.go.dev/k8s.io/apimachinery/pkg/apis/meta/v1#UpdateOptions

        Args:
            resource (SourceObjectType): The resource to deploy
            namespace (str | None, optional): Optional namespace for the resource. Defaults to None or namespace
                in the provided resources.
            dry_run (list[str] | None, optional): Optional List of string dryrruns to use. Valid values can be gathered
                from the golang docs. Defaults to None.
            field_manager (str | None, optional): Optional field manager string to use to manage resource fields.
                Defaults to None.
            field_validation (str | None, optional): Optional fieldValidation instructs the server on how to
                handle objects in the request containing unknown or duplicate fields. Defaults to None.
            extra_options_kwargs (dict[str, Any] | None, optional): Optional dictionary containing more CreateOption
                parameters. Defaults to None.
            subresources (list[str] | None, optional): Subresource of an object to get. Defaults to None.
            **kwargs: Unused kwargs for compatibility

        Returns:
            dict: The updated object from the cluster in a dictionary
        """
        options = {**(extra_options_kwargs or {}), **kwargs}
        if dry_run:
            options["dryRun"] = dry_run
        if field_manager:
            options["fieldManager"] = field_manager
        if field_validation:
            options["fieldValidation"] = field_validation
        serialized_options = serialize_to_go(options)

        serialized_resource, resource_metadata = process_input_resource(resource)
        if not namespace and resource_metadata.namespace:
            namespace = resource_metadata.namespace
        resource_ptr = self._resource
        if namespace:
            resource_ptr = resource_ptr.Namespace(namespace)

        subresource_options = subresources if subresources else []
        result = resource_ptr.UpdateStatus(serialized_resource, serialized_options, *subresource_options)
        return deserialize_from_go(result)

    @wrap_kube_error
    def patch(  # noqa: PLR0917, PLR0913
        self,
        name: str,
        patch_type: str,
        patch_data: SourceObjectType,
        namespace: str | None = None,
        dry_run: list[str] | None = None,
        field_manager: str | None = None,
        field_validation: str | None = None,
        force: bool | None = None,
        extra_options_kwargs: dict[str, Any] | None = None,
        subresources: list[str] | None = None,
        **kwargs,
    ) -> dict:
        """Patch an object in the cluster. The parameters map to https://pkg.go.dev/k8s.io/apimachinery/pkg/apis/meta/v1#PatchOptions

        Args:
            name (str): Name of the object to patch
            patch_type (str): Type of patch to use. See https://pkg.go.dev/k8s.io/apimachinery/pkg/types#PatchType for
                available options
            patch_data (SourceObjectType): The raw patch data to use

            resource (SourceObjectType): The resource to deploy
            namespace (str | None, optional): Optional namespace for the resource. Defaults to None or namespace
                in the provided resources.
            dry_run (list[str] | None, optional): Optional List of string dryrruns to use. Valid values can be gathered
                from the golang docs. Defaults to None.
            field_manager (str | None, optional): Optional field manager string to use to manage resource fields.
                Defaults to None.
            force (bool | None, optional): If the patch should be forced ignoring field_manager. Defaults to None.
            field_validation (str | None, optional): Optional fieldValidation instructs the server on how to
                handle objects in the request containing unknown or duplicate fields. Defaults to None.
            extra_options_kwargs (dict[str, Any] | None, optional): Optional dictionary containing more PatchOptions
                parameters. Defaults to None.
            subresources (list[str] | None, optional): Subresource of an object to get. Defaults to None.
            **kwargs: Unused kwargs for compatibility

        Returns:
            dict: The patched object from the cluster in a dictionary
        """
        options = {**(extra_options_kwargs or {}), **kwargs}
        if dry_run:
            options["dryRun"] = dry_run
        if field_manager:
            options["fieldManager"] = field_manager
        if field_validation:
            options["fieldValidation"] = field_validation
        if field_manager:
            options["force"] = force
        serialized_options = serialize_to_go(options)

        serialized_patch = serialize_to_go(patch_data)
        resource_ptr = self._resource
        if namespace:
            resource_ptr = resource_ptr.Namespace(namespace)

        subresource_options = subresources if subresources else []
        result = resource_ptr.Patch(name, patch_type, serialized_patch, serialized_options, *subresource_options)
        return deserialize_from_go(result)

    @wrap_kube_error
    def apply(  # noqa: PLR0917, PLR0913
        self,
        resource: SourceObjectType,
        name: str | None = None,
        namespace: str | None = None,
        dry_run: bool | None = None,
        field_manager: str | None = None,
        force: bool | None = None,
        extra_options_kwargs: dict[str, Any] | None = None,
        subresources: list[str] | None = None,
        **kwargs,
    ) -> dict:
        """Apply an object in the cluster. The parameters map to https://pkg.go.dev/k8s.io/apimachinery/pkg/apis/meta/v1#ApplyOptions.
        See https://kubernetes.io/docs/reference/using-api/server-side-apply/ for more information

        Args:
            resource (SourceObjectType): The resource to deploy
            name (str | None, optional): Optional name for the resource. Defaults to None or name
                in the provided resources.
            namespace (str | None, optional): Optional namespace for the resource. Defaults to None or namespace
                in the provided resources.
            dry_run (list[str] | None, optional): Optional List of string dryrruns to use. Valid values can be gathered
                from the golang docs. Defaults to None.
            field_manager (str | None, optional): Optional field manager string to use to manage resource fields.
                Defaults to None.
            force (bool | None, optional): If the patch should be forced ignoring field_manager. Defaults to None.
            extra_options_kwargs (dict[str, Any] | None, optional): Optional dictionary containing more ApplyOptions
                parameters. Defaults to None.
            subresources (list[str] | None, optional): Subresource of an object to get. Defaults to None.
            **kwargs: Unused kwargs for compatibility

        Returns:
            dict: The applied object from the cluster in a dictionary
        """
        options = {**(extra_options_kwargs or {}), **kwargs}
        if dry_run:
            options["dryRun"] = dry_run
        if field_manager:
            options["fieldManager"] = field_manager
        if force:
            options["force"] = force
        serialized_options = serialize_to_go(options)

        serialized_resource, resource_metadata = process_input_resource(resource)
        if not namespace and resource_metadata.namespace:
            namespace = resource_metadata.namespace
        if not name and resource_metadata.name:
            name = resource_metadata.name

        resource_ptr = self._resource
        if namespace:
            resource_ptr = resource_ptr.Namespace(namespace)

        subresource_options = subresources if subresources else []
        result = resource_ptr.Apply(name, serialized_resource, serialized_options, *subresource_options)
        return deserialize_from_go(result)

    @wrap_kube_error
    def apply_status(  # noqa: PLR0917, PLR0913
        self,
        resource: SourceObjectType,
        name: str | None = None,
        namespace: str | None = None,
        dry_run: bool | None = None,
        field_manager: str | None = None,
        force: bool | None = None,
        extra_options_kwargs: dict[str, Any] | None = None,
        subresources: list[str] | None = None,
        **kwargs,
    ) -> dict:
        """Apply a status object in the cluster. The parameters map to https://pkg.go.dev/k8s.io/apimachinery/pkg/apis/meta/v1#ApplyOptions.
        See https://kubernetes.io/docs/reference/using-api/server-side-apply/ for more information

        Args:
            resource (SourceObjectType): The resource to deploy
            name (str | None, optional): Optional name for the resource. Defaults to None or name
                in the provided resources.
            namespace (str | None, optional): Optional namespace for the resource. Defaults to None or namespace
                in the provided resources.
            dry_run (list[str] | None, optional): Optional List of string dryrruns to use. Valid values can be gathered
                from the golang docs. Defaults to None.
            field_manager (str | None, optional): Optional field manager string to use to manage resource fields.
                Defaults to None.
            force (bool | None, optional): If the patch should be forced ignoring field_manager. Defaults to None.
            field_validation (str | None, optional): Optional fieldValidation instructs the server on how to
                handle objects in the request containing unknown or duplicate fields. Defaults to None.
            extra_options_kwargs (dict[str, Any] | None, optional): Optional dictionary containing more ApplyOptions
                parameters. Defaults to None.
            subresources (list[str] | None, optional): Subresource of an object to get. Defaults to None.
            **kwargs: Unused kwargs for compatibility

        Returns:
            dict: The applied object from the cluster in a dictionary
        """
        options = {**(extra_options_kwargs or {}), **kwargs}
        if dry_run:
            options["dryRun"] = dry_run
        if field_manager:
            options["fieldManager"] = field_manager
        if force:
            options["force"] = force
        serialized_options = serialize_to_go(options)

        serialized_resource, resource_metadata = process_input_resource(resource)
        if not namespace and resource_metadata.namespace:
            namespace = resource_metadata.namespace
        if not name and resource_metadata.name:
            name = resource_metadata.name

        resource_ptr = self._resource
        if namespace:
            resource_ptr = resource_ptr.Namespace(namespace)

        subresource_options = subresources if subresources else []
        result = resource_ptr.ApplyStatus(name, serialized_resource, serialized_options, *subresource_options)
        return deserialize_from_go(result)

    @wrap_kube_error
    def delete(  # noqa: PLR0917, PLR0913
        self,
        name: str,
        namespace: str | None = None,
        grace_period_seconds: int | None = None,
        propagation_policy: str | None = None,
        dry_run: list[str] | None = None,
        ignore_store_read_error: bool | None = None,
        extra_options_kwargs: dict[str, Any] | None = None,
        **kwargs,
    ):
        """Delete an object from the cluster. The parameters map to https://pkg.go.dev/k8s.io/apimachinery/pkg/apis/meta/v1#DeleteOptions.

        Args:
            name (str): Name for the resource to delete.
            namespace (str | None, optional): Optional namespace for the resource. Defaults to None
            dry_run (list[str] | None, optional): Optional List of string dryrruns to use. Valid values can be gathered
                from the golang docs. Defaults to None.
            grace_period_seconds (int | None, optional): Optional time to wait for graceful termination before
                deleting the resource. Defaults to None.
            propagation_policy (str | None, optional): Optional DeletionPropagation decides how a deletion propagates
                to dependents of the object. See https://pkg.go.dev/k8s.io/apimachinery/pkg/apis/meta/v1#DeletionPropagation
                for more information. Defaults to None.
            ignore_store_read_error (bool | None, optional): Optional override to force successful deletion even
                if there is an etcd store error. Defaults to None.
            extra_options_kwargs (dict[str, Any] | None, optional): Optional dictionary containing more DeleteOptions
                parameters. Defaults to None.
            subresources (list[str] | None, optional): Subresource of an object to get. Defaults to None.
            **kwargs: Unused kwargs for compatibility
        """
        options = {**(extra_options_kwargs or {}), **kwargs}
        if grace_period_seconds:
            options["gracePeriodSeconds"] = grace_period_seconds
        if propagation_policy:
            options["PropagationPolicy"] = propagation_policy
        if dry_run:
            options["dryRun"] = dry_run
        if ignore_store_read_error:
            options["IgnoreStoreReadErrorWithClusterBreakingPotential"] = ignore_store_read_error
        serialized_options = serialize_to_go(options)

        resource_ptr = self._resource
        if namespace:
            resource_ptr = resource_ptr.Namespace(namespace)

        resource_ptr.Delete(name, serialized_options)

    @wrap_kube_error
    def delete_collection(  # noqa: PLR0917, PLR0913
        self,
        namespace: str | None = None,
        grace_period_seconds: int | None = None,
        propagation_policy: str | None = None,
        dry_run: list[str] | None = None,
        limit: int | None = None,
        resource_version: str | None = None,
        resource_version_match: str | None = None,
        label_selector: str | None = None,
        field_selector: str | None = None,
        timeout: int | None = None,
        ignore_store_read_error: bool | None = None,
        extra_delete_options_kwargs: dict[str, Any] | None = None,
        extra_list_options_kwargs: dict[str, Any] | None = None,
        **kwargs,
    ):
        """Delete a collection of objects from the cluster. The parameters map to both
        https://pkg.go.dev/k8s.io/apimachinery/pkg/apis/meta/v1#DeleteOptions and
         https://pkg.go.dev/k8s.io/apimachinery/pkg/apis/meta/v1#ListOptions

        Args:
            name (str): Name for the resource to delete.
            namespace (str | None, optional): Optional namespace for the resource. Defaults to None
            dry_run (list[str] | None, optional): Optional List of string dryrruns to use. Valid values can be gathered
                from the golang docs. Defaults to None.
            grace_period_seconds (int | None, optional): Optional time to wait for graceful termination before
                deleting the resource. Defaults to None.
            propagation_policy (str | None, optional): Optional DeletionPropagation decides how a deletion propagates
                to dependents of the object. See https://pkg.go.dev/k8s.io/apimachinery/pkg/apis/meta/v1#DeletionPropagation
                for more information. Defaults to None.
            ignore_store_read_error (bool | None, optional): Optional override to force successful deletion even
                if there is an etcd store error. Defaults to None.
            extra_delete_options_kwargs (dict[str, Any] | None, optional): Optional dictionary containing more
                DeleteOptions parameters. Defaults to None.
            resource_version (str | None, optional): Optional resourceVersion to fetch. Maps to the resourceVersion of
                the ObjectList object. Defaults to None.
            resource_version_match (str | None, optional): Optional regex string for filtering returned resources.
                Defaults to None.
            label_selector (str | None, optional): Optional label selector to filter returned resources.
                Defaults to None.
            field_selector (str | None, optional): Optional field selector to filter returned resources.
                Defaults to None.
            timeout (int | None, optional): Optional server timeout for the request. Defaults to None.
            limit (int | None, optional): Optional max number of resources returned. Defaults to None.
            extra_list_options_kwargs (dict[str, Any] | None, optional): Optional dictionary containing more ListOption
                parameters. Defaults to None.
            **kwargs: Unused kwargs for compatibility
        """
        delete_options = {**(extra_delete_options_kwargs or {}), **kwargs}
        if grace_period_seconds:
            delete_options["gracePeriodSeconds"] = grace_period_seconds
        if propagation_policy:
            delete_options["PropagationPolicy"] = propagation_policy
        if dry_run:
            delete_options["dryRun"] = dry_run
        if ignore_store_read_error:
            delete_options["IgnoreStoreReadErrorWithClusterBreakingPotential"] = ignore_store_read_error

        list_options = {**(extra_list_options_kwargs or {}), **kwargs}
        if resource_version:
            list_options["resourceVersion"] = resource_version
        if resource_version_match:
            list_options["resourceVersionMatch"] = resource_version_match
        if label_selector:
            list_options["labelSelector"] = label_selector
        if field_selector:
            list_options["fieldSelector"] = field_selector
        if timeout:
            list_options["timeoutSeconds"] = timeout
        if limit:
            list_options["Limit"] = limit
        serialized_del_options = serialize_to_go(delete_options)
        serialized_list_options = serialize_to_go(list_options)

        resource_ptr = self._resource
        if namespace:
            resource_ptr = resource_ptr.Namespace(namespace)
        resource_ptr.DeleteCollection(serialized_del_options, serialized_list_options)

    @wrap_kube_error
    def watch(  # noqa: PLR0917, PLR0913
        self,
        namespace: str | None = None,
        resource_version: str | None = None,
        resource_version_match: str | None = None,
        label_selector: str | None = None,
        field_selector: str | None = None,
        timeout: int | None = None,
        limit: int | None = None,
        continue_req: str | None = None,
        extra_options_kwargs: dict[str, Any] | None = None,
        watcher: Watch | None = None,
        **kwargs,
    ) -> Watch:
        """Watch for events from the cluster. The parameters map to https://pkg.go.dev/k8s.io/apimachinery/pkg/apis/meta/v1#WatchOptions

        Args:
            namespace (str | None, optional): Optional namespace for the resource. Defaults to None.
            resource_version (str | None, optional): Optional resourceVersion to fetch. Maps to the resourceVersion of
                the ObjectList object. Defaults to None.
            resource_version_match (str | None, optional): Optional regex string for filtering returned resources.
                Defaults to None.
            label_selector (str | None, optional): Optional label selector to filter returned resources.
                Defaults to None.
            field_selector (str | None, optional): Optional field selector to filter returned resources.
                Defaults to None.
            timeout (int | None, optional): Optional server timeout for the request. Defaults to None.
            limit (int | None, optional): Optional max number of resources returned. Defaults to None.
            continue_req (str | None, optional): Optional continue token to use to iterate over more results. Used with
                limit keywarg. Defaults to None.
            extra_options_kwargs (dict[str, Any] | None, optional): Optional dictionary containing more ListOption
                parameters. Defaults to None.
            subresources (list[str] | None, optional): Optional subresource of an object to get. Defaults to None.
            watcher (Watch | None, optional): Optional Watch object to use as the watcher interface. Users
                can use this to stop the event stream during or outside of iteration
            **kwargs: Unused kwargs for compatibility

        Returns:
            dict: The ObjectList object from the cluster as a dictionary e.g. use `.get("items")` to get list of
                resources
        """
        options = {**(extra_options_kwargs or {}), **kwargs}
        if resource_version:
            options["resourceVersion"] = resource_version
        if resource_version_match:
            options["resourceVersionMatch"] = resource_version_match
        if label_selector:
            options["labelSelector"] = label_selector
        if field_selector:
            options["fieldSelector"] = field_selector
        if timeout:
            options["timeoutSeconds"] = timeout
        if limit:
            options["Limit"] = limit
        if continue_req:
            options["continue"] = continue_req
        serialized_options = serialize_to_go(options)

        resource_ptr = self._resource
        if namespace:
            resource_ptr = resource_ptr.Namespace(namespace)

        if not watcher:
            watcher = Watch()

        interface = resource_ptr.Watch(serialized_options)
        watcher.interface = interface

        return watcher

    # ! Defined at bottom of class to avoid overriding built-in list
    @wrap_kube_error
    def list(  # noqa: PLR0917, PLR0913
        self,
        namespace: str | None = None,
        limit: int | None = None,
        resource_version: str | None = None,
        resource_version_match: str | None = None,
        label_selector: str | None = None,
        field_selector: str | None = None,
        timeout: int | None = None,
        continue_req: str | None = None,
        extra_options_kwargs: dict[str, Any] | None = None,
        **kwargs,
    ) -> dict:
        """List an object from the cluster. The parameters map to https://pkg.go.dev/k8s.io/apimachinery/pkg/apis/meta/v1#ListOptions

        Args:
            namespace (str | None, optional): Optional namespace for the resource. Defaults to None.
            resource_version (str | None, optional): Optional resourceVersion to fetch. Maps to the resourceVersion of
                the ObjectList object. Defaults to None.
            resource_version_match (str | None, optional): Optional regex string for filtering returned resources.
                Defaults to None.
            label_selector (str | None, optional): Optional label selector to filter returned resources.
                Defaults to None.
            field_selector (str | None, optional): Optional field selector to filter returned resources.
                Defaults to None.
            timeout (int | None, optional): Optional server timeout for the request. Defaults to None.
            limit (int | None, optional): Optional max number of resources returned. Defaults to None.
            continue_req (str | None, optional): Optional continue token to use to iterate over more results. Used with
                limit keywarg. Defaults to None.
            extra_options_kwargs (dict[str, Any] | None, optional): Optional dictionary containing more ListOption
                parameters. Defaults to None.
            subresources (list[str] | None, optional): Optional subresource of an object to get. Defaults to None.
            **kwargs: Unused kwargs for compatibility

        Returns:
            dict: The ObjectList object from the cluster as a dictionary e.g. use `.get("items")` to get list of
                resources
        """
        options = {
            **(extra_options_kwargs or {}),
            **kwargs,
        }
        if resource_version:
            options["resourceVersion"] = resource_version
        if resource_version_match:
            options["resourceVersionMatch"] = resource_version_match
        if label_selector:
            options["labelSelector"] = label_selector
        if field_selector:
            options["fieldSelector"] = field_selector
        if timeout:
            options["timeoutSeconds"] = timeout
        if limit:
            options["Limit"] = limit
        if continue_req:
            options["continue"] = continue_req
        serialized_options = serialize_to_go(options)

        resource_ptr = self._resource
        if namespace:
            resource_ptr = resource_ptr.Namespace(namespace)
        result = resource_ptr.List(serialized_options)
        return deserialize_from_go(result)
