# Environment Setup

> conda env create -f environment.yaml
> 
* Add `REGRID_WRAPPER_LOG_DIR` location to environment.

# Testing

> pytest src/test

For parallel testing:

> mpirun -n 8 pytest -m mpi src/test
