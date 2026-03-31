# CLI Usage

The `rw` command provides a set of command-line tools for regridding.

## MPAS to UGRID Conversion

1. `conda env create -f environment-uxarray.yaml`
2. `cd <regrid-wrapper src>`
3. `conda run -n regrid-wrapper-uxarray pip install -e .`
4. `export REGRID_WRAPPER_LOG_DIR=<path to log dir>`
4. `conda run -n regrid-wrapper-uxarray rw mpas-to-ugrid <flags>`

Convert an MPAS grid file to UGRID format:

```bash
usage: rw mpas-to-ugrid [-h] -i INPUT -o OUTPUT [--clobber]

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input MPAS grid path
  -o OUTPUT, --output OUTPUT
                        Output UGRID path
  --clobber             Overwrite output file if it exists (default is False)
```
