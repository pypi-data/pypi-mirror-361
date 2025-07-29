/* ----------------------------------------------------------------- *
 * (C) Copyright IBM Corporation 2024.                               *
 *                                                                   *
 * The source code for this program is not published or otherwise    *
 * divested of its trade secrets, irrespective of what has been      *
 * deposited with the U.S. Copyright Office.                         *
 * ----------------------------------------------------------------- */
// SPDX-License-Identifier: Apache-2.0
package internal

import (
	"k8s.io/client-go/rest"
	"k8s.io/client-go/tools/clientcmd"
	clientcmdapi "k8s.io/client-go/tools/clientcmd/api/v1"
)

// GenerateKubeConfigFromRest generates a valid kube config json from an active rest config
func GenerateKubeConfigFromRest(config *rest.Config, namespace string, contextName string) ([]byte, error) {
	clusters := []clientcmdapi.NamedCluster{
		{
			Cluster: clientcmdapi.Cluster{
				Server:                   config.Host,
				CertificateAuthorityData: config.TLSClientConfig.CAData,
			},
			Name: contextName,
		},
	}
	contexts := []clientcmdapi.NamedContext{
		{
			Context: clientcmdapi.Context{
				Cluster:   contextName,
				Namespace: namespace,
				AuthInfo:  contextName,
			},
			Name: contextName,
		},
	}
	authinfos := []clientcmdapi.NamedAuthInfo{
		{
			AuthInfo: clientcmdapi.AuthInfo{
				Username:              config.Username,
				Password:              config.Password,
				ClientCertificateData: config.CertData,
				ClientKeyData:         config.KeyData,
				Token:                 config.BearerToken,
			},
			Name: contextName,
		},
	}

	clientConfig := clientcmdapi.Config{
		Kind:           "Config",
		APIVersion:     "v1",
		Clusters:       clusters,
		Contexts:       contexts,
		CurrentContext: contextName,
		AuthInfos:      authinfos,
	}

	return Marshal(clientConfig)
}

// GenerateRestFromKubeConfig creates a rest Config object from the raw json of a
// kube config
func GenerateRestFromKubeConfig(rawConfig []byte) (*rest.Config, error) {
	clientConfig, err := clientcmd.NewClientConfigFromBytes(rawConfig)
	if err != nil {
		return nil, err
	}

	return clientConfig.ClientConfig()
}
