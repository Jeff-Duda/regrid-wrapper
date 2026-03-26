from dataclasses import dataclass

from regrid_wrapper.esmpy.field_wrapper import GridSpec, NameListType


@dataclass
class RaveGridSpec(GridSpec):
    x_center: str = "grid_lont"
    y_center: str = "grid_latt"
    x_dim: NameListType = ("grid_xt",)
    y_dim: NameListType = ("grid_yt",)
    x_corner: str = "grid_lon"
    y_corner: str = "grid_lat"
    x_corner_dim: NameListType | None = ("grid_x",)
    y_corner_dim: NameListType | None = ("grid_y",)
