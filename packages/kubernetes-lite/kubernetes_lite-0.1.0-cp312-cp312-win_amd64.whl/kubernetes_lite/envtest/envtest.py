# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0
"""This module contains the implementation fo the pythonic wrapper around
https://pkg.go.dev/sigs.k8s.io/controller-runtime/pkg/envtest
"""

import atexit
from functools import cached_property
from io import BytesIO
from logging import Logger, getLogger
from threading import Event

from kubernetes_lite.client import DynamicClient
from kubernetes_lite.setup_envtest import internal_run_setup_envtest_command
from kubernetes_lite.wrapper.server import EnvTestEnvironment, NewEnvTestEnvironment, NewEnvTestEnvironmentWithPath


class EnvTest:
    """EnvTest is a wrapper around the golang EnvTest object provided by
    https://pkg.go.dev/sigs.k8s.io/controller-runtime/pkg/envtest. This class
    exposes methods to start and stop the server as well as fetch a raw kubeconfig
    or client object. This class can also handle calling setup-envtest to download
    the required binaries and create the path.

    To configure the underyling golang EnvTestEnvironment checkout the environmental variables
    exposed by EnvTest: https://book.kubebuilder.io/reference/envtest.html#environment-variables
    """

    def __init__(self, log: Logger | None = None):
        """Initialize the EnvTest object and create an event to ensure the server isn't
        shutdown multiple times

        Arguments:
            log (logger | None): Optional logger to provide. Defaults to None
        """
        self._log = log if log else getLogger("envtest")
        self._env: EnvTestEnvironment | None = None
        self._stop_event = Event()

    @cached_property
    def env(self) -> EnvTestEnvironment:
        """Return the underlying golang EnvTestEnvironment object. Must be called
        after starting the server

        Returns:
            EnvTestEnvironment: The underlying golang object for this instance
        """
        if not self._env:
            raise RuntimeError("Must start environment before accessing it")
        return self._env

    def start(self, auto_setup: bool = True) -> BytesIO:
        """Construct and start the EnvTestEnvironment object. Can optionally run setupenv-test
        to download the correct kube bins.

        Args:
            auto_setup (bool, optional): If setup-envtest should be ran to fetch the local
                path. Defaults to True.

        Returns:
            BytesIO: A raw kube_config for interacting with the cluster.
        """
        path = None
        if auto_setup:
            result = internal_run_setup_envtest_command("use", "-p", "path")
            result.log_and_raise(self._log, raise_exc=True)
            path = result.stdout

        if path:
            self._env = NewEnvTestEnvironmentWithPath(path)
        else:
            self._env = NewEnvTestEnvironment()

        self.env.Start()
        atexit.register(self.stop)

        return self.config()

    def stop(self):
        """Stop the envtest server if it hasn't already been stopped"""
        if self._stop_event.is_set():
            return

        self.env.Stop()
        self._stop_event.set()

    def config(self) -> BytesIO:
        """Fetch a kubeconfig object for the given EnvTest server. Must be called
        after start()

        Returns:
            BytesIO: The raw byte stream of the kube object
        """
        return BytesIO(bytes(self.env.GetKubeConfig()))

    def client(self) -> DynamicClient:
        """Fetch a dynamic client object for interacting with the EnvTest server. Must be called
        after start()

        Returns:
            DynamicClient: A client to interact with the server
        """
        return DynamicClient(self.config())
