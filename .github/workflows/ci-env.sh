#!/usr/bin/env bash

pushd /opt/regrid-wrapper/spack-stack
. setup.sh
spack env activate regrid-wrapper
popd

pushd $GITHUB_WORKSPACE
