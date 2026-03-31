#!/usr/bin/env bash

set -ue

module use /autofs/ncrc-svm1_proj/epic/spack-stack/c6/spack-stack-2.1.0/envs/ue-oneapi-2025.2.1/modules/Core

module avail

module load stack-intel-oneapi-compilers/2025.2.1
module load stack-cray-mpich/8.1.32

module load py-pytest/8.2.1

which python
