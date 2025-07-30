#!/usr/bin/env python
import unittest
from ipyleaflet import basemaps

from chartops import common


class TestResolveBasemapName(unittest.TestCase):
    def test_resolve_simple_basemap_name(self) -> None:
        basemap_name = "OpenStreetMap"
        basemap = common.resolve_basemap_name(basemap_name)
        expected_basemap = getattr(basemaps, basemap_name)
        self.assertIs(basemap, expected_basemap)

    def test_resolve_nested_basemap_name(self) -> None:
        basemap_name = "Esri.WorldImagery"
        basemap = common.resolve_basemap_name(basemap_name)
        expected_basemap = getattr(getattr(basemaps, "Esri"), "WorldImagery")
        self.assertIs(basemap, expected_basemap)

    def test_resolve_invalid_basemap_name(self) -> None:
        basemap_name = "InvalidBasemap"
        with self.assertRaises(AttributeError):
            common.resolve_basemap_name(basemap_name)

    def test_resolve_invalid_nested_basemap_name(self) -> None:
        basemap_name = "OpenStreetMap.Invalid"
        with self.assertRaises(AttributeError):
            common.resolve_basemap_name(basemap_name)
