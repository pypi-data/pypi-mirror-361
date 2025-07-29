/* ----------------------------------------------------------------- *
 * (C) Copyright IBM Corporation 2024.                               *
 *                                                                   *
 * The source code for this program is not published or otherwise    *
 * divested of its trade secrets, irrespective of what has been      *
 * deposited with the U.S. Copyright Office.                         *
 * ----------------------------------------------------------------- */
// SPDX-License-Identifier: Apache-2.0

package client

import (
	"context"

	"github.ibm.com/Michael-Honaker/kubernetes-lite/kubernetes_lite/go_wrapper/internal"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/types"
	"k8s.io/client-go/dynamic"
)

// The WrappedResourceInterface is designed to mirror client-go's ResourceInterface with one major
// difference. Instead of accepting and returning pointers to the various apimachinery types/objects
// it handles everything though binary buffers (*uint16) pointers which greatly simplifies the CGO
// function call
type WrappedResourceInterface interface {
	Get(name string, opts []byte, subresources ...string) ([]byte, error)
	List(opts []byte) ([]byte, error)
	Create(obj []byte, opts []byte, subresources ...string) ([]byte, error)
	Update(obj []byte, opts []byte, subresources ...string) ([]byte, error)
	UpdateStatus(obj []byte, opts []byte) ([]byte, error)
	Patch(name string, pt string, data []byte, opts []byte, subresources ...string) ([]byte, error)
	Apply(name string, obj []byte, opts []byte, subresources ...string) ([]byte, error)
	ApplyStatus(name string, obj []byte, opts []byte) ([]byte, error)
	Watch(opts []byte) (WrappedWatchInterface, error)
	Delete(name string, opts []byte, subresources ...string) error
	DeleteCollection(opts []byte, listOptions []byte) error
}

type wrappedResourceInterfaceImpl struct {
	resource dynamic.ResourceInterface
}

// Get Request
func (w *wrappedResourceInterfaceImpl) Get(name string, opts []byte, subresources ...string) ([]byte, error) {
	// type cast the arguments to their correct client counterparts
	getOpts := metav1.GetOptions{}
	err := internal.Unmarshal(opts, &getOpts)
	if err != nil {
		return nil, err
	}

	// Get the object from the cluster
	getObj, err := w.resource.Get(context.Background(), name, getOpts, subresources...)
	if err != nil {
		return nil, internal.WrapKubernetesError(err)
	}

	// Serialize the object back to json
	serObj, err := internal.Marshal(getObj)
	if err != nil {
		return nil, err
	}
	return serObj, nil
}

// List Request
func (w *wrappedResourceInterfaceImpl) List(opts []byte) ([]byte, error) {
	// type cast the arguments to their correct client counterparts
	listOpts := metav1.ListOptions{}
	err := internal.Unmarshal(opts, &listOpts)
	if err != nil {
		return nil, err
	}

	// Get the objects from the cluster
	listObj, err := w.resource.List(context.Background(), listOpts)
	if err != nil {
		return nil, internal.WrapKubernetesError(err)
	}

	// Serialize the object back to json
	return internal.Marshal(listObj)
}

// Create Request
func (w *wrappedResourceInterfaceImpl) Create(obj []byte, opts []byte, subresources ...string) ([]byte, error) {
	parsedObj, err := internal.DeserializeJSONToUnstructured(obj)
	if err != nil {
		return nil, err
	}

	// type cast exported fields to their client counterparts
	createOpts := metav1.CreateOptions{}
	err = internal.Unmarshal(opts, &createOpts)
	if err != nil {
		return nil, err
	}

	updatedObj, err := w.resource.Create(context.Background(), parsedObj, createOpts, subresources...)
	if err != nil {
		return nil, internal.WrapKubernetesError(err)
	}
	return internal.Marshal(updatedObj)
}

// Update Request
func (w *wrappedResourceInterfaceImpl) Update(obj []byte, opts []byte, subresources ...string) ([]byte, error) {
	parsedObj, err := internal.DeserializeJSONToUnstructured(obj)
	if err != nil {
		return nil, err
	}

	// type cast exported fields to their client counterparts
	updateOpts := metav1.UpdateOptions{}
	err = internal.Unmarshal(opts, &updateOpts)
	if err != nil {
		return nil, err
	}

	updatedObj, err := w.resource.Update(context.Background(), parsedObj, updateOpts, subresources...)
	if err != nil {
		return nil, internal.WrapKubernetesError(err)
	}
	return internal.Marshal(updatedObj)
}

// UpdateStatus Request
func (w *wrappedResourceInterfaceImpl) UpdateStatus(obj []byte, opts []byte) ([]byte, error) {
	parsedObj, err := internal.DeserializeJSONToUnstructured(obj)
	if err != nil {
		return nil, err
	}

	// type cast exported fields to their client counterparts
	updateOpts := metav1.UpdateOptions{}
	err = internal.Unmarshal(opts, &updateOpts)
	if err != nil {
		return nil, err
	}

	updatedObj, err := w.resource.UpdateStatus(context.Background(), parsedObj, updateOpts)
	if err != nil {
		return nil, internal.WrapKubernetesError(err)
	}
	return internal.Marshal(updatedObj)
}

// Patch Request
func (w *wrappedResourceInterfaceImpl) Patch(name string, pt string, data []byte, opts []byte, subresources ...string) ([]byte, error) {
	// type cast exported fields to their client counterparts
	parsedPatchType := types.PatchType(pt)
	patchOpts := metav1.PatchOptions{}
	err := internal.Unmarshal(opts, &patchOpts)
	if err != nil {
		return nil, err
	}

	updatedObj, err := w.resource.Patch(context.Background(), name, parsedPatchType, data, patchOpts, subresources...)
	if err != nil {
		return nil, internal.WrapKubernetesError(err)
	}
	return internal.Marshal(updatedObj)
}

// Apply Request
func (w *wrappedResourceInterfaceImpl) Apply(name string, obj []byte, opts []byte, subresources ...string) ([]byte, error) {
	parsedObj, err := internal.DeserializeJSONToUnstructured(obj)
	if err != nil {
		return nil, err
	}

	// type cast exported fields to their client counterparts
	applyOpts := metav1.ApplyOptions{}
	err = internal.Unmarshal(opts, &applyOpts)
	if err != nil {
		return nil, err
	}

	updatedObj, err := w.resource.Apply(context.Background(), name, parsedObj, applyOpts, subresources...)
	if err != nil {
		return nil, internal.WrapKubernetesError(err)
	}
	return internal.Marshal(updatedObj)
}

// ApplyStatus Request
func (w *wrappedResourceInterfaceImpl) ApplyStatus(name string, obj []byte, opts []byte) ([]byte, error) {
	parsedObj, err := internal.DeserializeJSONToUnstructured(obj)
	if err != nil {
		return nil, err
	}

	// type cast exported fields to their client counterparts
	applyOpts := metav1.ApplyOptions{}
	err = internal.Unmarshal(opts, &applyOpts)
	if err != nil {
		return nil, err
	}

	updatedObj, err := w.resource.ApplyStatus(context.Background(), name, parsedObj, applyOpts)
	if err != nil {
		return nil, internal.WrapKubernetesError(err)
	}
	return internal.Marshal(updatedObj)
}

// Watch Request returns a WrappedWatchInterface interface for iterating events
func (w *wrappedResourceInterfaceImpl) Watch(opts []byte) (WrappedWatchInterface, error) {
	// type cast exported fields to their client counterparts
	listOpts := metav1.ListOptions{}
	err := internal.Unmarshal(opts, &listOpts)
	if err != nil {
		return nil, err
	}

	watchInterface, err := w.resource.Watch(context.Background(), listOpts)
	if err != nil {
		return nil, internal.WrapKubernetesError(err)
	}
	return NewWrappedWatchInterface(watchInterface), nil
}

// Delete Request
func (w *wrappedResourceInterfaceImpl) Delete(name string, opts []byte, subresources ...string) error {
	// type cast exported fields to their client counterparts
	deleteOpts := metav1.DeleteOptions{}
	err := internal.Unmarshal(opts, &deleteOpts)
	if err != nil {
		return err
	}

	err = w.resource.Delete(context.Background(), name, deleteOpts, subresources...)
	return internal.WrapKubernetesError(err)
}

// Delete Collection Request
func (w *wrappedResourceInterfaceImpl) DeleteCollection(suppliedDelOpts []byte, suppliedListOpts []byte) error {
	// type cast exported fields to their client counterparts
	deleteOpts := metav1.DeleteOptions{}
	err := internal.Unmarshal(suppliedDelOpts, &deleteOpts)
	if err != nil {
		return err
	}
	listOpts := metav1.ListOptions{}
	err = internal.Unmarshal(suppliedListOpts, &listOpts)
	if err != nil {
		return err
	}

	err = w.resource.DeleteCollection(context.Background(), deleteOpts, listOpts)
	return internal.WrapKubernetesError(err)

}
