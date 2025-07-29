/* ----------------------------------------------------------------- *
 * (C) Copyright IBM Corporation 2024.                               *
 *                                                                   *
 * The source code for this program is not published or otherwise    *
 * divested of its trade secrets, irrespective of what has been      *
 * deposited with the U.S. Copyright Office.                         *
 * ----------------------------------------------------------------- */
// SPDX-License-Identifier: Apache-2.0
package server

import (
	"errors"

	"github.ibm.com/Michael-Honaker/kubernetes-lite/kubernetes_lite/go_wrapper/internal"
	"k8s.io/client-go/rest"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/envtest"
	"sigs.k8s.io/controller-runtime/pkg/log/zap"
)

// Default settings for the kube config
const (
	DefaultContextName string = "default-context"
	DefaultNamespace   string = "default"
)

// EnvTestEnvironment defines the interface for starting and stopping an EnvTest server as well as
// fetching a generic kube config
type EnvTestEnvironment interface {
	Start() ([]byte, error)
	Stop() error
	GetKubeConfig() ([]byte, error)
}

// envTestEnvironmentImpl implements the EnvTestEnvironment
type envTestEnvironmentImpl struct {
	Env    *envtest.Environment
	Config *rest.Config
}

// Start an EnvTest server. Can only be ran once per instance
func (e *envTestEnvironmentImpl) Start() ([]byte, error) {
	// Configure the global logger
	opts := zap.Options{
		Development: true,
	}
	ctrl.SetLogger(zap.New(zap.UseFlagOptions(&opts)))

	cfg, err := e.Env.Start()
	if err != nil {
		return nil, err
	}

	e.Config = cfg
	res, err := internal.GenerateKubeConfigFromRest(e.Config, DefaultNamespace, DefaultContextName)
	return res, err
}

// Stop the envtest instance. Should only be ran once per instance
func (e *envTestEnvironmentImpl) Stop() error {
	err := e.Env.Stop()
	if err != nil {
		return err
	}
	return nil
}

// GetKubeConfig returns the raw kubeconfig with admin access. Can be ran multiple timess
func (e *envTestEnvironmentImpl) GetKubeConfig() ([]byte, error) {
	if e.Config == nil {
		return nil, errors.New("must call Start before running GetKubeConfig")
	}
	return internal.GenerateKubeConfigFromRest(e.Config, DefaultNamespace, DefaultContextName)
}

// Construct a EnvTest environment loading the path from the default locations
func NewEnvTestEnvironment() (EnvTestEnvironment, error) {
	return NewEnvTestEnvironmentWithPath("")
}

// Construct a EnvTest environment with the path to the kubebuilder assets
func NewEnvTestEnvironmentWithPath(path string) (EnvTestEnvironment, error) {
	testEnv := &envtest.Environment{
		ErrorIfCRDPathMissing: false,
		BinaryAssetsDirectory: path,
	}
	env := &envTestEnvironmentImpl{Env: testEnv, Config: nil}
	return env, nil
}
