/* ----------------------------------------------------------------- *
 * (C) Copyright IBM Corporation 2024.                               *
 *                                                                   *
 * The source code for this program is not published or otherwise    *
 * divested of its trade secrets, irrespective of what has been      *
 * deposited with the U.S. Copyright Office.                         *
 * ----------------------------------------------------------------- */
// SPDX-License-Identifier: Apache-2.0
package setup

import (
	"bytes"
	"io"
	"os"
)

// withCapturedStream is a helper function to capture the output of a os.File and return it as
// a string
func withCapturedStream(stream **os.File, fn func()) string {
	// Replace stream with local pipe
	oldStream := *stream
	r, w, _ := os.Pipe()
	*stream = w

	// Make capture channel
	outChan := make(chan string)
	// copy the output in a separate goroutine so printing can't block indefinitely
	go func() {
		var buf bytes.Buffer
		io.Copy(&buf, r)
		stringRes := buf.String()
		outChan <- stringRes
	}()

	fn()

	// Close the writing pipe so the buffer reader knows to stop
	w.Close()
	*stream = oldStream // restoring the stream

	// Gather the stdout result
	localChanOut := <-outChan
	return localChanOut
}

// withOverriddenStream is similar to withOverriddenStream but it overwrites a reading stream
// with some binary data
func withOverriddenStream(stream **os.File, overwritten_data []byte, fn func()) {
	// Replace stream with local pipe
	oldStream := *stream
	r, w, _ := os.Pipe()
	*stream = r

	// copy the overwritten data in a separate goroutine so the pipe can't block indefinitely
	go func() {
		buf := bytes.NewBuffer(overwritten_data)
		io.Copy(w, buf)
	}()

	fn()

	// Close the writing pipe so the buffer reader knows to stop
	w.Close()
	*stream = oldStream // restoring the stream
}
