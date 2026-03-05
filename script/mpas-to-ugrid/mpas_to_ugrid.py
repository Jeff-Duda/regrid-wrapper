import uxarray as ux


def convert_mpas_to_ugrid(input_path: str, output_path: str) -> None:
    """
    Reads an MPAS grid file using uxarray and writes it to a NetCDF file in UGRID format.
    """
    print(f"Reading MPAS grid from: {input_path}")
    # uxarray.open_grid can read MPAS files directly
    uxgrid = ux.open_grid(input_path)
    print(uxgrid)

    print(f"Writing UGRID to: {output_path}")
    uxgrid.to_xarray().to_netcdf(output_path)
    print("Conversion completed successfully.")


if __name__ == "__main__":
    input_path = "/scratch4/BMC/acomp/Sudheer/Fire-nest/Retros/MPAS/BensTest/conus3km/conus3km.20250922/stmp/20250922/rrfs_ic_00_v2.1.2/det/ic_00/init.nc"
    output_path = "/scratch3/NCEPDEV/stmp/Benjamin.Koziol/sandbox/data/mpas-aerosols/ugrid.nc"
    convert_mpas_to_ugrid(input_path, output_path)
