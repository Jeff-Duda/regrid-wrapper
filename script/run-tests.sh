#!/usr/bin/env bash

set -e

cd ..

pytest src/test
mpirun -n 8 pytest -m "mpi" src/test
