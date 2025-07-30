from typing import Union, Any, Optional
from matplotlib.colors import Colormap, LinearSegmentedColormap
from matplotlib import colormaps


def resolve_basemap_name(basemap_name: str) -> Any:
    """
    Resolve a basemap name into an xyzservices object.

    Args:
    basemap_name (str): Dot-separated name of the basemap (e.g., 'Esri.WorldImagery').

    Returns:
        Any: An xyzservices object, compatible with both folium and ipyleaflet.

    Raises:
        AttributeError: If the basemap name is not valid.
    """
    import xyzservices.providers as xyz

    provider = xyz
    for part in basemap_name.split("."):
        if hasattr(provider, part):
            provider = getattr(provider, part)
        else:
            raise AttributeError(f"Unsupported basemap: {basemap_name}")
    return provider


def resolve_colormap(colormap: Optional[Union[str, dict]]) -> Optional[Colormap]:
    """
    Resolve a colormap input to a matplotlib colormap object.

    Args:
        colormap (str or dict): The input colormap.
            - If dict: Creates and returns a LinearSegmentedColormap.
            - If str: Returns the corresponding built-in matplotlib colormap.
            - If None: Returns None.

    Returns:
        matplotlib.colors.Colormap: A valid colormap object.

    Raises:
        ValueError: If the colormap dictionary is invalid or the string is not a recognized colormap name.
        TypeError: If the input type is not str or dict.
    """
    if colormap is None:
        return None

    if isinstance(colormap, dict):
        try:
            custom_colormap = LinearSegmentedColormap("custom", colormap)
            custom_colormap._init()  # Forces colormap dict validation
            return custom_colormap
        except Exception as e:
            raise ValueError(f"Invalid colormap dictionary format: {e}")

    if isinstance(colormap, str):
        if colormap in colormaps:
            return colormaps[colormap]
        else:
            raise ValueError(
                f"Invalid colormap name '{colormap}'. Must be one of: {list(colormaps)}"
            )

    raise TypeError(
        f"Invalid colormap type: expected str, dict, or Colormap, got {type(colormap)}"
    )
