#!/usr/bin/env bash

set -ue

module use /contrib/spack-stack/spack-stack-2.1.0/envs/ue-oneapi-2025.3.1/modules/Core
module load stack-intel-oneapi-compilers/2025.3.1
module load stack-intel-oneapi-mpi/2021.17

module load esmf/8.9.1

which python
python -c "import esmpy"
echo "successfully imported"