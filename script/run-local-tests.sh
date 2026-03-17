#!/usr/bin/env bash

set -e

cd ..

pytest -vs src/test
mpirun -n 8 pytest -vs -m "mpi and not integration" src/test
