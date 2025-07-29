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
	"fmt"

	"k8s.io/apimachinery/pkg/api/errors"
)

const KubernetesErrorSep = ":"
const KubernetesUnknownReasonConst = "Unknown"

// Wrap a kubernetes error into a known format that includes both the status reason
// and the message
func WrapKubernetesError(err error) error {
	if err == nil {
		return nil
	}
	reason := errors.ReasonForError(err)
	// If kubernetes returns no reason then use the unknown const
	if reason == "" {
		reason = KubernetesUnknownReasonConst
	}
	return fmt.Errorf("%s%s%s", reason, KubernetesErrorSep, err.Error())
}
