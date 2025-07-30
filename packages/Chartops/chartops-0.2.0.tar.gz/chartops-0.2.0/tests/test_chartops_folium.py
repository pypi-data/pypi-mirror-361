import unittest
import tempfile
from pathlib import Path

from chartops.folium import Map
import folium
import pandas as pd
import geopandas as gpd


class TestChartopsFolium(unittest.TestCase):
    def setUp(self):
        self.map = Map()

    def test_map_initial_state(self):
        self.assertIsInstance(self.map, folium.Map)

    def test_adding_a_basemap(self):
        self.map.add_basemap("Esri.WorldImagery")
        self.assertTrue(
            any(
                isinstance(child, folium.TileLayer)
                for child in self.map._children.values()
            )
        )

    def test_adding_multiple_basemaps(self):
        self.map.add_basemap("Esri.WorldImagery")
        self.map.add_basemap("OpenTopoMap")
        tile_layers = [
            child
            for child in self.map._children.values()
            if isinstance(child, folium.TileLayer)
        ]
        self.assertGreaterEqual(len(tile_layers), 2)

    def test_adding_an_invalid_basemap(self):
        with self.assertRaises(AttributeError):
            self.map.add_basemap("Invalid.BasemapName")

    def test_adding_layer_control(self):
        self.map.add_layer_control()
        controls = [
            child
            for child in self.map._children.values()
            if isinstance(child, folium.LayerControl)
        ]
        self.assertTrue(len(controls) > 0)

    def test_adding_a_vector_layer_from_url(self):
        self.map.add_vector(
            "https://github.com/jupyter-widgets/ipyleaflet/raw/master/examples/europe_110.geo.json",
            name="Europe",
        )
        geojsons = [
            child
            for child in self.map._children.values()
            if isinstance(child, folium.GeoJson)
        ]
        self.assertTrue(len(geojsons) > 0)

    def test_adding_vector_layer_from_shapefile(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data = {
                "City": ["Tokyo", "New York", "London", "Paris"],
                "Latitude": [35.6895, 40.7128, 51.5074, 48.8566],
                "Longitude": [139.6917, -74.0060, -0.1278, 2.3522],
            }
            df = pd.DataFrame(data)
            gdf = gpd.GeoDataFrame(
                df,
                geometry=gpd.points_from_xy(df.Longitude, df.Latitude),
                crs="EPSG:4326",
            )
            shapefile_path = Path(temp_dir) / "cities.shp"
            gdf.to_file(shapefile_path)

            self.map.add_vector(shapefile_path, name="Cities")
            geojsons = [
                child
                for child in self.map._children.values()
                if isinstance(child, folium.GeoJson)
            ]
            self.assertTrue(len(geojsons) > 0)

    def test_adding_vector_layer_from_geojson_file(self):
        from shapely.geometry import Point

        with tempfile.TemporaryDirectory() as temp_dir:
            gdf = gpd.GeoDataFrame(geometry=[Point(0, 0), Point(1, 1)], crs="EPSG:4326")
            geojson_path = Path(temp_dir) / "points.geojson"
            gdf.to_file(geojson_path, driver="GeoJSON")
            self.map.add_vector(geojson_path, name="Points")
            geojsons = [
                child
                for child in self.map._children.values()
                if isinstance(child, folium.GeoJson)
            ]
            self.assertTrue(len(geojsons) > 0)

    def test_adding_vector_layer_from_invalid_file(self):
        with self.assertRaises(FileNotFoundError):
            self.map.add_vector("non_existent.shp", name="Invalid")

    def test_adding_vector_layer_with_custom_style(self):
        self.map.add_vector(
            "https://github.com/jupyter-widgets/ipyleaflet/raw/master/examples/europe_110.geo.json",
            name="Styled",
            color="red",
            weight=5,
            fillOpacity=0.3,
        )
        geojsons = [
            child
            for child in self.map._children.values()
            if isinstance(child, folium.GeoJson)
        ]
        self.assertTrue(len(geojsons) > 0)

    def test_adding_vector_layer_with_invalid_weight(self):
        with self.assertRaises(ValueError):
            self.map.add_vector(
                "https://github.com/jupyter-widgets/ipyleaflet/raw/master/examples/europe_110.geo.json",
                name="Invalid",
                weight="heavy",
            )

    def test_adding_vector_layer_with_invalid_fill_opacity(self):
        with self.assertRaises(ValueError):
            self.map.add_vector(
                "https://github.com/jupyter-widgets/ipyleaflet/raw/master/examples/europe_110.geo.json",
                name="Invalid",
                fillOpacity=2.0,
            )

    def test_adding_vector_layer_with_invalid_color_type(self):
        with self.assertRaises(ValueError):
            self.map.add_vector(
                "https://github.com/jupyter-widgets/ipyleaflet/raw/master/examples/europe_110.geo.json",
                name="Invalid",
                color=123,
            )
