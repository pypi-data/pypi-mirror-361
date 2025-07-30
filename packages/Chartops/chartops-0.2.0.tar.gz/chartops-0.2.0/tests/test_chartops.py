#!/usr/bin/env python

"""Tests for `chartops` package."""


import unittest
import tempfile
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from pathlib import Path
from chartops import chartops
from ipyleaflet import LayersControl, GeoJSON, ImageOverlay, WMSLayer, VideoOverlay
from unittest.mock import patch


class TestChartops(unittest.TestCase):
    """Tests for `chartops` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        self.map = chartops.Map()

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_map_initial_state(self) -> None:
        self.assertEqual(len(self.map.layers), 1)

    def test_adding_a_basemap(self) -> None:
        self.map.add_basemap("Esri.WorldImagery")
        self.assertEqual(len(self.map.layers), 2)

    def test_adding_multiple_basemaps(self) -> None:
        self.map.add_basemap("Esri.WorldImagery")
        self.map.add_basemap("OpenTopoMap")
        self.assertEqual(len(self.map.layers), 3)

    def test_adding_an_invalid_basemap(self) -> None:
        with self.assertRaises(AttributeError):
            self.map.add_basemap("Invalid.BasemapName")

    def test_adding_layer_control(self) -> None:
        self.map.add_layer_control()
        control = self.map.controls[-1]
        self.assertIsInstance(control, LayersControl)

    def test_adding_different_position_in_layer_control(self) -> None:
        self.map.add_layer_control("topleft")
        control = self.map.controls[-1]
        position = getattr(control, "position")
        self.assertEqual(position, "topleft")

    def test_adding_invalid_position_in_layer_control(self) -> None:
        with self.assertRaises(ValueError):
            self.map.add_layer_control("invalid")

    def test_adding_layer_control_with_all_positions(self) -> None:
        positions = ["topright", "topleft", "bottomright", "bottomleft"]
        for position in positions:
            map_instance = chartops.Map()
            map_instance.add_layer_control(position)
            control = map_instance.controls[-1]
            self.assertIsInstance(control, LayersControl)
            self.assertEqual(getattr(control, "position"), position)

    def test_adding_a_vector_layer_from_a_url(self) -> None:
        self.map.add_vector(
            "https://github.com/jupyter-widgets/ipyleaflet/raw/master/examples/europe_110.geo.json"
        )
        layer = self.map.layers[-1]
        self.assertIsInstance(layer, GeoJSON)

    def test_adding_a_vector_layer_from_shapefile(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data = {
                "City": ["Tokyo", "New York", "London", "Paris"],
                "Latitude": [35.6895, 40.7128, 51.5074, 48.8566],
                "Longitude": [139.6917, -74.0060, -0.1278, 2.3522],
            }
            df = pd.DataFrame(data)
            gdf = gpd.GeoDataFrame(
                df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude)
            )
            shapefile_path = Path(temp_dir, "temp_shapefile.shp")
            gdf.to_file(shapefile_path)

            self.map.add_vector(shapefile_path)
            layer = self.map.layers[-1]
            self.assertIsInstance(layer, GeoJSON)

    def test_adding_a_vector_layer_from_geojson_file(self):
        from shapely.geometry import Point

        with tempfile.TemporaryDirectory() as temp_dir:
            gdf = gpd.GeoDataFrame(geometry=[Point(0, 0), Point(1, 1)], crs="EPSG:4326")
            geojson_path = Path(temp_dir, "temp.geojson")
            gdf.to_file(geojson_path, driver="GeoJSON")
            self.map.add_vector(geojson_path)
            layer = self.map.layers[-1]
            self.assertIsInstance(layer, GeoJSON)

    def test_adding_a_vector_layer_from_an_invalid_file(self):
        shapefile_path = Path("invalid_shapefile.shp")
        with self.assertRaises(FileNotFoundError):
            self.map.add_vector(shapefile_path)

    def test_adding_a_vector_layer_from_an_invalid_string(self):
        shapefile_path = "invalid_shapefile.shp"
        with self.assertRaises(ValueError):
            self.map.add_vector(shapefile_path)

    def test_adding_a_vector_layer_with_a_custom_color(self) -> None:
        self.map.add_vector(
            "https://github.com/jupyter-widgets/ipyleaflet/raw/master/examples/europe_110.geo.json",
            **{"color": "red"},
        )
        layer = self.map.layers[-1]
        print(layer.style)
        self.assertEqual(layer.style["color"], "red")

    def test_adding_a_vector_layer_with_custom_weight(self) -> None:
        self.map.add_vector(
            "https://github.com/jupyter-widgets/ipyleaflet/raw/master/examples/europe_110.geo.json",
            **{"weight": 5},
        )
        layer = self.map.layers[-1]
        self.assertEqual(layer.style["weight"], 5)

    def test_adding_a_vector_layer_with_custom_fillOpacity(self) -> None:
        self.map.add_vector(
            "https://github.com/jupyter-widgets/ipyleaflet/raw/master/examples/europe_110.geo.json",
            **{"fillOpacity": 0.5},
        )
        layer = self.map.layers[-1]
        self.assertEqual(layer.style["fillOpacity"], 0.5)

    def test_adding_a_vector_layer_with_invalid_color(self) -> None:
        with self.assertRaises(ValueError):
            self.map.add_vector(
                "https://github.com/jupyter-widgets/ipyleaflet/raw/master/examples/europe_110.geo.json",
                **{"color": 123},
            )

    def test_adding_a_vector_layer_with_invalid_weight(self) -> None:
        with self.assertRaises(ValueError):
            self.map.add_vector(
                "https://github.com/jupyter-widgets/ipyleaflet/raw/master/examples/europe_110.geo.json",
                **{"weight": "thick"},
            )

    def test_adding_a_vector_layer_with_invalid_fillOpacity(self) -> None:
        with self.assertRaises(ValueError):
            self.map.add_vector(
                "https://github.com/jupyter-widgets/ipyleaflet/raw/master/examples/europe_110.geo.json",
                **{"fillOpacity": 2},
            )

    def test_add_raster_from_url(self):
        url = (
            "https://github.com/opengeos/datasets/releases/download/raster/dem_90m.tif"
        )
        self.map.add_raster(url, opacity=0.8)
        layer = self.map.layers[-1]
        self.assertEqual(layer.opacity, 0.8)

    def test_add_raster_with_custom_name(self):
        url = (
            "https://github.com/opengeos/datasets/releases/download/raster/dem_90m.tif"
        )
        custom_name = "Elevation Model"
        self.map.add_raster(url, opacity=1.0, name=custom_name)
        layer = self.map.layers[-1]
        self.assertEqual(layer.name, custom_name)

    def test_add_raster_invalid_path(self):
        path = Path("non_existent_file.tif")
        with self.assertRaises(FileNotFoundError):
            self.map.add_raster(path, opacity=0.9)

    def test_add_raster_invalid_opacity_type(self):
        url = (
            "https://github.com/opengeos/datasets/releases/download/raster/dem_90m.tif"
        )
        with self.assertRaises(ValueError):
            self.map.add_raster(url, opacity="high")

    def test_add_raster_invalid_colormap(self):
        url = (
            "https://github.com/opengeos/datasets/releases/download/raster/dem_90m.tif"
        )
        with patch(
            "chartops.common.resolve_colormap",
            side_effect=ValueError("Invalid colormap"),
        ):
            with self.assertRaises(ValueError) as cm:
                self.map.add_raster(url, opacity=0.7, colormap="invalid_colormap")
            self.assertIn("Failed to resolve colormap", str(cm.exception))

    def test_add_image_valid_remote_url(self):
        url = "https://i.imgur.com/06Q1fSz.png"
        bounds = ((-90, -180), (90, 180))
        self.map.add_image(url, bounds=bounds, opacity=0.6)
        layer = self.map.layers[-1]
        self.assertIsInstance(layer, ImageOverlay)

    def test_add_image_valid_local_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            image_data = np.random.rand(50, 50)
            image_path = Path(tmpdir) / "test.png"
            plt.imsave(image_path, image_data)

            bounds = ((-10, -10), (10, 10))
            self.map.add_image(image_path, bounds=bounds, opacity=0.8)
            layer = self.map.layers[-1]
            self.assertIsInstance(layer, ImageOverlay)

    def test_add_image_invalid_bounds_type(self):
        url = "https://i.imgur.com/06Q1fSz.png"
        bounds = "not-a-tuple"
        with self.assertRaises(TypeError):
            self.map.add_image(url, bounds=bounds, opacity=0.5)

    def test_add_image_bounds_wrong_structure(self):
        url = "https://i.imgur.com/06Q1fSz.png"
        bounds = (-90, -180, 90, 180)
        with self.assertRaises(TypeError):
            self.map.add_image(url, bounds=bounds, opacity=0.5)

    def test_add_image_bounds_not_numeric(self):
        url = "https://i.imgur.com/06Q1fSz.png"
        bounds = (("south", "west"), ("north", "east"))
        with self.assertRaises(TypeError):
            self.map.add_image(url, bounds=bounds, opacity=0.5)

    def test_add_image_invalid_opacity_type(self):
        url = "https://i.imgur.com/06Q1fSz.png"
        bounds = ((-90, -180), (90, 180))
        with self.assertRaises(TypeError):
            self.map.add_image(url, bounds=bounds, opacity="high")

    def test_add_image_opacity_out_of_range(self):
        url = "https://i.imgur.com/06Q1fSz.png"
        bounds = ((-90, -180), (90, 180))
        with self.assertRaises(TypeError):
            self.map.add_image(url, bounds=bounds, opacity=1.5)

    def test_add_image_missing_local_file(self):
        path = Path("/nonexistent/image.png")
        bounds = ((-90, -180), (90, 180))
        with self.assertRaises(FileNotFoundError):
            self.map.add_image(path, bounds=bounds, opacity=0.5)

    def test_add_video_valid_remote_url(self):
        url = "https://www.mapbox.com/bites/00188/patricia_nasa.webm"
        bounds = ((-90, -180), (90, 180))
        self.map.add_video(url, bounds=bounds, opacity=0.7)
        layer = self.map.layers[-1]
        self.assertIsInstance(layer, VideoOverlay)

    def test_add_video_valid_local_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = Path(tmpdir) / "test_video.mp4"
            with open(video_path, "wb") as f:
                f.write(b"\x00" * 1024)

            bounds = ((-10, -10), (10, 10))
            self.map.add_video(video_path, bounds=bounds, opacity=0.9)
            layer = self.map.layers[-1]
            self.assertIsInstance(layer, VideoOverlay)

    def test_add_video_invalid_bounds_type(self):
        url = "https://www.mapbox.com/bites/00188/patricia_nasa.webm"
        bounds = "invalid_bounds"
        with self.assertRaises(TypeError):
            self.map.add_video(url, bounds=bounds, opacity=0.5)

    def test_add_video_bounds_wrong_structure(self):
        url = "https://www.mapbox.com/bites/00188/patricia_nasa.webm"
        bounds = (-90, -180, 90, 180)  # Flat tuple instead of nested
        with self.assertRaises(TypeError):
            self.map.add_video(url, bounds=bounds, opacity=0.5)

    def test_add_video_bounds_not_numeric(self):
        url = "https://www.mapbox.com/bites/00188/patricia_nasa.webm"
        bounds = (("south", "west"), ("north", "east"))
        with self.assertRaises(TypeError):
            self.map.add_video(url, bounds=bounds, opacity=0.5)

    def test_add_video_invalid_opacity_type(self):
        url = "https://www.mapbox.com/bites/00188/patricia_nasa.webm"
        bounds = ((-90, -180), (90, 180))
        with self.assertRaises(TypeError):
            self.map.add_video(url, bounds=bounds, opacity="high")

    def test_add_video_opacity_out_of_range(self):
        url = "https://www.mapbox.com/bites/00188/patricia_nasa.webm"
        bounds = ((-90, -180), (90, 180))
        with self.assertRaises(TypeError):
            self.map.add_video(url, bounds=bounds, opacity=1.5)

    def test_add_video_missing_local_file(self):
        path = Path("/nonexistent/video.mp4")
        bounds = ((-90, -180), (90, 180))
        with self.assertRaises(FileNotFoundError):
            self.map.add_video(path, bounds=bounds, opacity=0.5)

    def test_add_wms_layer_valid(self):
        url = "http://mesonet.agron.iastate.edu/cgi-bin/wms/nexrad/n0r.cgi"
        layers = "nexrad-n0r-900913"
        name = "Test"
        format = "image/png"
        transparent = False

        self.map.add_wms_layer(url, layers, name, format, transparent)
        wms_layer = self.map.layers[-1]
        self.assertIsInstance(wms_layer, WMSLayer)
        self.assertEqual(wms_layer.name, name)

    def test_add_wms_layer_invalid_url_type(self):
        with self.assertRaises(TypeError):
            self.map.add_wms_layer(
                url=123,
                layers="layer",
                name="Layer",
                format="image/png",
                transparent=True,
            )

    def test_add_wms_layer_invalid_layers_type(self):
        with self.assertRaises(TypeError):
            self.map.add_wms_layer(
                url="http://mesonet.agron.iastate.edu/cgi-bin/wms/nexrad/n0r.cgi",
                layers=123,
                name="Layer",
                format="image/png",
                transparent=True,
            )

    def test_add_wms_layer_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.map.add_wms_layer(
                url="http://mesonet.agron.iastate.edu/cgi-bin/wms/nexrad/n0r.cgi",
                layers="layer",
                name=123,
                format="image/png",
                transparent=True,
            )

    def test_add_wms_layer_invalid_format_type(self):
        with self.assertRaises(TypeError):
            self.map.add_wms_layer(
                url="http://mesonet.agron.iastate.edu/cgi-bin/wms/nexrad/n0r.cgi",
                layers="layer",
                name="Layer",
                format=123,
                transparent=True,
            )

    def test_add_wms_layer_invalid_transparent_type(self):
        with self.assertRaises(TypeError):
            self.map.add_wms_layer(
                url="http://mesonet.agron.iastate.edu/cgi-bin/wms/nexrad/n0r.cgi",
                layers="layer",
                name="Layer",
                format="image/png",
                transparent="yes",
            )

    def test_add_wms_layer_failure_simulation(self):
        with patch(
            "chartops.chartops.WMSLayer", side_effect=Exception("Failed to initialize")
        ):
            with self.assertRaises(ValueError) as cm:
                self.map.add_wms_layer(
                    url="http://mesonet.agron.iastate.edu/cgi-bin/wms/nexrad/n0r.cgi",
                    layers="layer",
                    name="Layer",
                    format="image/png",
                    transparent=True,
                )
            self.assertIn("Failed to add WMS layer", str(cm.exception))
