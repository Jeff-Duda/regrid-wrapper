prepend_path("MODULEPATH", "/scratch3/NCEPDEV/stmp/Benjamin.Koziol/sandbox/spack-stack/envs/mpas-aerosols/modules/Core")
prepend_path("MODULEPATH", "/scratch3/NCEPDEV/stmp/Benjamin.Koziol/sandbox/spack-stack/envs/mpas-aerosols/modules/intel-oneapi-mpi/2021.17/intel-oneapi-compilers/2025.3.1")
prepend_path("MODULEPATH", "/scratch3/NCEPDEV/stmp/Benjamin.Koziol/sandbox/spack-stack/envs/mpas-aerosols/modules/intel-oneapi-compilers/2025.3.1")

load("stack-intel-oneapi-compilers/2025.3.1")
load("stack-intel-oneapi-mpi/2021.17")

load("esmf/8.9.1")
load("py-netcdf4/1.7.2")
load("py-pytest/8.2.1")
load("py-xarray/2024.7.0")

load("nco")

-- prepend_path("MODULEPATH", "/contrib/spack-stack/spack-stack-1.9.2/envs/ue-oneapi-2024.2.1/install/modulefiles/Core")
-- load("stack-oneapi")
-- load("stack-intel-oneapi-mpi")

--prepend_path("MODULEPATH", "/contrib/spack-stack/spack-stack-1.9.3/envs/ue-gcc-12.4.0/install/modulefiles/Core")
--load("stack-gcc")
--load("stack-openmpi")
--load("stack-python")
