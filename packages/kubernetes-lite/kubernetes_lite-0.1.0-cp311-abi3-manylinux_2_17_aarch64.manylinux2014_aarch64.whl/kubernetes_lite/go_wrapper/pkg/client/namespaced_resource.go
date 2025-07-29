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
	"k8s.io/client-go/dynamic"
)

// WrappedNamespaceableResourceInterface is a wrapper around the ResourceInterface for interacting with
// cluster wide resources. This interface can also be namespace scoped with the Namespace method.
type WrappedNamespaceableResourceInterface interface {
	Namespace(string) WrappedResourceInterface
	WrappedResourceInterface
}

// Implementation of the WrappedNamespaceableResourceInterface
type wrappedNamespaceableResourceInterface struct {
	wrappedResourceInterfaceImpl
	resource dynamic.NamespaceableResourceInterface
}

// Returns a namespace specific resource handler
func (w wrappedNamespaceableResourceInterface) Namespace(namespace string) WrappedResourceInterface {
	return &wrappedResourceInterfaceImpl{resource: w.resource.Namespace(namespace)}
}
