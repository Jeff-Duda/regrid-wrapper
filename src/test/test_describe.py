from pathlib import Path

from regrid_wrapper.describe import DescribeParams, describe
from test.conftest import create_rrfs_grid_file


def test(tmp_path_shared: Path) -> None:
    data = tmp_path_shared / "data.nc"
    _ = create_rrfs_grid_file(data)

    params = DescribeParams(
        files=(data,),
        varnames=("grid_lont", "grid_latt"),
        namespace="dust",
        csv_out=tmp_path_shared / "summary.csv",
    )
    df = describe(params)
    assert df is not None
