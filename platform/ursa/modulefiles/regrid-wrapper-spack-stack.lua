prepend_path("MODULEPATH", "/contrib/spack-stack/spack-stack-1.9.2/envs/ue-oneapi-2024.2.1/install/modulefiles/Core")
load("stack-oneapi")
load("stack-intel-oneapi-mpi")
load("stack-python")

--prepend_path("MODULEPATH", "/contrib/spack-stack/spack-stack-1.9.3/envs/ue-gcc-12.4.0/install/modulefiles/Core")
--load("stack-gcc")
--load("stack-openmpi")
--load("stack-python")
