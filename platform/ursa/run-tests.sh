#!/bin/bash

# git pull && time bash run-tests.sh 2>&1 | tee out.run-tests.sh

set -eux

#platform=ursa
platform=gaeac6

# --------------------------------------------------------------------------------------------------

if [[ ${platform} = "gaeac6" ]]; then
  rw_dir=/gpfs/f6/bil-fire8/scratch/Benjamin.Koziol/sandbox/git-benkozi
  account="bil-fire8"
  cluster="--clusters=c6"
  partition=" --partition=batch"
elif [[ ${platform} = "ursa" ]]; then
  rw_dir=/scratch3/NCEPDEV/stmp/Benjamin.Koziol/sandbox/git-benkozi
  account="epic"
  cluster=""
  partition=""
else
  echo "platform not supported"
  exit 1
fi

# --------------------------------------------------------------------------------------------------

module purge

export REGRID_WRAPPER_LOG_DIR=$(readlink -f .)

module use modulefiles
module load regrid-wrapper-spack-stack.${platform}
#module load regrid-wrapper-spack-stack-2_1
#module load py-mpi4py py-netcdf4 py-pytest
#module load py-mpi4py py-pytest py-xarray
#module load py-pytest
module list
export PYTHONPATH=${rw_dir}/regrid-wrapper/src:${PYTHONPATH:-}

#cd /scratch3/NCEPDEV/stmp/Benjamin.Koziol/sandbox/git-benkozi/regrid-wrapper/platform/ursa  # Path to the cloned directory of regrid-wrapper
#srun --account epic --nodes 1 --tasks 2 --time 00:01:00 python test_mpi4py.py

cd ${rw_dir}/regrid-wrapper  # Path to the cloned directory of regrid-wrapper
srun --account ${account} --nodes 1 --tasks 1 --time 00:01:00 ${cluster} ${partition} pytest -vs src/test
srun --account ${account} --nodes 1 --tasks 8 --time 00:01:00 ${cluster} ${partition} pytest -vs -m "mpi" src/test
#srun --account epic --nodes 1 --tasks 8 --time 00:01:00 pytest -vs -m "mpi" src/test/test_esmpy/test_field_wrapper.py::TestGridWrapper::test_fill_nc_variables
