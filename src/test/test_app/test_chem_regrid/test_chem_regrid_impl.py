from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
import xarray as xr

from regrid_wrapper.app.chem_regrid.chem_regrid_impl import main
from regrid_wrapper.app.chem_regrid.context import ChemRegridContext, DatasetName
from regrid_wrapper.context.comm import COMM
from test.conftest import create_rrfs_grid_file, TEST_LOGGER

_RAVE_FIELDS = ["TPM", "FRE", "FRP_MEAN", "PM25", "NH3", "SO2", "CH4", "CO", "NOx"]

def create_rave_file_from_ugrid(ugrid_path: Path, output_path: Path) -> None:
    if COMM.rank == 0:
        ds = xr.open_dataset(ugrid_path)
        buffer = 10
        min_lon = float(ds.node_lon.min()) - buffer
        max_lon = float(ds.node_lon.max()) + buffer
        min_lat = float(ds.node_lat.min()) - buffer
        max_lat = float(ds.node_lat.max()) + buffer
        create_rrfs_grid_file(
            output_path,
            fields=_RAVE_FIELDS,
            min_lon=min_lon,
            max_lon=max_lon,
            min_lat=min_lat,
            max_lat=max_lat,
            ntime=1,
        )
    COMM.barrier()


def test_rrfs_grid_from_ugrid(ugrid_path: Path, tmp_path_shared: Path) -> None:
    rrfs_grid_from_ugrid = tmp_path_shared / "rrfs_grid_from_ugrid.nc"
    create_rave_file_from_ugrid(ugrid_path, rrfs_grid_from_ugrid)

    assert rrfs_grid_from_ugrid.exists()

    # ncdump(rrfs_grid_from_ugrid)

    ds_rrfs = xr.open_dataset(rrfs_grid_from_ugrid)
    ds_ugrid = xr.open_dataset(ugrid_path)

    # Check spatial extent
    buffer = 10
    assert ds_rrfs.grid_lont.min() == ds_ugrid.node_lon.min() - buffer
    assert ds_rrfs.grid_lont.max() == ds_ugrid.node_lon.max() + buffer
    assert ds_rrfs.grid_latt.min() == ds_ugrid.node_lat.min() - buffer
    assert ds_rrfs.grid_latt.max() == ds_ugrid.node_lat.max() + buffer

    # Check expected variables
    assert "grid_lont" in ds_rrfs
    assert "grid_latt" in ds_rrfs
    assert "grid_lon" in ds_rrfs
    assert "grid_lat" in ds_rrfs


@pytest.fixture
def chem_regrid_context(tmp_path_shared: Path, ugrid_path: Path) -> ChemRegridContext:
    # Setup directories
    workdir = tmp_path_shared / "work"
    input_dir = tmp_path_shared / "input"
    output_dir = tmp_path_shared / "output"
    weight_dir = tmp_path_shared / "weights"

    if COMM.rank == 0:
        workdir.mkdir(exist_ok=True)
        input_dir.mkdir(exist_ok=True)
        output_dir.mkdir(exist_ok=True)
        weight_dir.mkdir(exist_ok=True)
    COMM.barrier()

    cycle = "2026040809"
    ebb_dcycle = 1  # same-day

    # Create RAVE input files for the 25 iterations of the dates_needed loop
    for i in range(25):
        date_dt = datetime(2026, 4, 8, 9) + timedelta(hours=i)
        date_str = date_dt.strftime("%Y%m%d%H")
        # find_latest_rave_file looks for "RAVE-HrlyEmiss-3km_v2r0_blend_s" + date_to_process
        rave_filename = f"RAVE-HrlyEmiss-3km_v2r0_blend_s{date_str}_e{date_str}_v2.nc"
        rave_path = input_dir / rave_filename
        create_rave_file_from_ugrid(ugrid_path, rave_path)

    # Create dummy destination file (MPAS grid)
    # The main() reads num_cells from dst_path
    dst_path = workdir / "init.nc"
    ds_dst = xr.Dataset()
    num_cells = 162
    ds_dst["latCell"] = xr.DataArray(np.ones(num_cells), dims=["nCells"])
    ds_dst["lonCell"] = xr.DataArray(np.ones(num_cells), dims=["nCells"])
    ds_dst["areaCell"] = xr.DataArray(np.ones(num_cells), dims=["nCells"])
    ds_dst["xtime"] = xr.DataArray(np.ones(num_cells), dims=["nCells"])
    if COMM.rank == 0:
        ds_dst.to_netcdf(dst_path)
    COMM.barrier()

    # Create ChemRegridContext
    ctx = ChemRegridContext(
        dataset_name=DatasetName.RAVE,
        workdir=workdir,
        input_dir=input_dir,
        output_dir=output_dir,
        weight_dir=weight_dir,
        cycle=cycle,
        mesh_name="test_mesh",
        scrip_path=ugrid_path,
        dst_path=dst_path,
        ebb_dcycle=ebb_dcycle,
        fcst_length=24,
    )
    return ctx


@pytest.mark.mpi
def test_mock_chem_regrid_impl_rave_integration(
    ugrid_path: Path, tmp_path_shared: Path, chem_regrid_context: ChemRegridContext
) -> None:

    # Mock RaveToMpasRegridProcessor to avoid actual regridding
    with (
        patch("regrid_wrapper.app.chem_regrid.chem_regrid_impl.RaveToMpasRegridProcessor") as mock_processor_class,
        patch("regrid_wrapper.app.chem_regrid.chem_regrid_impl.RaveToMpasRegridContext") as _,
    ):
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor

        # Run main
        main(chem_regrid_context)

        # Verify the loop ran 25 times
        # processor is initialized once (processor is None for the first pass)
        # then updated 24 times
        assert mock_processor_class.call_count == 1
        assert mock_processor.run.call_count == 25


@pytest.mark.mpi
def test_chem_regrid_impl_rave_integration(ugrid_path: Path, tmp_path_shared: Path, chem_regrid_context: ChemRegridContext) -> None:
    main(chem_regrid_context)
    output_files = list(chem_regrid_context.output_dir.glob("*"))
    # TEST_LOGGER.info(f"{output_files=}")
    assert len(output_files) == 25
    actual_sums = {'TPM': 85.65801452561297, 'FRE': 308.36885229220667,
                   'FRP_MEAN': 308.36885229220667, 'PM25': 85.65801452561297,
                   'NH3': 5.038706736800762, 'SO2': 0.08565801452561297, 'CH4': 5.353625907850811,
                   'CO': 3.059214804486177, 'NOx': 2.3586989507052842}
    for output_file in output_files:
        with xr.open_dataset(output_file) as ds:
            # TEST_LOGGER.info(f"{ds=}")
            for rave_field in _RAVE_FIELDS:
                # TEST_LOGGER.info(f"{rave_field=}, {rave_field=}")
                target = ds[rave_field]
                # TEST_LOGGER.info(f"{target=}")
                if rave_field in ("FRE", "FRP_MEAN"):
                    expected_shape = (1, 162)
                else:
                    expected_shape = (1, 162, 1)
                assert target.shape == expected_shape

                np.testing.assert_almost_equal(target.sum(), actual_sums[rave_field])

    weight_output_files = list(chem_regrid_context.weight_dir.glob("*"))
    # TEST_LOGGER.info(f"{weight_output_files=}")
    assert len(weight_output_files) == 1
    with xr.open_dataset(weight_output_files[0]) as ds:
        # TEST_LOGGER.info(f"{ds=}")
        assert ds.sizes == {"n_s": 6109}
        np.testing.assert_almost_equal(ds["S"].sum(), 168.59977032981334)
