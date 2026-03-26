import pytest

try:
    import uxarray as ux  # type: ignore # noqa: F401
except ImportError:
    pytest.skip("uxarray not installed", allow_module_level=True)

import time
from pathlib import Path

import esmpy
import pytest

from regrid_wrapper.context.comm import COMM
from regrid_wrapper.mpas.mpas_to_ugrid import run_conversion
from test.conftest import TEST_LOGGER


def read_ugrid_mesh(input_path: Path) -> esmpy.Mesh:
    manager = esmpy.Manager()
    t1 = time.perf_counter()
    mesh = esmpy.Mesh(filename=str(input_path), filetype=esmpy.FileFormat.UGRID, meshname="grid_topology")
    t2 = time.perf_counter()
    TEST_LOGGER.debug(f"mesh read time: {t2 - t1} s, {manager.pet_count=}")
    return mesh


@pytest.fixture
def ugrid_path(tmp_path_shared: Path) -> Path:
    ugrid_path = Path("/opt/uxarray/test/meshfiles/mpas/QU/mesh.QU.1920km.151026.nc")
    assert ugrid_path.exists()

    output_path = tmp_path_shared / "ugrid.nc"
    if COMM.rank == 0:
        run_conversion(ugrid_path, output_path)
    COMM.barrier()
    # shutil.copy2(output_path, "/opt/project/src/test/bin/mesh.QU.1920km.151026.ugrid.nc")
    return output_path


@pytest.fixture
def ugrid_esmpy_mesh(ugrid_path: Path) -> esmpy.Mesh:
    mesh = read_ugrid_mesh(ugrid_path)
    return mesh


@pytest.mark.mpi
def test_mpas_to_ugrid(ugrid_esmpy_mesh: esmpy.Mesh) -> None:
    assert isinstance(ugrid_esmpy_mesh, esmpy.Mesh)
