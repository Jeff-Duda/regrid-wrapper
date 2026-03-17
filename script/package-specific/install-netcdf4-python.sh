#!/bin/bash

set -ue

clonedir=/home/Benjamin.Koziol/htmp/
installpath=/home/Benjamin.Koziol/htmp/regrid-wrapper-nc4

module purge
module use modulefiles
module load regrid-wrapper-spack-stack nco py-pip py-numpy py-setuptools
module load py-mpi4py
which python
which pip
python -c "import mpi4py; print(mpi4py.__file__)"

cd ${clonedir}
#rm -rf ${clonedir}/netcdf4-python #tdk:rm
#git clone --recurse-submodules https://github.com/Unidata/netcdf4-python.git
cd netcdf4-python
#git checkout master
git checkout v1.7.1.post2

#python -m venv ${venvpath}
#source ${venvpath}/bin/activate

#export PYTHONPATH=${PYTHONPATH}:/contrib/spack-stack/spack-stack-1.9.2/envs/ue-oneapi-2024.2.1/install/oneapi/2024.2.1/py-mpi4py-4.0.1-plc5ydd/lib/python3.11/site-packages
python -m pip install -v --no-cache-dir --target ${installpath} .
