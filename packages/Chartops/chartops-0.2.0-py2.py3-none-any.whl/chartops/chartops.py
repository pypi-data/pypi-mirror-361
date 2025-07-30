import geopandas as gpd
from typing import Union, Optional, Tuple
from pathlib import Path
from ipyleaflet import Map as iPyLeafletMap
from ipyleaflet import (
    LayersControl,
    basemap_to_tiles,
    GeoJSON,
    ImageOverlay,
    WMSLayer,
    VideoOverlay,
)
from chartops import common


class Map(iPyLeafletMap):
    def add_basemap(self, basemap_name: str, **kwargs) -> None:
        """
        Add a basemap to the ipyleaflet map.

        Args:
            basemap_name (str): Name of the basemap to add. Resolved with xyzservices.
            **kwargs (dict): Extra kwargs to pass to basemap_to_tiles.

        Returns:
            None
        """
        basemap = common.resolve_basemap_name(basemap_name)
        basemap_tiles = basemap_to_tiles(basemap, **kwargs)
        basemap_tiles.base = True
        basemap_tiles.name = basemap_name
        self.add(basemap_tiles)

    def add_layer_control(self, position: str = "topright") -> None:
        """
        Add a layer control to the map.

        Args:
            position (str, optional): Position of the layer control. Valid positions are "topright", "topleft", "bottomright", "bottomleft". Default is "topright".

        Returns:
            None

        Raises:
            ValueError: If the position is not valid.
        """
        valid_positions = ["topright", "topleft", "bottomright", "bottomleft"]
        if position not in valid_positions:
            raise ValueError(
                f"Invalid position '{position}'. Valid positions are: {valid_positions}"
            )
        self.add(LayersControl(position=position))

    def add_vector(self, filepath: Union[Path, str], name: str = "", **kwargs) -> None:
        """
        Add a vector layer to the map.

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
            FileNotFoundError: If the local filepath does not exist.
            ValueError: If the vector data cannot be read or converted to GeoJSON, or if styling options are invalid.
        """
        if isinstance(filepath, Path) and not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        color = kwargs.get("color", "blue")
        if not isinstance(color, str):
            raise ValueError(f"color must be a string, got {type(color)}")

        weight = kwargs.get("weight", 2)
        if not isinstance(weight, int):
            raise ValueError(f"weight must be an integer, got {type(weight)}")

        fillOpacity = kwargs.get("fillOpacity", 0.1)
        if not isinstance(fillOpacity, (int, float)) or not (0 <= fillOpacity <= 1):
            raise ValueError("fillOpacity must be a float between 0 and 1")

        try:
            gdf = gpd.read_file(filepath)
            geojson = gdf.__geo_interface__
            layer = GeoJSON(
                data=geojson,
                name=name,
                style={"color": color, "weight": weight, "fillOpacity": fillOpacity},
            )
            self.add(layer)
        except Exception as e:
            raise ValueError(f"Failed to add vector layer from {filepath}: {e}")

    def add_raster(
        self,
        url: Union[str, Path],
        opacity: float,
        name: Optional[str] = None,
        colormap: Optional[Union[str, dict]] = None,
        **kwargs,
    ) -> None:
        """
        Add a raster layer to the map using a local or remote tile source.

        Args:
            url (str or Path): Path or URL to the raster file.
            opacity (float): Opacity of the raster layer. Must be between 0 and 1.
            name (str, optional): Name of the layer. Defaults to the stem of the file path.
            colormap (str or dict, optional): Colormap to apply to the raster. Can be a colormap name or a dict. Resolved using `common.resolve_colormap`.
            **kwargs (dict): Additional keyword arguments passed to the tile layer.

        Returns:
            None

        Raises:
            FileNotFoundError: If the local raster file does not exist.
            ValueError: If the opacity is not valid or raster layer cannot be added.
        """
        from localtileserver import TileClient, get_leaflet_tile_layer

        if isinstance(url, Path) and not url.exists():
            raise FileNotFoundError(f"Raster file not found: {url}")

        if not isinstance(opacity, (int, float)) or not (0 <= opacity <= 1):
            raise ValueError("opacity must be a float between 0 and 1")

        try:
            colormap_arg = common.resolve_colormap(colormap)
        except Exception as e:
            raise ValueError(f"Failed to resolve colormap: {e}")

        try:
            client = TileClient(str(url))
        except Exception as e:
            raise ValueError(f"Failed to create TileClient from {url}: {e}")

        try:
            self.center = client.center()
            self.zoom = client.default_zoom
            tile_layer = get_leaflet_tile_layer(
                client, colormap=colormap_arg, opacity=opacity, **kwargs
            )
            tile_layer.name = name or ""
            self.add(tile_layer)
        except Exception as e:
            raise ValueError(f"Failed to add raster layer: {e}")

    def add_image(
        self,
        url: Union[str, Path],
        bounds: Tuple[Tuple[float, float], Tuple[float, float]],
        opacity: float,
        **kwargs,
    ) -> None:
        """
        Add a static image overlay to the map.

        Args:
            url (str or Path): URL or path to the image to overlay.
            bounds (tuple): A tuple of ((south, west), (north, east)) coordinates defining the bounding box of the image.
            opacity (float): Opacity of the image overlay. Must be between 0 and 1.
            **kwargs (dict): Additional keyword arguments passed to ImageOverlay.

        Returns:
            None

        Raises:
            ValueError: If the bounds are not in correct format or opacity is invalid.
            FileNotFoundError: If the local image path does not exist.
        """
        if isinstance(url, Path) and not url.exists():
            raise FileNotFoundError(f"Image file not found: {url}")

        if (
            not isinstance(bounds, tuple)
            or len(bounds) != 2
            or not all(isinstance(pair, tuple) and len(pair) == 2 for pair in bounds)
            or not all(
                isinstance(coord, (int, float)) for pair in bounds for coord in pair
            )
        ):
            raise TypeError(
                "bounds must be a tuple of two (lat, lon) tuples: ((south, west), (north, east))"
            )

        if not isinstance(opacity, (int, float)) or not (0 <= opacity <= 1):
            raise TypeError("opacity must be a float between 0 and 1")

        try:
            image = ImageOverlay(url=str(url), bounds=bounds, opacity=opacity, **kwargs)
            self.add(image)
        except Exception as e:
            raise ValueError(f"Failed to add image overlay: {e}")

    def add_video(
        self,
        url: Union[str, Path],
        bounds: Tuple[Tuple[float, float], Tuple[float, float]],
        opacity: float,
        **kwargs,
    ) -> None:
        """
        Add a video overlay to the map.

        Args:
            url (str or Path): URL or path to the video to overlay.
            bounds (tuple): A tuple of ((south, west), (north, east)) coordinates defining the bounding box of the video.
            opacity (float): Opacity of the video overlay. Must be between 0 and 1.
            **kwargs (dict): Additional keyword arguments passed to VideoOverlay.

        Returns:
            None

        Raises:
            ValueError: If the bounds are not in correct format or opacity is invalid.
            FileNotFoundError: If the local video path does not exist.
        """
        if isinstance(url, Path) and not url.exists():
            raise FileNotFoundError(f"Video file not found: {url}")

        if (
            not isinstance(bounds, tuple)
            or len(bounds) != 2
            or not all(isinstance(pair, tuple) and len(pair) == 2 for pair in bounds)
            or not all(
                isinstance(coord, (int, float)) for pair in bounds for coord in pair
            )
        ):
            raise TypeError(
                "bounds must be a tuple of two (lat, lon) tuples: ((south, west), (north, east))"
            )

        if not isinstance(opacity, (int, float)) or not (0 <= opacity <= 1):
            raise TypeError("opacity must be a float between 0 and 1")

        try:
            video = VideoOverlay(url=str(url), bounds=bounds, opacity=opacity, **kwargs)
            self.add(video)
        except Exception as e:
            raise ValueError(f"Failed to add video overlay: {e}")

    def add_wms_layer(
        self, url: str, layers: str, name: str, format: str, transparent: bool, **kwargs
    ) -> None:
        """
        Add a WMS (Web Map Service) layer to the map.

        Args:
            url (str): Base URL of the WMS service.
            layers (str): Comma-separated list of layer names to request from the service.
            name (str): Name of the layer to show in the map.
            format (str): Image format for the WMS tiles (e.g., 'image/png').
            transparent (bool): Whether the WMS tiles should support transparency.
            **kwargs (dict): Additional keyword arguments passed to the WMSLayer.

        Returns:
            None

        Raises:
            TypeError: If any of the required parameters are not of the expected type.
            ValueError: If the WMS layer cannot be created or added.
        """
        if not isinstance(url, str):
            raise TypeError(f"url must be a string, got {type(url)}")
        if not isinstance(layers, str):
            raise TypeError(f"layers must be a string, got {type(layers)}")
        if not isinstance(name, str):
            raise TypeError(f"name must be a string, got {type(name)}")
        if not isinstance(format, str):
            raise TypeError(f"format must be a string, got {type(format)}")
        if not isinstance(transparent, bool):
            raise TypeError(f"transparent must be a boolean, got {type(transparent)}")

        try:
            wms = WMSLayer(
                url=url,
                layers=layers,
                format=format,
                transparent=transparent,
                **kwargs,
            )
            wms.name = name
            self.add(wms)
        except Exception as e:
            raise ValueError(f"Failed to add WMS layer: {e}")
