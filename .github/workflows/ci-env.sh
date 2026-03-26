#!/usr/bin/env bash

git config --global --add safe.directory /opt/regrid-wrapper/spack-stack

pushd /opt/regrid-wrapper/spack-stack
. setup.sh
spack env activate regrid-wrapper
popd

pushd $GITHUB_WORKSPACE
