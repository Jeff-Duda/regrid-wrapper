prepend_path("MODULEPATH", "/gpfs/f6/bil-fire8/scratch/Benjamin.Koziol/sandbox/spack-stack/envs/mpas-aerosols-v2/modules/Core")
prepend_path("MODULEPATH", "/gpfs/f6/bil-fire8/scratch/Benjamin.Koziol/sandbox/spack-stack/envs/mpas-aerosols-v2/modules/cray-mpich/8.1.32/intel-oneapi-compilers/2025.2.1")
prepend_path("MODULEPATH", "/gpfs/f6/bil-fire8/scratch/Benjamin.Koziol/sandbox/spack-stack/envs/mpas-aerosols-v2/modules/intel-oneapi-compilers/2025.2.1")

load("stack-intel-oneapi-compilers/2025.2.1")
load("stack-cray-mpich/8.1.32")

load("esmf/8.9.1")
load("py-netcdf4/1.7.2")
load("py-pytest/8.2.1")
load("py-xarray/2024.7.0")

load("Core/24.11")
load("nco/5.1.9")
