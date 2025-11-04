load("regrid-wrapper-spack-stack")

load("esmf/8.8.0")
load("py-xarray/2024.7.0")
load("py-netcdf4/1.7.1.post2")
load(pathJoin("nco", os.getenv("nco_ver") or "5.2.4"))

-- load("esmf/8.8.0")
-- load("py-xarray")
-- load("py-netcdf4")
-- load("nco")
