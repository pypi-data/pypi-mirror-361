from __future__ import annotations

import platform
import sys
import os

from setuptools import Extension
from setuptools import setup

if sys.platform != 'win32' and platform.python_implementation() == 'CPython':
    try:
        import wheel.bdist_wheel
    except ImportError:
        cmdclass = {}
    else:
        class bdist_wheel(wheel.bdist_wheel.bdist_wheel):
            def finalize_options(self) -> None:
                self.py_limited_api = f'cp3{sys.version_info[1]}'
                super().finalize_options()

        cmdclass = {'bdist_wheel': bdist_wheel}
else:
    cmdclass = {}


os.environ["CGO_CFLAGS_ALLOW"]="-O.*"

setup(
    ext_modules=[
        Extension(
            'kubernetes_lite.wrapper._wrapper', ['kubernetes_lite/wrapper/wrapper.go'],
            py_limited_api=True,
        ),
    ],
    cmdclass=cmdclass,
    build_golang={'root': 'github.ibm.com/Michael-Honaker/kubernetes-lite/kubernetes_lite'},
)