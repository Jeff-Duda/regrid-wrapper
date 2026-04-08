from pathlib import Path

import esmpy
import pytest

from regrid_wrapper.context.comm import COMM
from regrid_wrapper.esmpy.field_wrapper import Dimension, GridSpec, MeshWrapper, MetaToField, NcToField, NcToGrid, NcToMesh
from test.conftest import TEST_LOGGER, create_rrfs_grid_file


@pytest.fixture
def mwrap(ugrid_path: Path) -> MeshWrapper:
    # ncdump(ugrid_path)
    nc2mesh = NcToMesh(path=ugrid_path)
    mwrap = nc2mesh.create_mesh_wrapper()
    return mwrap


@pytest.fixture
def mesh_nc2field(ugrid_path: Path, mwrap: MeshWrapper) -> NcToField:
    # with open_nc(ugrid_path, mode="a", parallel=True) as ds:
    #     ds.createVariable("foo", "f4", ("n_face",))

    nc2field = NcToField(path=ugrid_path, name="foo", gwrap=mwrap, staggerloc=esmpy.MeshLoc.ELEMENT)
    return nc2field


@pytest.fixture
def grid_nc2field(tmp_path_shared: Path) -> NcToField:
    TEST_LOGGER.info("grid_nc2field: enter")
    src_path = tmp_path_shared / "grid.nc"
    TEST_LOGGER.info(f"{src_path=}")

    if COMM.rank == 0:
        TEST_LOGGER.info("grid_nc2field: create RRFS grid file")
        _ = create_rrfs_grid_file(src_path, fields=["foo"])
    COMM.barrier()

    nc2grid = NcToGrid(
        path=src_path,
        spec=GridSpec(
            x_center="grid_lont",
            y_center="grid_latt",
            x_dim=("grid_xt",),
            y_dim=("grid_yt",),
            x_corner="grid_lon",
            y_corner="grid_lat",
            x_corner_dim=("grid_x",),
            y_corner_dim=("grid_y",),
        ),
    )
    TEST_LOGGER.info("grid_nc2field: before create grid wrapper")
    gwrap = nc2grid.create_grid_wrapper()
    TEST_LOGGER.info("grid_nc2field: after create grid wrapper")

    nc2field = NcToField(path=src_path, name="foo", gwrap=gwrap)
    TEST_LOGGER.info("grid_nc2field: exit")
    return nc2field


@pytest.mark.mpi
def test_grid_to_mesh_regridding(mesh_nc2field: NcToField, grid_nc2field: NcToField, tmp_path_shared: Path) -> None:
    TEST_LOGGER.info("test_grid_to_mesh_regridding")
    src_fwrap = grid_nc2field.create_field_wrapper()

    dst_field = mesh_nc2field.create_field_wrapper()

    weight_filename = tmp_path_shared / "weights.nc"
    _ = esmpy.Regrid(
        srcfield=src_fwrap.value,
        dstfield=dst_field.value,
        regrid_method=esmpy.RegridMethod.CONSERVE,
        unmapped_action=esmpy.UnmappedAction.IGNORE,
        ignore_degenerate=True,
        filename=str(weight_filename),
    )

    assert weight_filename.exists()

    # if COMM.rank == 0:
    #     ncdump(weight_filename, header_only=True)


class TestNcToMesh:
    @pytest.mark.mpi
    def test_create_mesh_wrapper(self, mwrap: MeshWrapper) -> None:
        assert isinstance(mwrap.value, esmpy.Mesh)


class TestNcToField:
    @pytest.mark.mpi
    def test_create_field_wrapper(self, mesh_nc2field: NcToField) -> None:
        fwrap = mesh_nc2field.create_field_wrapper()
        assert isinstance(fwrap.value, esmpy.Field)


class TestMetaToField:
    @pytest.mark.mpi
    def test_create_field_wrapper(self, grid_nc2field: NcToField) -> None:
        dim_time = Dimension(name=("time",), size=24, lower=0, upper=23, staggerloc=esmpy.StaggerLoc.CENTER, coordinate_type="time")
        meta2field = MetaToField(name="foo", gwrap=grid_nc2field.gwrap, dim_time=dim_time)
        fwrap = meta2field.create_field_wrapper()
        assert fwrap.value.data.shape[2] == 24
