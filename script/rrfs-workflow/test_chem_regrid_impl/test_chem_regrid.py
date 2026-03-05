import sys
from unittest.mock import MagicMock

# Mock esmpy BEFORE any other imports that might trigger it
mock_esmpy = MagicMock()
mock_esmpy.StaggerLoc.CENTER = 0
mock_esmpy.MeshLoc.ELEMENT = 1
mock_esmpy.RegridMethod.CONSERVE = 2
mock_esmpy.UnmappedAction.IGNORE = 3
mock_esmpy.FileFormat.SCRIP = 4

sys.modules["esmpy"] = mock_esmpy

import pytest
import numpy as np
from pathlib import Path

# Try importing netCDF4, if it fails, the test will fail anyway but with a better message
import netCDF4 as nc

# Now it's safe to import from regrid_wrapper
from regrid_wrapper.chem_regrid_impl.chem_regrid import (
    RaveToMpasRegridContext,
    RaveToMpasRegridProcessor,
)
from regrid_wrapper.context.comm import COMM

def create_mock_rave_file(path: Path):
    with nc.Dataset(path, "w") as ds:
        ds.createDimension("grid_xt", 10)
        ds.createDimension("grid_yt", 10)
        ds.createDimension("grid_x", 11)
        ds.createDimension("grid_y", 11)
        ds.createDimension("time", 1)
        
        # Center coords
        lont = ds.createVariable("grid_lont", "f4", ("grid_yt", "grid_xt"))
        lont[:] = np.ones((10, 10))
        latt = ds.createVariable("grid_latt", "f4", ("grid_yt", "grid_xt"))
        latt[:] = np.ones((10, 10))
        
        # Corner coords
        lon = ds.createVariable("grid_lon", "f4", ("grid_y", "grid_x"))
        lon[:] = np.ones((11, 11))
        lat = ds.createVariable("grid_lat", "f4", ("grid_y", "grid_x"))
        lat[:] = np.ones((11, 11))
        
        # Data fields
        tpm = ds.createVariable("TPM", "f4", ("grid_yt", "grid_xt", "time"))
        tpm[:, :, :] = np.ones((10, 10, 1), dtype="f4")
        tpm.setncattr("units", "kg/hr")

        pm25 = ds.createVariable("PM25", "f4", ("grid_yt", "grid_xt", "time"))
        pm25[:, :, :] = np.ones((10, 10, 1), dtype="f4") * 0.5
        pm25.setncattr("units", "kg/hr")
        
        # Area field (needed for RAVE)
        area = ds.createVariable("area", "f4", ("grid_yt", "grid_xt"))
        area[:] = np.ones((10, 10))
    
    # Verify the file immediately
    with nc.Dataset(path, "r") as ds:
        v = ds.variables["TPM"]
        print(f"\nDEBUG: TPM shape in file: {v.shape}")
        print(f"DEBUG: TPM data: {v[:]}")
        if v[:].size == 0:
            print("WARNING: TPM data is EMPTY!")

def create_mock_mpas_file(path: Path, num_cells=100):
    with nc.Dataset(path, "w") as ds:
        ds.createDimension("nCells", num_cells)
        ds.createDimension("StrLen", 64)
        ds.createVariable("latCell", "f8", ("nCells",))[:] = 0.0
        ds.createVariable("lonCell", "f8", ("nCells",))[:] = 0.0
        ds.createVariable("areaCell", "f8", ("nCells",))[:] = 1.0
        ds.createVariable("xland", "i4", ("nCells",))[:] = 1
        xtime = ds.createVariable("xtime", "S1", ("nCells", "StrLen"))
        time_str = b"2026-02-27_10:12:00"
        for i in range(num_cells):
            xtime[i, :len(time_str)] = list(time_str)

def test_chem_regrid_rave_e2e(tmp_path):
    # Reset mock_esmpy for each run
    mock_esmpy.reset_mock()
    
    workdir = tmp_path / "work"
    workdir.mkdir(parents=True, exist_ok=True)
    
    src_path = workdir / "rave_input.nc"
    dst_path = workdir / "init.nc"
    new_dst_path = workdir / "output.nc"
    scrip_path = workdir / "scrip.nc"
    weight_path = workdir / "weights.nc"
    desc_stats_out = workdir / "stats.csv"
    
    if COMM.rank == 0:
        create_mock_rave_file(src_path)
        create_mock_mpas_file(dst_path, num_cells=100)
        # Create a dummy scrip file
        with nc.Dataset(scrip_path, "w") as ds:
            ds.createDimension("grid_size", 100)
            ds.createDimension("grid_corners", 4)
            ds.createDimension("grid_rank", 1)
    
    COMM.barrier()
    
    context = RaveToMpasRegridContext(
        dataset_name="RAVE",
        src_path=src_path,
        dst_path=dst_path,
        new_dst_path=new_dst_path,
        desc_stats_out=desc_stats_out,
        weight_path=weight_path,
        InterpMethod="CONSERVE",
        scrip_path=scrip_path,
        num_cells=100,
        mesh_name="test_mesh",
        field_names=("TPM",),
        x_center="grid_lont",
        y_center="grid_latt",
        x_dim="grid_xt",
        y_dim="grid_yt",
        x_corner="grid_lon",
        y_corner="grid_lat",
        x_corner_dim="grid_x",
        y_corner_dim="grid_y",
        level_in_name="None",
        level_out_name="nkwildfire",
        level_out_size=1,
        time_name="time",
        time_size=1,
    )
    
    # Setup mock field data behaviors
    def field_side_effect(grid, name=None, typekind=None, staggerloc=None, meshloc=None, ndbounds=None):
        mock_field = MagicMock()
        # grid is a mock
        if grid == mock_esmpy.Grid.return_value:
            # Source grid
            # If name is None, we look at the Grid object or assume based on ndbounds if available
            # But here name is usually passed from FieldWrapper.
            if name and any(x in name for x in ["TPM", "PM25", "DBL_POLL", "ENL_POLL"]):
                # These have time dim
                mock_field.data = np.zeros((10, 10, 1))
                mock_field.lower_bounds = [0, 0, 0]
                mock_field.upper_bounds = [10, 10, 1]
            else:
                # Coordinates or Area don't have time dim
                mock_field.data = np.zeros((10, 10))
                mock_field.lower_bounds = [0, 0]
                mock_field.upper_bounds = [10, 10]
                # Corner coords might be 11x11
                if name and ("lon" in name or "lat" in name) and "lont" not in name and "latt" not in name:
                     mock_field.data = np.zeros((11, 11))
                     mock_field.upper_bounds = [11, 11]
        else:
            # Destination mesh (100)
            mock_field.data = np.zeros((100,))
            mock_field.lower_bounds = [0]
            mock_field.upper_bounds = [100]
        return mock_field

    mock_esmpy.Field.side_effect = field_side_effect
    
    # Setup mock grid/mesh behaviors
    mock_grid_instance = mock_esmpy.Grid.return_value
    mock_grid_instance.lower_bounds = [np.array([0, 0]), np.array([0, 0])]
    mock_grid_instance.upper_bounds = [np.array([10, 10]), np.array([11, 11])]
    
    mock_mesh_instance = mock_esmpy.Mesh.return_value
    mock_mesh_instance.lower_bounds = [0]
    mock_mesh_instance.upper_bounds = [100]
    
    processor = RaveToMpasRegridProcessor(context)
    processor.initialize()
    processor.run()
    processor.finalize()
    
    # Verifications
    assert mock_esmpy.Mesh.called
    assert mock_esmpy.Field.called
    assert mock_esmpy.Regrid.called
    assert new_dst_path.exists()
    
    if COMM.rank == 0:
        with nc.Dataset(new_dst_path, "r") as ds:
            assert "TPM" in ds.variables
            # nCells=100, level=1, time=1
            # Actual shape depends on how set_variable_data and DimensionCollection work
            # In our case it seems it's (time, nCells, level) -> (1, 100, 1)
            assert ds.variables["TPM"].shape == (1, 100, 1)
