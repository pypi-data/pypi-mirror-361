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
	"time"

	"github.ibm.com/Michael-Honaker/kubernetes-lite/kubernetes_lite/go_wrapper/internal"

	// Import all Kubernetes client auth plugins (e.g. Azure, GCP, OIDC, etc.)
	// to ensure that exec-entrypoint and run can make use of them.
	"k8s.io/client-go/discovery"
	"k8s.io/client-go/discovery/cached/memory"
	_ "k8s.io/client-go/plugin/pkg/client/auth"
	"k8s.io/client-go/restmapper"

	"k8s.io/client-go/rest"

	"k8s.io/apimachinery/pkg/api/meta"
	"k8s.io/apimachinery/pkg/runtime/schema"
	"k8s.io/client-go/dynamic"
	"sigs.k8s.io/controller-runtime/pkg/client/config"
)

// Simple dynamic client interface that allows users to create a Resource Interface
type WrappedDynamicClient interface {
	Resource(apiVersion string, kind string) (WrappedNamespaceableResourceInterface, error)
}

// Internal struct for implementing the WrappedDynamicClient interface
type wrappedDynamicClientImpl struct {
	client *dynamic.DynamicClient
	mapper meta.RESTMapper
	cache  discovery.CachedDiscoveryInterface
}

// Constructor which returns the internal struct object. Automatically
// handles loading from kubeconfig/in-cluster
func NewWrappedDynamicClient(qps float32, burst int, timeout string) (WrappedDynamicClient, error) {
	// Get the current kube config objects. This checks the os env,
	// and local KubeConfig files for first match
	cfg, err := config.GetConfig()
	if err != nil {
		return nil, internal.WrapKubernetesError(err)
	}
	return newWrappedDynamicClientFromRest(cfg, qps, burst, timeout)
}

// Constructor which returns the internal struct object. Expects user to provide
// a valid KubeConfig in raw bytes
func NewWrappedDynamicClientWithConfig(config []byte, qps float32, burst int, timeout string) (WrappedDynamicClient, error) {
	// Get the current kube config objects from the provided config
	cfg, err := internal.GenerateRestFromKubeConfig(config)
	if err != nil {
		return nil, internal.WrapKubernetesError(err)
	}
	return newWrappedDynamicClientFromRest(cfg, qps, burst, timeout)
}

// Helper function to construct a wrapper client from a given rest config and options
func newWrappedDynamicClientFromRest(cfg *rest.Config, qps float32, burst int, timeout string) (WrappedDynamicClient, error) {
	// Configure timeout
	if timeout != "" {
		timeoutDuration, err := time.ParseDuration(timeout)
		if err != nil {
			return nil, internal.WrapKubernetesError(err)
		}
		cfg.Timeout = timeoutDuration
	}

	// Setup ratelimiting
	cfg.QPS = qps
	cfg.Burst = burst

	// Construct the new dynamic client
	cli, err := dynamic.NewForConfig(cfg)
	if err != nil {
		return nil, internal.WrapKubernetesError(err)
	}

	// From the dynamic client construct a REST mapper using a local memory cache
	disc_cli, err := discovery.NewDiscoveryClientForConfig(cfg)
	if err != nil {
		return nil, internal.WrapKubernetesError(err)
	}
	disc_cache := memory.NewMemCacheClient(disc_cli)
	mapper := restmapper.NewDeferredDiscoveryRESTMapper(disc_cache)

	return &wrappedDynamicClientImpl{cache: disc_cache, client: cli, mapper: mapper}, nil
}

// Construct a dynamic resource  from the apiVersion and kind. This function handles getting the correct
// GVR and rest mapping
func (w *wrappedDynamicClientImpl) Resource(apiVersion string, kind string) (WrappedNamespaceableResourceInterface, error) {
	return w.internalResource(apiVersion, kind, true)
}

// Internal helper for getting a resource. Handles cache invalidation on kind miss
func (w *wrappedDynamicClientImpl) internalResource(apiVersion string, kind string, retry_missing bool) (WrappedNamespaceableResourceInterface, error) {
	// Attempt to singularlize the kind
	kind, err := w.mapper.ResourceSingularizer(kind)
	if err != nil {
		// Ignore NoResourceMatchError errors and try the kind as is
		_, ok := err.(*meta.NoResourceMatchError)
		if !ok {
			return nil, internal.WrapKubernetesError(err)
		}
	}

	// Get the GVK Schema for a given apiVersion/kind
	gv, err := schema.ParseGroupVersion(apiVersion)
	if err != nil {
		return nil, internal.WrapKubernetesError(err)
	}
	gvk := gv.WithKind(kind)

	// Use the rest mapper to fill in the remaining GVR
	mapping, err := w.mapper.RESTMapping(gvk.GroupKind(), gvk.Version)
	if err != nil {
		// If no match then attempt to invalidate the cache and retry
		if meta.IsNoMatchError(err) && retry_missing {
			w.cache.Invalidate()
			return w.internalResource(apiVersion, kind, false)
		}
		return nil, internal.WrapKubernetesError(err)
	}

	dynamicResource := w.client.Resource(mapping.Resource)
	wrappedInterface := wrappedResourceInterfaceImpl{resource: dynamicResource}
	return &wrappedNamespaceableResourceInterface{wrappedResourceInterfaceImpl: wrappedInterface, resource: dynamicResource}, nil
}
