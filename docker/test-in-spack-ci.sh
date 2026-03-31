#!/usr/bin/env bash

set -eu

cd /opt/regrid-wrapper/spack-stack
. setup.sh
spack env activate regrid-wrapper

cd /opt/project
export PYTHONPATH=/opt/project/src

pre-commit run --all
pytest -v src
mpirun -n 8 pytest -v -m "mpi and not integration" src/test
