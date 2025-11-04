#!/bin/bash

set -eu

module purge

export REGRID_WRAPPER_LOG_DIR=$(readlink -f .)

module use modulefiles
module load regrid-wrapper-spack-stack
module load py-mpi4py py-netcdf4 py-pytest
module list

cd ${REGRID_WRAPPER_ROOT_DIR}  # Path to the cloned directory of regrid-wrapper
srun --account epic --nodes 1 --tasks 1 --time 00:01:00 pytest -vs src/test
srun --account epic --nodes 1 --tasks 8 --time 00:01:00 pytest -vs -m "mpi" src/test
