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
	"errors"

	"github.ibm.com/Michael-Honaker/kubernetes-lite/kubernetes_lite/go_wrapper/internal"

	// Import all Kubernetes client auth plugins (e.g. Azure, GCP, OIDC, etc.)
	// to ensure that exec-entrypoint and run can make use of them.
	"k8s.io/apimachinery/pkg/watch"
)

var EmptyEvent = watch.Event{}

// WrappedWatchInterface allows CGO applications to iterate over a channel
type WrappedWatchInterface interface {
	Stop()
	Next() ([]byte, error)
}

// Implementation of the WrappedWatchInterface
type wrappedWatchInterfaceImpl struct {
	Watcher     watch.Interface
	eventStream <-chan watch.Event
}

// Construct a new WrappedWatchInterface from a client-go watch interface
func NewWrappedWatchInterface(watcher watch.Interface) WrappedWatchInterface {
	stream := watcher.ResultChan()
	return wrappedWatchInterfaceImpl{
		Watcher:     watcher,
		eventStream: stream,
	}
}

// Stop the underlying watcher
func (w wrappedWatchInterfaceImpl) Stop() {
	w.Watcher.Stop()
}

// Get the next event from the underlying watcher
func (w wrappedWatchInterfaceImpl) Next() ([]byte, error) {
	v := <-w.eventStream
	if v == EmptyEvent {
		return nil, errors.New("stop iteration")
	}
	return internal.Marshal(v)

}
