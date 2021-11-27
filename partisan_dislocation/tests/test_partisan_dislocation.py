import unittest
import pandas as pd
from shapely.geometry import Polygon
from shapely.geometry import Point
import geopandas as gpd
from partisan_dislocation import random_points_in_polygon
from partisan_dislocation import calculate_voter_knn
from partisan_dislocation import calculate_dislocation


class TestPartisanDislocation(unittest.TestCase):
    def test_random_points_in_polygon_simple_test(self):
        df = gpd.GeoDataFrame(
            {
                "dem": [0, 1],
                "rep": [1, 0],
                "geometry": [
                    Polygon([(0, 0), (1, 1), (0, 1)]),
                    Polygon([(0, 0), (1, 1), (0, 1)]),
                ],
            },
            crs="esri:102010",
        )
        result = random_points_in_polygon(df, p=1)
        benchmark = pd.Series([0, 1], name="dem")
        pd.testing.assert_series_equal(result["dem"], benchmark)

    def test_random_points_in_polygon_seed(self):
        df = gpd.GeoDataFrame(
            {
                "dem": [0, 1],
                "rep": [1, 0],
                "geometry": [
                    Polygon([(0, 0), (1, 1), (0, 1)]),
                    Polygon([(0, 0), (1, 1), (0, 1)]),
                ],
            },
            crs="esri:102010",
        )
        result1 = random_points_in_polygon(df, p=0.5, random_seed=47)
        result2 = random_points_in_polygon(df, p=0.5, random_seed=47)
        pd.testing.assert_frame_equal(result1, result2)

    def test_uniformswing(self):
        df = gpd.GeoDataFrame(
            {
                "dem": [10000],
                "rep": [20000],
                "geometry": [
                    Polygon([(0, 1), (1, 0), (0, 0), (1, 1)]),
                ],
            },
            crs="esri:102010",
        )
        # No swing
        df_random_points = random_points_in_polygon(df, p=0.5, uniform_swing_to_dems=0)
        assert (
            df_random_points["dem"].mean() > 0.29
            and df_random_points["dem"].mean() < 0.38
        )

        # With swing
        df_random_points = random_points_in_polygon(
            df, p=0.5, uniform_swing_to_dems=1 / 6
        )

        assert (
            df_random_points["dem"].mean() > 0.47
            and df_random_points["dem"].mean() < 0.53
        )

    def test_random_points_in_polygon_negative_coordinates(self):
        df = gpd.GeoDataFrame(
            {
                "dem": [0, 1],
                "rep": [1, 0],
                "geometry": [
                    Polygon([(-1, -1), (2, -3), (4, 7)]),
                    Polygon([(8, 10), (-5, -3), (6, 9)]),
                ],
            },
            crs="esri:102010",
        )
        result = random_points_in_polygon(df, p=1)
        benchmark = pd.Series([0, 1], name="dem")
        pd.testing.assert_series_equal(result["dem"], benchmark)

    def test_random_points_in_polygon_float_coordinates(self):
        df = gpd.GeoDataFrame(
            {
                "dem": [0, 1],
                "rep": [1, 0],
                "geometry": [
                    Polygon([(-1.3, -1.0), (2.8, -3.1), (4.4, 7.9)]),
                    Polygon([(8.6, 10.5), (-5.3, -3.4), (6.2, 9.1)]),
                ],
            },
            crs="esri:102010",
        )
        result = random_points_in_polygon(df, p=1)
        benchmark = pd.Series([0, 1], name="dem")
        pd.testing.assert_series_equal(result["dem"], benchmark)

    def test_random_points_in_polygon_column_names(self):
        df = gpd.GeoDataFrame(
            {
                "dem": [0, 1],
                "rep": [1, 0],
                "geometry": [
                    Polygon([(-1.3, -1.0), (2.8, -3.1), (4.4, 7.9)]),
                    Polygon([(8.6, 10.5), (-5.3, -3.4), (6.2, 9.1)]),
                ],
            },
            crs="esri:102010",
        )
        result = random_points_in_polygon(
            df, p=1, dem_vote_count="dem", repub_vote_count="rep"
        )
        benchmark = pd.Series([0, 1], name="dem")
        pd.testing.assert_series_equal(result["dem"], benchmark)

    def test_random_points_in_polygon_prob_test(self):
        df = gpd.GeoDataFrame(
            {
                "dem": [1, 1, 0, 0, 0, 0],
                "rep": [0, 0, 1, 1, 1, 1],
                "geometry": [
                    Polygon([(0, 1), (1, 0), (0, 0)]),
                    Polygon([(0, -1), (-1, 0), (0, 0)]),
                    Polygon([(0, 1), (-1, 0), (0, 0)]),
                    Polygon([(0, -1), (1, 0), (0, 0)]),
                    Polygon([(1, 0), (1, 1), (0, 1)]),
                    Polygon([(1, 0), (-1, -1), (0, -1)]),
                ],
            },
            crs="esri:102010",
        )
        result = random_points_in_polygon(df, p=1)
        benchmark = pd.Series([1, 1, 0, 0, 0, 0], name="dem")
        pd.testing.assert_series_equal(result["dem"], benchmark)

    def test_calculate_voter_knn_simple_test(self):
        df = gpd.GeoDataFrame(
            {
                "dem": [1, 1, 0, 0, 0, 0],
                "rep": [0, 0, 1, 1, 1, 1],
                "geometry": [
                    Polygon([(0, 1), (1, 0), (0, 0)]),
                    Polygon([(0, -1), (-1, 0), (0, 0)]),
                    Polygon([(0, 1), (-1, 0), (0, 0)]),
                    Polygon([(0, -1), (1, 0), (0, 0)]),
                    Polygon([(1, 0), (1, 1), (0, 1)]),
                    Polygon([(1, 0), (-1, -1), (0, -1)]),
                ],
            },
            crs="esri:102010",
        )
        df_random_points = random_points_in_polygon(df, p=1)
        df_voter_knn = calculate_voter_knn(df_random_points, k=3)

    def test_calculate_dislocation_simple_test(self):
        df = gpd.GeoDataFrame(
            {
                "dem": [1, 1, 0, 0, 0, 0],
                "rep": [0, 0, 1, 1, 1, 1],
                "geometry": [
                    Polygon([(0, 1), (1, 0), (0, 0)]),
                    Polygon([(0, -1), (-1, 0), (0, 0)]),
                    Polygon([(0, 1), (-1, 0), (0, 0)]),
                    Polygon([(0, -1), (1, 0), (0, 0)]),
                    Polygon([(1, 0), (1, 1), (0, 1)]),
                    Polygon([(1, 0), (-1, -1), (0, -1)]),
                ],
            },
            crs="esri:102010",
        )
        district_test = gpd.GeoDataFrame(
            {
                "district": [1, 2, 3],
                "geometry": [
                    Polygon([(-1, 0), (0, 1), (1, 0)]),
                    Polygon([(0, 1), (1, 1), (1, -1), (0, -1)]),
                    Polygon([(-1, 0), (1, 0), (-1, -1)]),
                ],
            },
            crs="esri:102010",
        )
        df_random_points = random_points_in_polygon(df, p=1)
        df_voter_knn = calculate_voter_knn(df_random_points, k=3)
        df_dislocation = calculate_dislocation(df_voter_knn, district_test)

    def test_calculation_of_knn(self):
        df = gpd.GeoDataFrame(
            {
                "dem": [1, 0, 1, 0, 0, 1],
                "geometry": [
                    Point(-3, 0),
                    Point(-2, 0),
                    Point(-1, 0),
                    Point(0, 0),
                    Point(1, 0),
                    Point(2, 0),
                ],
            },
            crs="esri:102010",
        )
        pd.testing.assert_series_equal(
            calculate_voter_knn(df, k=2)["knn_shr_dem"],
            pd.Series([0.5, 1, 0, 0.5, 0.5, 0], name="knn_shr_dem"),
        )

    def test_calculation_of_dislocation(self):
        df = gpd.GeoDataFrame(
            {
                "dem": [1, 0, 1, 0, 0, 1],
                "geometry": [
                    Point(-3, 0),
                    Point(-2, 0),
                    Point(-1, 0),
                    Point(0, 0),
                    Point(1, 0),
                    Point(2, 0),
                ],
            },
            crs="esri:102010",
        )
        districts = gpd.GeoDataFrame(
            {
                "dist": [1, 0],
                "geometry": [
                    Polygon([[-3.5, -1], [-3.5, 1], [-1.5, 1], [-1.5, -1], [-3.5, -1]]),
                    Polygon([[-1.5, 1], [-1.5, -1], [2.5, -1], [2.5, 1], [-1.5, 1]]),
                ],
            },
            crs="esri:102010",
        )
        knns = calculate_voter_knn(df, k=2)
        dislocation = calculate_dislocation(knns, districts)

        expected_result = pd.DataFrame(
            {
                "district_dem_share": [0.5] * 6,
                "partisan_dislocation": [0, -0.5, 0.5, 0, 0, 0.5],
            }
        )

        pd.testing.assert_frame_equal(
            dislocation[["district_dem_share", "partisan_dislocation"]], expected_result
        )

    def test_adding_district_name(self):
        df = gpd.GeoDataFrame(
            {
                "dem": [1, 0, 1, 0, 0, 1],
                "geometry": [
                    Point(-3, 0),
                    Point(-2, 0),
                    Point(-1, 0),
                    Point(0, 0),
                    Point(1, 0),
                    Point(2, 0),
                ],
            },
            crs="esri:102010",
        )
        districts = gpd.GeoDataFrame(
            {
                "dist": [1, 0],
                "geometry": [
                    Polygon([[-3.5, -1], [-3.5, 1], [-1.5, 1], [-1.5, -1], [-3.5, -1]]),
                    Polygon([[-1.5, 1], [-1.5, -1], [2.5, -1], [2.5, 1], [-1.5, 1]]),
                ],
                "dist_name": ["a", "b"],
            },
            crs="esri:102010",
        )
        knns = calculate_voter_knn(df, k=2)
        dislocation = calculate_dislocation(
            knns, districts, district_id_col="dist_name"
        )

        expected_result = pd.DataFrame(
            {
                "district_dem_share": [0.5] * 6,
                "partisan_dislocation": [0, -0.5, 0.5, 0, 0, 0.5],
                "dist_name": ["a", "a", "b", "b", "b", "b"],
            }
        )

        pd.testing.assert_frame_equal(
            dislocation[["district_dem_share", "partisan_dislocation", "dist_name"]],
            expected_result,
        )


class TestPartisanDislocationProbabilities(unittest.TestCase):
    def test_probability_value_small(self):
        p = 0.73  # set the probability
        delta = 0.06  # a small number used to calculate interval for checking if generated dem proportion falls inside the range
        f = 8  # factor to be multiplied with delta
        df = gpd.GeoDataFrame(
            {
                "dem": [100],
                "rep": [200],
                "geometry": [
                    Polygon([(0, 1), (1, 0), (0, 0), (1, 1)]),
                ],
            },
            crs="esri:102010",
        )
        df_random_points = random_points_in_polygon(df, p=0.73)

        for party in ["dem", "rep"]:
            relevant_dem_value = 1 if party == "dem" else 0
            proportion = (df_random_points["dem"] == relevant_dem_value).sum() / df.loc[
                0, party
            ]
            assert abs(proportion - p) < f * delta

    def test_probability_value_medium(self):
        p = 0.37  # set the probability
        delta = 0.04  # 1 standard deviation
        f = 8  # factor to be multiplied with delta
        df = gpd.GeoDataFrame(
            {
                "dem": [1000],
                "rep": [2000],
                "geometry": [
                    Polygon([(0, 1), (1, 0), (0, 0), (1, 1)]),
                ],
            },
            crs="esri:102010",
        )
        df_random_points = random_points_in_polygon(df, p=0.37)

        for party in ["dem", "rep"]:
            relevant_dem_value = 1 if party == "dem" else 0
            proportion = (df_random_points["dem"] == relevant_dem_value).sum() / df.loc[
                0, party
            ]
            assert abs(proportion - p) < f * delta

    def test_probability_value_large(self):
        p = 0.29  # set the probability
        delta = 0.015  # 1 standard error of mean
        f = 8  # factor to be multiplied with delta
        df = gpd.GeoDataFrame(
            {
                "dem": [10000],
                "rep": [20000],
                "geometry": [
                    Polygon([(0, 1), (1, 0), (0, 0), (1, 1)]),
                ],
            },
            crs="esri:102010",
        )
        df_random_points = random_points_in_polygon(df, p=0.29)

        for party in ["dem", "rep"]:
            relevant_dem_value = 1 if party == "dem" else 0
            proportion = (df_random_points["dem"] == relevant_dem_value).sum() / df.loc[
                0, party
            ]
            assert abs(proportion - p) < f * delta


class TestPartisanDislocationExceptions(unittest.TestCase):
    def test_zero_area_polygon_error(self):
        df = gpd.GeoDataFrame(
            {
                "dem": [0, 1],
                "rep": [1, 0],
                "geometry": [
                    Polygon([(0, 0), (0, 0), (0, 0)]),
                    Polygon([(0, 0), (1, 1), (0, 1)]),
                ],
            },
            crs="esri:102010",
        )
        with self.assertRaises(ValueError):
            random_points_in_polygon(df, p=1)

    def test_no_crs(self):
        df = gpd.GeoDataFrame(
            {
                "dem": [0, 1],
                "rep": [1, 0],
                "geometry": [
                    Polygon([(0, 0), (0, 0), (0, 0)]),
                    Polygon([(0, 0), (1, 1), (0, 1)]),
                ],
            }
        )
        with self.assertRaises(ValueError):
            random_points_in_polygon(df, p=1)


if __name__ == "__main__":
    unittest.main()
