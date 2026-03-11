import random
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, List

import numpy as np
import pytest
import xarray as xr

from regrid_wrapper.context.comm import COMM
from regrid_wrapper.context.env import ENV
from regrid_wrapper.context.logging import LOGGER
import netCDF4 as nc

TEST_LOGGER = LOGGER.getChild("test")


@pytest.fixture
def bin_dir() -> Path:
    return Path(__file__).parent.joinpath("bin").resolve().expanduser()


@pytest.fixture
def tmp_path_shared(tmp_path: Path) -> Path:
    return Path(COMM.bcast({"path": str(tmp_path)}, root=0)["path"])


@contextmanager
def custom_env(**kwargs: Any) -> Iterator[None]:
    orig = {}
    for k, v in kwargs.items():
        orig[k] = getattr(ENV, k)
        setattr(ENV, k, v)
    try:
        yield
    finally:
        for k, v in orig.items():
            setattr(ENV, k, v)


def create_analytic_data_array(
    dims: List[str],
    lon_mesh: np.ndarray,
    lat_mesh: np.ndarray,
    ntime: int | None = None,
) -> xr.DataArray:
    deg_to_rad = 3.141592653589793 / 180.0
    analytic_data = 2.0 + np.cos(deg_to_rad * lon_mesh) ** 2 * np.cos(
        2.0 * deg_to_rad * (90.0 - lat_mesh)
    )
    if ntime is not None:
        time_modifier = np.arange(1, ntime + 1).reshape(ntime, 1, 1)
        analytic_data = analytic_data.reshape([1] + list(analytic_data.shape))
        analytic_data = np.repeat(analytic_data, ntime, axis=0)
        analytic_data = time_modifier * analytic_data
    return xr.DataArray(
        analytic_data,
        dims=dims,
    )


def create_rrfs_grid_file(
    path: Path,
    with_corners: bool = True,
    fields: List[str] | None = None,
    min_lon: int = 230,
    max_lon: int = 300,
    min_lat: int = 25,
    max_lat: int = 50,
    nlon: int = 71,
    nlat: int = 26,
) -> xr.Dataset:
    if path.exists():
        raise ValueError(f"path exists: {path}")
    lon = np.linspace(min_lon, max_lon, nlon)
    lat = np.linspace(min_lat, max_lat, nlat)
    lon_mesh, lat_mesh = np.meshgrid(lon, lat)
    ds = xr.Dataset()
    dims = ["grid_yt", "grid_xt"]
    ds["grid_lont"] = xr.DataArray(lon_mesh, dims=dims)
    ds["grid_latt"] = xr.DataArray(lat_mesh, dims=dims)
    if with_corners:
        lonc = np.hstack((lon - 0.5, [lon[-1] + 0.5]))
        latc = np.hstack((lat - 0.5, [lat[-1] + 0.5]))
        lonc_mesh, latc_mesh = np.meshgrid(lonc, latc)
        ds["grid_lon"] = xr.DataArray(lonc_mesh, dims=["grid_y", "grid_x"])
        ds["grid_lat"] = xr.DataArray(latc_mesh, dims=["grid_y", "grid_x"])
    if fields is not None:
        for field in fields:
            ds[field] = create_analytic_data_array(dims, lon_mesh, lat_mesh)
    ds.to_netcdf(path)
    return ds


# def create_veg_map_file(path: Path, field_names: List[str]) -> xr.Dataset:
#     if path.exists():
#         raise ValueError(f"path exists: {path}")
#     lon = np.linspace(230, 300, 71)
#     lat = np.linspace(25, 50, 26)
#     lon_mesh, lat_mesh = np.meshgrid(lon, lat)
#
#     with nc.Dataset(path, "w") as ds:
#         ds.createDimension("lon", 71)
#         ds.createDimension("geolon", 71)
#         ds.createDimension("lat", 26)
#         ds.createDimension("geolat", 26)
#         geolat = ds.createVariable("geolat", float, ("lat", "lon"))
#         geolat[:] = lat_mesh
#         geolon = ds.createVariable("geolon", float, ("lat", "lon"))
#         geolon[:] = lon_mesh
#         for field_name in field_names:
#             field = ds.createVariable(field_name, float, ("geolat", "geolon"))
#             field[:] = create_analytic_data_array(
#                 ("geolat", "geolon"), lon_mesh, lat_mesh
#             )
#             field.setncattr("foo", random.random())
#
#     # ds = xr.Dataset()
#     # dims = ["geolat", "geolon"]
#     # ds["geolat"] = xr.DataArray(lat_mesh, dims=dims)
#     # ds["geolon"] = xr.DataArray(lon_mesh, dims=dims)
#     # for field_name in field_names:
#     #     ds[field_name] = create_analytic_data_array(dims, lon_mesh, lat_mesh)
#     #     ds[field_name].attrs["foo"] = random.random()
#     # ds.to_netcdf(path)
#
#     return ds


# DUST_FIELD_OFFSETS = {ii: random.randint(1, 1000) for ii in ("foo", "bar")}
#
#
# def create_dust_data_file(path: Path) -> xr.Dataset:
#     if path.exists():
#         raise ValueError(f"path exists: {path}")
#
#     lon = np.linspace(230, 300, 71)
#     lat = np.linspace(25, 50, 26)
#     lon_mesh, lat_mesh = np.meshgrid(lon, lat)
#     ds = xr.Dataset()
#     dims = ["lat", "lon"]
#     ds["geolat"] = xr.DataArray(lat_mesh, dims=dims)
#     ds["geolon"] = xr.DataArray(lon_mesh, dims=dims)
#
#     ds["time"] = xr.DataArray(np.arange(12, dtype=np.double), dims=["time"])
#
#     for coord_name in ["time", "geolat", "geolon"]:
#         ds[coord_name].attrs["foo"] = random.random()
#
#     for field_name in ("foo", "bar"):
#         ds[field_name] = create_analytic_data_array(
#             ["time", "lat", "lon"], lon_mesh, lat_mesh, ntime=12
#         )
#         ds[field_name] += DUST_FIELD_OFFSETS[field_name]
#         ds[field_name].attrs["foo"] = random.random()
#     ds.attrs["foo"] = random.random()
#     ds.to_netcdf(path)
#     return ds


def assert_zero_sum_diff(actual: np.ndarray, expected: np.ndarray) -> None:
    assert (actual - expected).sum() == 0
