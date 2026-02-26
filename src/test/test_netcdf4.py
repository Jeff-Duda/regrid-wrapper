from pathlib import Path

import pytest
from mpi4py import MPI

import netCDF4 as nc

from regrid_wrapper.context.env import ENV


@pytest.mark.mpi
def test_parallel(tmp_path_shared: Path) -> None:
    if not ENV.REGRID_WRAPPER_PARALLEL_NC4:
        pytest.skip("parallel netcdf4 not selected")
    ds = nc.Dataset(
        tmp_path_shared / "foo.nc",
        mode="w",
        clobber=False,
        parallel=True,
        comm=MPI.COMM_WORLD,
        info=MPI.Info(),
    )
    ds.close()
