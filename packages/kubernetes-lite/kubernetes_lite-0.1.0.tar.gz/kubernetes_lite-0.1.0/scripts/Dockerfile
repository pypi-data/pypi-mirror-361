# ***************************************************************** #
# (C) Copyright IBM Corporation 2024.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #
# SPDX-License-Identifier: Apache-2.0

ARG BUILD_LAYER=local

FROM registry.access.redhat.com/ubi9/python-311 as base

# Make base user non root
USER default

FROM base as build

WORKDIR /opt/build
# REquire root for all build permissions
USER 0

# Install go and other system dependencies
COPY --chown=0:0 scripts/*.py scripts/
RUN python3 -m scripts.install_build_reqs > build.env

# Copy over buld files
COPY  --chown=0:0 setup.py setup.py
COPY  --chown=0:0 README.md README.md
COPY  --chown=0:0 LICENSE LICENSE
COPY  --chown=0:0 pyproject.toml pyproject.toml
COPY  --chown=0:0 kubernetes_lite kubernetes_lite

# Run the build and install the wheel
RUN source "/opt/build/build.env" && pip3 install build && python3 -m build && pip3 install dist/*.whl


FROM base as test

# Copy over the wheel and install test dependencies
USER default
COPY --chown=default:default --from=build /opt/build/dist/*.whl /opt/dist/
RUN pip3 install $(ls /opt/dist/*.whl)[test]

# Copy over the tests themselves
COPY --chown=default:default tests tests

FROM base as release

USER default

COPY --from=build --chown=default:default /opt/build/dist/*.whl /opt/dist/

RUN pip3 install /opt/dist/*