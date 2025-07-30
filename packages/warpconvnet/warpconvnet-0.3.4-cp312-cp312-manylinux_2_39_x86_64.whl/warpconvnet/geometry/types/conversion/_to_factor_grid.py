from typing import List, Tuple, Union, Optional, Literal

from warpconvnet.ops.reductions import REDUCTION_TYPES_STR


def points_to_factor_grid(
    points: "Points",
    grid_shapes: List[Tuple[int, int, int]],
    memory_formats: List[Union["GridMemoryFormat", str]],
    search_radius: Optional[float] = None,
    k: Optional[int] = None,
    search_type: Literal["radius", "knn", "voxel"] = "radius",
    reduction: REDUCTION_TYPES_STR = "mean",
) -> "FactorGrid":
    """Convert points to a factorized grid geometry.

    Args:
        points: Points to convert
        grid_shapes: List of grid resolutions (H, W, D)
        memory_formats: List of factorized formats to use

    Returns:
        Factorized grid geometry
    """
    from warpconvnet.geometry.types.factor_grid import FactorGrid
    from warpconvnet.geometry.types.grid import GridMemoryFormat
    from warpconvnet.geometry.types.points import Points
    from warpconvnet.geometry.types.conversion.to_grid import points_to_grid

    assert isinstance(points, Points), f"input points must be a Points object, got {type(points)}"
    for memory_format in memory_formats:
        assert isinstance(
            memory_format, GridMemoryFormat
        ), f"memory_format must be a GridMemoryFormat object, got {type(memory_format)}"

    geometries = []
    for grid_shape, memory_format in zip(grid_shapes, memory_formats):
        geometry = points_to_grid(
            points,
            grid_shape,
            memory_format,
            search_radius=search_radius,
            k=k,
            search_type=search_type,
            reduction=reduction,
        )
        geometries.append(geometry)
    return FactorGrid(geometries)
