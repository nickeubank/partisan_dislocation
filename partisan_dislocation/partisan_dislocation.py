import numpy as np
from scipy.spatial import cKDTree
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import random

def random_points_in_polygon(precincts, k,
                             p=None, post_sampling_k=None,
                             dem_vote_count_column="dem",
                             repub_vote_count_column="rep",
                             dem_uniform_swing=0,
                             random_seed=None):
    """
    :param precincts: :class:`geopandas.GeoDataFrame`
    :param k: Effecive num nearest neighbors to consider.
              This is the number of voters you would want to
              consider if you were NOT downsampling.
              If you set k=1,000 and p=0.1, then the actual
              number of representative voter points considered
              in nearest neighbor analysis will be 100.
    :param p: Sampling parameter. (default=None).
              Cannot be combined with `post_sampling_k`.
              Probability of voter inclusion; inverse of number
              of actual voters represented by each representative
              voter.
    :param post_sampling_k: (default=None)
              Number of neighbors considered after sampling.
              Implies a sampling probability and cannot
              be combined with `p`.
    :param dem_vote_count_column: (default="dem")
              Name of column with Democratic vote counts per precinct.
    :param repub_vote_count_column: (default="rep")
              Name of column with Republican vote counts per precinct.
    :param dem_uniform_swing:
    :param random_seed: (default=None)
              Random state or seed passed to numpy.
    """

    # Checks
    if p is not None and post_sampling_k is not None:
        raise ValueError("Cannot use both p and post_sampling_k.")


    gf = pd.DataFrame(columns=['dem','KnnShrDem', 'GEOID10','geometry'])

    for index, row in df.iterrows():

        points_to_add =  np.random.binomial(int(row[election+"D"]), prob)

        points = random_points_in_polygon(points_to_add, row.geometry)

        for point in points:
            gf=gf.append({'dem': 1, 'KnnShrDem': None,
                          'GEOID10': row["GEOID10"], 'geometry': point}, ignore_index=True)

        points_to_add =  np.random.binomial(int(row[election+"R"]), prob)

        points = _make_random_points(points_to_add, row.geometry)

        for point in points:
            gf=gf.append({'dem': 0, 'KnnShrDem': None,
                          'GEOID10': row["GEOID10"], 'geometry': point}, ignore_index=True)


def _make_random_points(number, polygon):
    #Generates number of uniformly distributed points in polygon
    points = []
    min_x, min_y, max_x, max_y = polygon.bounds
    i= 0
    while i < number:
        point = Point(random.uniform(min_x, max_x), random.uniform(min_y, max_y))
        if polygon.contains(point):
            points.append(point)
            i += 1
    return points


def calculate_voter_knn(voter_points, k, target_column='dem'):
    """
        Calculation composition of nearest neigbhors.

        :param voter_points: :class:`geopandas.GeoDataFrame`.
              GeoDataFrame of voter points
        :param k: Num nearest neighbors to consider.
        :param target_column: Feature to average
    """

    tree = cKDTree(list(zip(voter_points["geometry"].x, voter_points["geometry"].y)))

    dd, ii = tree.query(list(zip(voter_points["geometry"].x, voter_points["geometry"].y)), k=k)

    dd = None


    its = 0
    for index, row in voter_points.iterrows():
        row[f'KnnShr{target_column}'] = sum(voter_points[target_column][ii[its]])/k
        its+=1


    voter_points[target_column] = pd.to_numeric(voter_points[target_column])
    voter_points[f"KnnShr{target_column}"] = pd.to_numeric(voter_points[f"KnnShr{target_column}"])

def calculate_dislocation(voter_points, districts,
                          knn_column = 'KnnShrDem',
                          district_voteshare='dem'):
    """
        Calculation difference between knn dem share
        and dem share of assigned district

        :param voter_points: :class:`geopandas.GeoDataFrame`.
              GeoDataFrame of voter points.
        :param voter_points: :class:`geopandas.GeoDataFrame`.
              GeoDataFrame of district polygons.
        :param knn_column: Column of `voter_points` with kNN scores
        :param district_voteshare: Column of `districts` with
              district feature to difference from `knn_columns`.
    """

    districts = districts.to_crs(voter_points.crs)
    voter_points.overlay(districts[[district_voteshare]]
    voter_points['dislocation'] = voter_points[knn_column] -
                                  voter_points[district_voteshare]
