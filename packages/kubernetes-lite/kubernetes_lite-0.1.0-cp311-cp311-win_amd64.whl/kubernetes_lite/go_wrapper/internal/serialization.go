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
	"encoding/json"
	//"github.com/bytedance/sonic"
	"k8s.io/apimachinery/pkg/apis/meta/v1/unstructured"
)

// Deserialize a bytes object into a generic unstructured Kubernetes object. Unstructured
// automatically handles setting the proper apiVersion/Kind parameters
func DeserializeJSONToUnstructured(jsonData []byte) (*unstructured.Unstructured, error) {
	u := &unstructured.Unstructured{}
	err := Unmarshal(jsonData, u)
	if err != nil {
		return nil, err
	}
	return u, nil
}

// Helper function to abstract all marshalling incase we switch serialization type or backend providers
func Marshal(obj interface{}) ([]byte, error) {
	return json.Marshal(obj)
}

// Similar to Marshal and is used as an abstraction incase we change serialization/backend providers
func Unmarshal(data []byte, structure interface{}) error {
	err := json.Unmarshal(data, structure)
	if err != nil {
		return err
	}
	return nil
}
