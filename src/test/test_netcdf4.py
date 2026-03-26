from pathlib import Path

import netCDF4 as nc
import pytest
from mpi4py import MPI


@pytest.mark.mpi
def test_parallel(tmp_path_shared: Path) -> None:
    ds = nc.Dataset(
        tmp_path_shared / "foo.nc",
        mode="w",
        clobber=False,
        parallel=True,
        comm=MPI.COMM_WORLD,
        info=MPI.Info(),
    )
    ds.close()
