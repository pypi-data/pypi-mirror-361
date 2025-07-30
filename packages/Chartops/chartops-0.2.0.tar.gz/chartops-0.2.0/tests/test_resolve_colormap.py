#!/usr/bin/env python
import unittest
from matplotlib.colors import Colormap
from chartops import common


class TestResolveColormap(unittest.TestCase):

    def test_valid_colormap_str(self):
        for name in ["viridis", "plasma", "inferno"]:
            with self.subTest(name=name):
                cmap = common.resolve_colormap(name)
                self.assertIsInstance(cmap, Colormap)

    def test_invalid_colormap_str(self):
        with self.assertRaises(ValueError) as cm:
            common.resolve_colormap("not_a_colormap")
        self.assertIn("Invalid colormap name", str(cm.exception))

    def test_valid_colormap_dict(self):
        colormap_dict = {
            "red": [(0.0, 0.0, 0.0), (0.5, 1.0, 1.0), (1.0, 1.0, 1.0)],
            "green": [(0.0, 0.0, 0.0), (0.75, 1.0, 1.0), (1.0, 1.0, 1.0)],
            "blue": [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)],
        }
        cmap = common.resolve_colormap(colormap_dict)
        self.assertIsInstance(cmap, Colormap)

    def test_invalid_colormap_dicts(self):
        invalid_dicts = [
            {"green": [], "blue": []},
            {"red": "not-a-list", "green": [], "blue": []},
            {"red": [(0.5, 1.0)], "green": [], "blue": []},
            {"red": [(0.0, 0.0), (1.0, 1.0)], "green": [], "blue": []},
            {
                "red": [(1.0, 0.0, 0.0), (0.5, 1.0, 1.0)],
                "green": [(0.0, 0.0, 0.0)],
                "blue": [(0.0, 0.0, 0.0)],
            },
        ]
        for idx, cmap_dict in enumerate(invalid_dicts):
            with self.subTest(i=idx, cmap_dict=cmap_dict):
                with self.assertRaises(ValueError) as cm:
                    common.resolve_colormap(cmap_dict)
                self.assertIn("Invalid colormap dictionary format", str(cm.exception))

    def test_none_colormap(self):
        self.assertIsNone(common.resolve_colormap(None))

    def test_invalid_type(self):
        for invalid_input in [123, 3.14, ["viridis"], object()]:
            with self.subTest(invalid_input=invalid_input):
                with self.assertRaises(TypeError) as cm:
                    common.resolve_colormap(invalid_input)
                self.assertIn("Invalid colormap type", str(cm.exception))
