import folium
from typing import Union
from chartops import common
from pathlib import Path
import geopandas as gpd


class Map(folium.Map):
    def add_basemap(self, basemap_name: str, **kwargs) -> None:
        """
        Add a basemap to the folium map.

        Args:
            basemap_name (str): Name of the basemap to add. Resolved with xyzservices.
            **kwargs (dict): Extra kwargs to pass to basemap_to_tiles.

        Returns:
            None
        """
        basemap = common.resolve_basemap_name(basemap_name)
        folium.TileLayer(
            tiles=basemap.build_url(),
            attr=basemap.attribution,
            name=basemap_name,
            **kwargs,
        ).add_to(self)

    def add_layer_control(self) -> None:
        """
        Add a layer control widget to the folium map.

        Returns:
            None
        """
        folium.LayerControl().add_to(self)

    def add_vector(self, filepath: Union[Path, str], name: str, **kwargs) -> None:
        """
        Add a vector data layer to the folium map.

        Args:
            filepath (Path or str): Path to the vector dataset or URL to a remote file.
            name (str): Name of the layer. Defaults to ''..
            **kwargs (dict): Additional styling options for the layer. Valid options include:
                - color: str (default: 'blue')
                - weight: int (default: 2)
                - fillOpacity: float (default: 0.1)

        Returns:
            None

        Raises:
            FileNotFoundError: If the provided file path does not exist.
            ValueError: If styling parameters are invalid.
        """
        color = kwargs.get("color", "blue")
        if not isinstance(color, str):
            raise ValueError(f"color must be a string, got {type(color)}")

        weight = kwargs.get("weight", 2)
        if not isinstance(weight, int):
            raise ValueError(f"weight must be an integer, got {type(weight)}")

        fill_opacity = kwargs.get("fillOpacity", 0.1)
        if not isinstance(fill_opacity, (int, float)) or not (0 <= fill_opacity <= 1):
            raise ValueError("fillOpacity must be a float between 0 and 1")

        if isinstance(filepath, str) and filepath.startswith("http"):
            folium.GeoJson(
                filepath,
                name=name,
                style_function=lambda feature: {
                    "color": color,
                    "weight": weight,
                    "fillOpacity": fill_opacity,
                },
            ).add_to(self)
        else:
            path = Path(filepath)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {filepath}")
            gdf = gpd.read_file(path)
            folium.GeoJson(
                gdf,
                name=name,
                style_function=lambda feature: {
                    "color": color,
                    "weight": weight,
                    "fillOpacity": fill_opacity,
                },
            ).add_to(self)
