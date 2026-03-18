import subprocess
from pathlib import Path

import netCDF4 as nc
import xarray as xr
import numpy as np

from regrid_wrapper.context.logging import LOGGER


def _convert_mpas_to_ugrid_(input_path: Path) -> Path:
    """
    Reads an MPAS grid file using uxarray and writes it to a NetCDF file in UGRID format.
    """
    import uxarray as ux

    LOGGER.info(f"Reading MPAS grid from: {input_path}")
    # uxarray.open_grid can read MPAS files directly
    uxgrid = ux.open_grid(input_path)
    LOGGER.info(uxgrid)

    output_path = "tmp_ugrid.nc"
    LOGGER.info(f"Writing UGRID to: {output_path}")
    uxgrid.to_xarray().to_netcdf(output_path)
    LOGGER.info("Conversion completed successfully.")
    return output_path


def _fix_conversion_(input_path: Path, output_path: Path) -> None:
    LOGGER.info("starting conversion")

    with nc.Dataset(input_path, "r") as ds:
        var = ds.variables["face_node_connectivity"][:]
        LOGGER.info(f"var.min={var.min()}")
        LOGGER.info(f"var.max={var.max()}")
        LOGGER.info(f"var.shape={var.shape}")
        LOGGER.info(f"var.count_masked={np.ma.count_masked(var)}")

    LOGGER.info("ncks...")
    varname = "face_node_connectivity"
    subprocess.check_call(["ncks", "-D", "1", "--overwrite", "-x", "-v", varname, input_path, output_path])

    with xr.open_dataset(input_path) as ds:
        sizes = ds.sizes
        attrs = ds["face_node_connectivity"].attrs
        LOGGER.info(f"attrs={attrs}")

    LOGGER.info("update masking")
    with nc.Dataset(output_path, "a") as dst_ds:
        dst_ds.createDimension("n_max_face_nodes", sizes["n_max_face_nodes"])
        dst_ds.createVariable("face_node_connectivity", "i4", ("n_face", "n_max_face_nodes"), fill_value=-1)
        dst_ds["face_node_connectivity"].setncatts(attrs)
        with nc.Dataset(input_path, "r") as src_ds:
            src = src_ds["face_node_connectivity"][:]
            new_src = src.filled(-1)
            dst_ds["face_node_connectivity"][:] = new_src

    with nc.Dataset(output_path, "r") as ds:
        var = ds.variables["face_node_connectivity"][:]
        LOGGER.info(f"var.min={var.min()}")
        LOGGER.info(f"var.min.masked={var.data.min()}")
        LOGGER.info(f"var.max.masked={var.data.max()}")
        LOGGER.info(f"var.max={var.max()}")
        LOGGER.info(f"var.shape={var.shape}")
        LOGGER.info(f"var.count_masked={np.ma.count_masked(var)}")

    LOGGER.info("done with conversion")

def run_conversion(input_path: Path, output_path: Path) -> None:
    tmp_ugrid_path = _convert_mpas_to_ugrid_(input_path)
    try:
        _fix_conversion_(tmp_ugrid_path, output_path)
    finally:
        Path(tmp_ugrid_path).unlink()

# if __name__ == "__main__":
#     input_path = "/scratch4/BMC/acomp/Sudheer/Fire-nest/Retros/MPAS/BensTest/conus3km/conus3km.20250922/stmp/20250922/rrfs_ic_00_v2.1.2/det/ic_00/init.nc"
#     output_path = "/scratch3/NCEPDEV/stmp/Benjamin.Koziol/sandbox/data/mpas-aerosols/ugrid.nc"
#
#     tmp_ugrid_path = convert_mpas_to_ugrid(input_path)
#     try:
#         fix_conversion(tmp_ugrid_path, output_path)
#     finally:
#         Path(tmp_ugrid_path).unlink()
