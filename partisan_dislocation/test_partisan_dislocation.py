import unittest
import pandas as pd
from shapely.geometry import Polygon
from shapely.geometry import Point
import geopandas as gpd
from partisan_dislocation import random_points_in_polygon
import random

class TestPartisanDislocation(unittest.TestCase):

    def test_random_points_in_polygon_with_zero_points(self):
        polygons = gpd.GeoSeries([Polygon([(0, 0), (1, 1), (0, 1)]), None, Polygon([])])
        points = []
        self.assertEqual(random_points_in_polygon(0,polygons.loc[0]), points, "Generating 0 random points")

    def test_random_points_in_polygon_random_values(self):
        polygons = gpd.GeoSeries([Polygon([(0, 0), (1, 1), (0, 1)]), None, Polygon([])])
        random.seed(0)
        points = random_points_in_polygon(2,polygons.loc[0])
        self.assertEqual(points[0], Point(0.4765969541523558, 0.5833820394550312), "Expected value for points generated")

    def test_random_points_in_polygon_append(self):
        polygons = gpd.GeoSeries([Polygon([(0, 0), (1, 1), (0, 1)]), None, Polygon([])])
        points = random_points_in_polygon(20,polygons.loc[0], "Expected number of points generated")
        self.assertEqual(len(points), 20)

if __name__ == '__main__':
    unittest.main()
