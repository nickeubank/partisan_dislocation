import unittest
import pandas as pd
from shapely.geometry import Polygon
from shapely.geometry import Point
import geopandas as gpd
from partisan_dislocation import random_points_in_polygon
import random

class TestPartisanDislocation(unittest.TestCase):

    def test_random_points_in_polygon_simple_test(self):
        df = gpd.GeoDataFrame({'D': [0, 1], 'R': [1, 0],
                               'geometry': [Polygon([(0, 0), (1, 1), (0, 1)]),
                                            Polygon([(0, 0), (1, 1), (0, 1)])]},
                               crs='esri:102010')
        result = random_points_in_polygon(df, p=1)
        benchmark = pd.Series([0, 1], name='dem')
        pd.testing.assert_series_equal(result["dem"], benchmark)

    def test_random_points_in_polygon_negative_coordinates(self):
        df = gpd.GeoDataFrame({'D': [0, 1], 'R': [1, 0],
                               'geometry': [Polygon([(-1, -1), (2, -3), (4, 7)]),
                                            Polygon([(8, 10), (-5, -3), (6, 9)])]},
                              crs='esri:102010')
        result = random_points_in_polygon(df, p=1)
        benchmark = pd.Series([0, 1], name='dem')
        pd.testing.assert_series_equal(result["dem"], benchmark)

    def test_random_points_in_polygon_float_coordinates(self):
        df = gpd.GeoDataFrame({'D': [0, 1], 'R': [1, 0],
                               'geometry': [Polygon([(-1.3, -1.0), (2.8, -3.1), (4.4, 7.9)]),
                                            Polygon([(8.6, 10.5), (-5.3, -3.4), (6.2, 9.1)])]},
                              crs='esri:102010')
        result = random_points_in_polygon(df, p=1)
        benchmark = pd.Series([0, 1], name='dem')
        pd.testing.assert_series_equal(result["dem"], benchmark)

    def test_random_points_in_polygon_column_names(self):
        df = gpd.GeoDataFrame({'dem': [0, 1], 'repub': [1, 0],
                               'geometry': [Polygon([(-1.3, -1.0), (2.8, -3.1), (4.4, 7.9)]),
                                            Polygon([(8.6, 10.5), (-5.3, -3.4), (6.2, 9.1)])]},
                              crs='esri:102010')
        result = random_points_in_polygon(df, p=1,
                                          dem_vote_count='dem',
                                          repub_vote_count='repub')
        benchmark = pd.Series([0, 1], name='dem')
        pd.testing.assert_series_equal(result["dem"], benchmark)

    # def test_random_points_in_polygon_diff_prob(self):
    #     df = gpd.GeoDataFrame({'P2008_D': [0, 1], 'P2008_R': [1, 0],
    #                            'geometry': [Polygon([(-1.3, -1.0), (2.8, -3.1), (4.4, 7.9)]),
    #                                         Polygon([(8.6, 10.5), (-5.3, -3.4), (6.2, 9.1)])]})
    #     result = random_points_in_polygon(df, p=0.5)
    #     benchmark = pd.Series([0, 1], name='dem')
    #     pd.testing.assert_series_equal(result["dem"], benchmark)


    #     def test_calculate_voter_knn_simple_test(self):
    #         df = gpd.GeoDataFrame({'D': [0, 1], 'R': [1, 0],
    #                                'geometry': [Polygon([(-1.3, -1.0), (2.8, -3.1), (4.4, 7.9)]),
    #                                             Polygon([(8.6, 10.5), (-5.3, -3.4), (6.2, 9.1)])]})
    #         result = random_points_in_polygon(df, p=1)
    #         benchmark = pd.Series([0, 0], name='dem')
    #         pd.testing.assert_series_equal(result["dem"], benchmark)

    # def test_random_points_in_polygon_float_values(self):
    #     df = gpd.GeoDataFrame({'P2008_D': [0, 1], 'P2008_R': [1, 0],
    #                            'geometry': [Point([(0, 0)]),
    #                                         Point([(0, 0)])]})
    #     result = random_points_in_polygon(df, p=1)
    #     benchmark = pd.Series([0, 0], name='dem')
    #     pd.testing.assert_frame_equal(result["dem"], benchmark)
    #
    #
    #
    #
    # def test_random_points_in_polygon_with_zero_points(self):
    #      df = gpd.GeoDataFrame({'P2008_D': [0, 1], 'P2008_R': [1, 0], 'geometry': [Polygon([]), Polygon([])]})
    #     result = random_points_in_polygon(df, p=1)
    #     benchmark = pd.Series([], name='dem')
    #     pd.testing.assert_series_equal(result["dem"], benchmark)
    #
    #
    # def test_random_points_in_polygon_random_values(self):
    #     # Assume
    #     polygons = gpd.GeoSeries([Polygon([(0, 0), (1, 1), (0, 1)]), None, Polygon([])])
    #     random.seed(0)
    #
    #     # Action
    #     points = random_points_in_polygon(2,polygons.loc[0])
    #
    #
    #     # Assert
    #     self.assertEqual(points[0], Point(0.4765969541523558, 0.5833820394550312), "Expected value for points generated")
    #
    # def test_random_points_in_polygon_append(self):
    #     # Assume
    #     polygons = gpd.GeoSeries([Polygon([(0, 0), (1, 1), (0, 1)]), None, Polygon([])])
    #
    #     # Action
    #     points = random_points_in_polygon(20,polygons.loc[0])
    #
    #     # Assert
    #     self.assertEqual(len(points), 20,  "Expected number of points generated")




if __name__ == '__main__':
    unittest.main()
