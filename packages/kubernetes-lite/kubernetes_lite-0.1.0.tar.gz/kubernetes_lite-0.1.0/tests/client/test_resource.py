# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
"""This module contains tests for the various resource operations"""

# Assisted by watsonx Code Assistant
import copy

from kubernetes_lite.client import DynamicResource
from kubernetes_lite.errors import ConflictError, NotFoundError
from tests.utils import (
    check_object_status,
    generate_test_object,
    validate_result,
)

import pytest


def test_create(resource_namespace: tuple[DynamicResource, str]):
    """Test that the client can create objects"""
    deployment_res, namespace = resource_namespace
    obj = generate_test_object(namespace)

    deployment_res.create(obj)

    check_object_status(deployment_res, expected_obj=obj)


def test_update(resource_namespace: tuple[DynamicResource, str]):
    """Test that the client can update objects"""
    deployment_res, namespace = resource_namespace
    org_obj = generate_test_object(namespace)

    # Ensure we get a NotFoundError if we update a nonexistent resource
    with pytest.raises(NotFoundError):
        deployment_res.update(org_obj)

    # Create initial resource before updating
    deployment_res.create(org_obj)

    updated_obj = copy.deepcopy(org_obj)
    updated_obj["metadata"]["labels"]["new-label"] = "test"

    deployment_res.update(updated_obj)

    check_object_status(deployment_res, expected_obj=updated_obj)


def test_update_status(resource_namespace: tuple[DynamicResource, str]):
    """Test that the client can update the status of objects"""
    deployment_res, namespace = resource_namespace
    obj = generate_test_object(namespace)

    current_obj = deployment_res.create(obj)
    assert not current_obj["status"].get("availableReplicas")

    current_obj["status"]["replicas"] = 1
    deployment_res.update_status(current_obj)

    check_object_status(deployment_res, expected_obj=current_obj)


def test_patch(resource_namespace: tuple[DynamicResource, str]):
    """Test that the client can patch objects with merge"""
    deployment_res, namespace = resource_namespace
    obj = generate_test_object(namespace)

    current_obj = deployment_res.create(obj)
    assert current_obj["spec"].get("replicas") == 3

    patch = {"spec": {"replicas": 1}}
    deployment_res.patch(
        patch_type="application/strategic-merge-patch+json",
        patch_data=patch,
        name=current_obj.get("metadata").get("name"),
        namespace=namespace,
    )

    current_obj["spec"]["replicas"] = 1
    check_object_status(deployment_res, expected_obj=current_obj)


def test_apply(resource_namespace: tuple[DynamicResource, str]):
    """Test that the client can apply objects"""
    deploy_res, namespace = resource_namespace
    obj = generate_test_object(namespace)

    check_object_status(deploy_res, namespace, exists=False)

    deploy_res.apply(obj, field_manager="test")
    check_object_status(deploy_res, expected_obj=obj)

    obj["spec"]["replicas"] = 2
    deploy_res.apply(obj, field_manager="test")
    check_object_status(deploy_res, expected_obj=obj)

    obj["spec"]["replicas"] = 3
    with pytest.raises(ConflictError):
        deploy_res.apply(obj, field_manager="other")
    deploy_res.apply(obj, field_manager="other", force=True)
    check_object_status(deploy_res, expected_obj=obj)


def test_apply_status(resource_namespace: tuple[DynamicResource, str]):
    """Test that the client can apply the status of objects"""
    deployment_res, namespace = resource_namespace
    obj = generate_test_object(namespace)

    current_obj = deployment_res.create(obj)
    assert not current_obj["status"].get("replicas")

    obj["status"] = {}
    obj["status"]["replicas"] = 1
    deployment_res.apply_status(obj, field_manager="test", force=True)

    check_object_status(deployment_res, expected_obj=obj)


def test_delete(resource_namespace: tuple[DynamicResource, str]):
    """Test that the client can delete objects"""
    deployment_resource, namespace = resource_namespace
    obj = generate_test_object(namespace)
    obj_metadata = obj.get("metadata")

    with pytest.raises(NotFoundError):
        deployment_resource.delete(obj_metadata.get("name"), obj_metadata.get("namespace"))

    # Create before attempting to delete for real
    deployment_resource.create(obj)

    deployment_resource.delete(obj_metadata.get("name"), obj_metadata.get("namespace"))
    check_object_status(deployment_resource, namespace, exists=False)


def test_delete_collection(resource_namespace: tuple[DynamicResource, str]):
    """Test that the client can delete a list of objects"""
    deployment_resource, namespace = resource_namespace

    # Assert that we can delete a collection with no objects
    deployment_resource.delete_collection(namespace=namespace)

    # Create before attempting to delete for real
    obj_1 = generate_test_object(namespace, name="test-1")
    obj_2 = generate_test_object(namespace, name="test-2")
    deployment_resource.create(obj_1)
    deployment_resource.create(obj_2)

    check_object_status(deployment_resource, namespace, name="test-1", exists=True)
    check_object_status(deployment_resource, namespace, name="test-2", exists=True)

    deployment_resource.delete_collection(namespace=namespace)
    check_object_status(deployment_resource, namespace, name="test-1", exists=False)
    check_object_status(deployment_resource, namespace, name="test-2", exists=False)


def test_list(resource_namespace: tuple[DynamicResource, str]):
    """Test that the client can list objects"""
    deployment_resource, namespace = resource_namespace

    # With no objects assert list returns empty
    empty_list_resp = deployment_resource.list(namespace=namespace)
    assert empty_list_resp
    assert empty_list_resp.get("items") == []

    obj_1 = generate_test_object(namespace, name="test-1")
    obj_2 = generate_test_object(namespace, name="test-2")
    deployment_resource.create(obj_1)
    deployment_resource.create(obj_2)

    list_resp = deployment_resource.list(namespace=namespace)
    assert list_resp
    assert len(list_resp.get("items")) == 2
    validate_result(list_resp.get("items")[0], obj_1)
    validate_result(list_resp.get("items")[1], obj_2)
