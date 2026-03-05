#!/bin/bash

# git pull && bash run-tests.sh 2>&1 | tee out.run-tests.sh

set -eu

module purge

export REGRID_WRAPPER_LOG_DIR=$(readlink -f .)

module use modulefiles
module load regrid-wrapper-spack-stack
#module load py-mpi4py py-netcdf4 py-pytest
#module load py-mpi4py py-pytest py-xarray
#module load py-pytest
module list
export PYTHONPATH=/scratch3/NCEPDEV/stmp/Benjamin.Koziol/sandbox/git-benkozi/regrid-wrapper/src:${PYTHONPATH:-}

#cd /scratch3/NCEPDEV/stmp/Benjamin.Koziol/sandbox/git-benkozi/regrid-wrapper/platform/ursa  # Path to the cloned directory of regrid-wrapper
#srun --account epic --nodes 1 --tasks 2 --time 00:01:00 python test_mpi4py.py

cd /scratch3/NCEPDEV/stmp/Benjamin.Koziol/sandbox/git-benkozi/regrid-wrapper  # Path to the cloned directory of regrid-wrapper
srun --account epic --nodes 1 --tasks 1 --time 00:01:00 pytest -vs src/test
srun --account epic --nodes 1 --tasks 8 --time 00:01:00 pytest -vs -m "mpi" src/test
#srun --account epic --nodes 1 --tasks 8 --time 00:01:00 pytest -vs -m "mpi" src/test/test_esmpy/test_field_wrapper.py::TestGridWrapper::test_fill_nc_variables
