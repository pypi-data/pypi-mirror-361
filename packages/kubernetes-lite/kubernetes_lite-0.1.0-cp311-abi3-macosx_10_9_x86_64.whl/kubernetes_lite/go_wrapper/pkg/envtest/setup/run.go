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
	"fmt"
	"os"
	"runtime"

	pflag "github.com/spf13/pflag"
	"github.ibm.com/Michael-Honaker/kubernetes-lite/kubernetes_lite/go_wrapper/internal"
	"sigs.k8s.io/controller-runtime/tools/setup-envtest/remote"
)

// SetupEnvTestResult contains the various results from running the SetupEnvTest command
// includes stdout/stderr and the serialized error message
type SetupEnvTestResult struct {
	Stderr *string `json:"stderr,omitempty"`
	Stdout *string `json:"stdout,omitempty"`
	ErrMsg *string `json:"error,omitempty"`
}

// CreatePanicFlagSet creates a new flagset with all of the arguments of SetupEnvTest. this
// function is largely copied from the vendored main file
func createPanicFlagSet() *pflag.FlagSet {

	flag := pflag.NewFlagSet(os.Args[0], pflag.PanicOnError)

	//! This is copied from vendored_main... not the best solution but it works
	force = flag.Bool("force", false, "force re-downloading dependencies, even if they're already present and correct")
	installedOnly = flag.BoolP("installed-only", "i", os.Getenv(envNoDownload) != "",
		"only look at installed versions -- do not query the remote API server, "+
			"and error out if it would be necessary to")
	verify = flag.Bool("verify", true, "verify dependencies while downloading")
	useEnv = flag.Bool("use-env", os.Getenv(envUseEnv) != "", "whether to return the value of KUBEBUILDER_ASSETS if it's already set")
	targetOS = flag.String("os", runtime.GOOS, "os to download for (e.g. linux, darwin, for listing operations, use '*' to list all platforms)")
	targetArch = flag.String("arch", runtime.GOARCH, "architecture to download for (e.g. amd64, for listing operations, use '*' to list all platforms)")
	binDir = flag.String("bin-dir", "",
		"directory to store binary assets (default: $OS_SPECIFIC_DATA_DIR/envtest-binaries)")
	index = flag.String("index", remote.DefaultIndexURL, "index to discover envtest binaries")

	return flag
}

// runMain runs the vendored main function while capturing stdout and stderr. It
// also handles capturing panics and the corresponding error
func runMain() SetupEnvTestResult {
	result := SetupEnvTestResult{}

	var envTestStdErr string

	// Run main but capture both stdout and stderr
	envTestStdOut := withCapturedStream(&os.Stdout, func() {
		envTestStdErr = withCapturedStream(&os.Stderr, func() {
			// Capture Panics
			defer func() {
				if x := recover(); x != nil {
					resultString := fmt.Sprintf("%v", x)
					result.ErrMsg = &resultString
				}
			}()

			main()
		})
	})

	result.Stdout = &envTestStdOut
	result.Stderr = &envTestStdErr

	return result
}

// SetupEnvTest runs the vendored main file with the provided stdin_data and json arg data
func SetupEnvTest(stdin_data []byte, arg_data []byte) ([]byte, error) {
	// type cast the arguments to their correct client counterparts
	osArgs := []string{}
	err := internal.Unmarshal(arg_data, &osArgs)
	if err != nil {
		return nil, err
	}

	// Overwrite input args
	os.Args = osArgs

	// Reset the pflag command line before running anything
	pflag.CommandLine = createPanicFlagSet()

	// run the main function while wrapping stdin
	var result SetupEnvTestResult
	withOverriddenStream(&os.Stdin, stdin_data, func() {
		result = runMain()
	})

	return internal.Marshal(result)
}
