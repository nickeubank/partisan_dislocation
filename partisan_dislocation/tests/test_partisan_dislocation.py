import unittest
import pandas as pd
from shapely.geometry import Polygon
from shapely.geometry import Point
import geopandas as gpd
from partisan_dislocation import random_points_in_polygon
from partisan_dislocation import calculate_voter_knn
from partisan_dislocation import calculate_dislocation
import random

class TestPartisanDislocation(unittest.TestCase):

    def test_random_points_in_polygon_simple_test(self):
        df = gpd.GeoDataFrame({'dem': [0, 1], 'rep': [1, 0],
                               'geometry': [Polygon([(0, 0), (1, 1), (0, 1)]),
                                            Polygon([(0, 0), (1, 1), (0, 1)])]},
                               crs='esri:102010')
        result = random_points_in_polygon(df, p=1)
        benchmark = pd.Series([0, 1], name='dem')
        pd.testing.assert_series_equal(result["dem"], benchmark)

    def test_random_points_in_polygon_negative_coordinates(self):
        df = gpd.GeoDataFrame({'dem': [0, 1], 'rep': [1, 0],
                               'geometry': [Polygon([(-1, -1), (2, -3), (4, 7)]),
                                            Polygon([(8, 10), (-5, -3), (6, 9)])]},
                              crs='esri:102010')
        result = random_points_in_polygon(df, p=1)
        benchmark = pd.Series([0, 1], name='dem')
        pd.testing.assert_series_equal(result["dem"], benchmark)

    def test_random_points_in_polygon_float_coordinates(self):
        df = gpd.GeoDataFrame({'dem': [0, 1], 'rep': [1, 0],
                               'geometry': [Polygon([(-1.3, -1.0), (2.8, -3.1), (4.4, 7.9)]),
                                            Polygon([(8.6, 10.5), (-5.3, -3.4), (6.2, 9.1)])]},
                              crs='esri:102010')
        result = random_points_in_polygon(df, p=1)
        benchmark = pd.Series([0, 1], name='dem')
        pd.testing.assert_series_equal(result["dem"], benchmark)

    def test_random_points_in_polygon_column_names(self):
        df = gpd.GeoDataFrame({'dem': [0, 1], 'rep': [1, 0],
                               'geometry': [Polygon([(-1.3, -1.0), (2.8, -3.1), (4.4, 7.9)]),
                                            Polygon([(8.6, 10.5), (-5.3, -3.4), (6.2, 9.1)])]},
                              crs='esri:102010')
        result = random_points_in_polygon(df, p=1,
                                          dem_vote_count='dem',
                                          repub_vote_count='rep')
        benchmark = pd.Series([0, 1], name='dem')
        pd.testing.assert_series_equal(result["dem"], benchmark)
        
    def test_random_points_in_polygon_prob_test(self):
        df = gpd.GeoDataFrame({'dem': [1, 1, 0, 0, 0, 0], 'rep': [0, 0, 1, 1, 1, 1],
                                'geometry': [Polygon([(0, 1), (1, 0), (0, 0)]),
                                             Polygon([(0, -1), (-1, 0), (0, 0)]),
                                             Polygon([(0, 1), (-1, 0), (0, 0)]),
                                             Polygon([(0, -1), (1, 0), (0, 0)]),
                                             Polygon([(1, 0), (1, 1), (0, 1)]),
                                             Polygon([(1, 0), (-1, -1), (0, -1)])]}, crs='esri:102010')
        result = random_points_in_polygon(df, p=1)
        benchmark = pd.Series([1, 1, 0, 0, 0, 0], name='dem')
        pd.testing.assert_series_equal(result['dem'], benchmark)

    def test_calculate_voter_knn_simple_test(self):
        df = gpd.GeoDataFrame({'dem': [1, 1, 0, 0, 0, 0], 'rep': [0, 0, 1, 1, 1, 1], 
                               'geometry': [Polygon([(0, 1), (1, 0), (0, 0)]), 
                                            Polygon([(0, -1), (-1, 0), (0, 0)]),
                                            Polygon([(0, 1), (-1, 0), (0, 0)]),
                                            Polygon([(0, -1), (1, 0), (0, 0)]),
                                            Polygon([(1, 0), (1, 1), (0, 1)]),
                                            Polygon([(1, 0), (-1, -1), (0, -1)])]}, crs='esri:102010')
        df_random_points = random_points_in_polygon(df, p=1)
        df_voter_knn = calculate_voter_knn(df_random_points, k=3)
        
    def test_calculate_dislocation_simple_test(self):
        df = gpd.GeoDataFrame({'dem': [1, 1, 0, 0, 0, 0], 'rep': [0, 0, 1, 1, 1, 1], 
                               'geometry': [Polygon([(0, 1), (1, 0), (0, 0)]), 
                                            Polygon([(0, -1), (-1, 0), (0, 0)]),
                                            Polygon([(0, 1), (-1, 0), (0, 0)]),
                                            Polygon([(0, -1), (1, 0), (0, 0)]),
                                            Polygon([(1, 0), (1, 1), (0, 1)]),
                                            Polygon([(1, 0), (-1, -1), (0, -1)])]}, crs='esri:102010')
        district_test = gpd.GeoDataFrame({'district': [1, 2, 3],
                                          'geometry': [Polygon([(-1, 0), (0, 1), (1, 0)]), 
                                                       Polygon([(0, 1), (1, 1), (1, -1), (0, -1)]),
                                                       Polygon([(-1, 0), (1, 0), (-1, -1)])]}, crs='esri:102010')
        df_random_points = random_points_in_polygon(df, p=1)
        df_voter_knn = calculate_voter_knn(df_random_points, k=3)
        df_dislocation = calculate_dislocation(df_voter_knn, district_test)

    def test_probability_value(self):
        dem_initial = 100 # set initial number of democrats
        p = 0.73 # set the probability
        delta = 0.01 # a small number used to calculate interval for checking if generated dem proportion falls inside the range
        f = 8 # factor to be multiplied with delta
        df = gpd.GeoDataFrame({'dem': [100], 'rep': [200],
                                      'geometry': [Polygon([(0, 1), (1, 0), (0, 0), (1, 1)]), 
                                                   ]}, crs='esri:102010')
        district_test = gpd.GeoDataFrame({'district': [1, 2, 3],
                                      'geometry': [Polygon([(-1, 0), (0, 1), (1, 0)]), 
                                                   Polygon([(0, 1), (1, 1), (1, -1), (0, -1)]),
                                                   Polygon([(-1, 0), (1, 0), (-1, -1)])]}, crs='esri:102010')
        df_random_points = random_points_in_polygon(df, p=0.73)
        dem_proportion = ((df_random_points['dem'].values == 1).sum())/dem_initial
        assert min(p-(f*delta), p+(f*delta)) < dem_proportion < max(p-(f*delta), p+(f*delta))
        
    def test_probability_value(self):
        dem_initial = 1000 # set initial number of democrats
        p = 0.37 # set the probability
        delta = 0.01 # a small number used to calculate interval for checking if generated dem proportion falls inside the range
        f = 6 # factor to be multiplied with delta
        df = gpd.GeoDataFrame({'dem': [1000], 'rep': [2000],
                                      'geometry': [Polygon([(0, 1), (1, 0), (0, 0), (1, 1)]), 
                                                   ]}, crs='esri:102010')
        district_test = gpd.GeoDataFrame({'district': [1, 2, 3],
                                      'geometry': [Polygon([(-1, 0), (0, 1), (1, 0)]), 
                                                   Polygon([(0, 1), (1, 1), (1, -1), (0, -1)]),
                                                   Polygon([(-1, 0), (1, 0), (-1, -1)])]}, crs='esri:102010')
        df_random_points = random_points_in_polygon(df, p=0.37)
        dem_proportion = ((df_random_points['dem'].values == 1).sum())/dem_initial
        assert min(p-(f*delta), p+(f*delta)) < dem_proportion < max(p-(f*delta), p+(f*delta))
        
    #     def test_probability_value(self):
    #         dem_initial = 100000 # set initial number of democrats
    #         p = 0.29 # set the probability
    #         delta = 0.01 # a small number used to calculate interval for checking if generated dem proportion falls inside the range
    #         f = 6 # factor to be multiplied with delta
    #         df = gpd.GeoDataFrame({'dem': [100000], 'rep': [200000],
    #                                       'geometry': [Polygon([(0, 1), (1, 0), (0, 0), (1, 1)]), 
    #                                                    ]}, crs='esri:102010')
    #         district_test = gpd.GeoDataFrame({'district': [1, 2, 3],
    #                                       'geometry': [Polygon([(-1, 0), (0, 1), (1, 0)]), 
    #                                                    Polygon([(0, 1), (1, 1), (1, -1), (0, -1)]),
    #                                                    Polygon([(-1, 0), (1, 0), (-1, -1)])]}, crs='esri:102010')
    #         df_random_points = random_points_in_polygon(df, p=0.29)
    #         dem_proportion = ((df_random_points['dem'].values == 1).sum())/dem_initial
    #         assert min(p-(f*delta), p+(f*delta)) < dem_proportion < max(p-(f*delta), p+(f*delta))


if __name__ == '__main__':
    unittest.main()
