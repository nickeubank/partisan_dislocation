import unittest
import pandas as pd
from shapely.geometry import Polygon
from shapely.geometry import Point
import geopandas as gpd
from partisan_dislocation import random_points_in_polygon
import random

class TestPartisanDislocation(unittest.TestCase):

    def test_random_points_in_polygon_simple_test(self):
        df = gpd.GeoDataFrame({'P2008_D': [0, 1], 'P2008_R': [1, 0],
                               'geometry': [Polygon([(0, 0), (1, 1), (0, 1)]),
                                            Polygon([(0, 0), (1, 1), (0, 1)])]})
        result = random_points_in_polygon(df, p=1)
        benchmark = pd.Series([0, 1], name='Dem')
        pd.testing.assert_series_equal(result["Dem"], benchmark)

    def test_random_points_in_polygon_with_zero_points(self):
        # Assume
         df = gpd.GeoDataFrame({'P2008_D': [0, 1], 'P2008_R': [1, 0],
                               'geometry': [Polygon([]),
                                            Polygon([]})
        # Action
        result = random_points_in_polygon(df, p=1)
        benchpark = pd.Series()

        # Assert
        self.assertEqual(random_points_in_polygon(0,polygons.loc[0]), points, "Generating 0 random points")
"""
    def test_random_points_in_polygon_random_values(self):
        # Assume
        polygons = gpd.GeoSeries([Polygon([(0, 0), (1, 1), (0, 1)]), None, Polygon([])])
        random.seed(0)

        # Action
        points = random_points_in_polygon(2,polygons.loc[0])


        # Assert
        self.assertEqual(points[0], Point(0.4765969541523558, 0.5833820394550312), "Expected value for points generated")

    def test_random_points_in_polygon_append(self):
        # Assume
        polygons = gpd.GeoSeries([Polygon([(0, 0), (1, 1), (0, 1)]), None, Polygon([])])

        # Action
        points = random_points_in_polygon(20,polygons.loc[0])

        # Assert
        self.assertEqual(len(points), 20,  "Expected number of points generated")

"""

if __name__ == '__main__':
    unittest.main()
