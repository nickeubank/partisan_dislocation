import numpy as np
from scipy.spatial import cKDTree
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import random

#precincts = gdp.read_



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

    total_voters = precincts[dem_vote_count_column].sum() + precincts[rep_vote_count_column].sum()
    voters_per_district = num_districts / total_voters


    gf = pd.DataFrame(columns=['dem','KnnShrDem', 'GEOID10','geometry'])

    for index, row in df.iterrows():

        points_to_add =  np.random.binomial(int(row[election+"D"]), prob)

        points = random_points_in_polygon(points_to_add, row.geometry)

        for point in points:
            gf=gf.append({'dem': 1, 'KnnShrDem': None,
                          'GEOID10': row["GEOID10"], 'geometry': point}, ignore_index=True)

        points_to_add =  np.random.binomial(int(row[election+"R"]), prob)

        points = random_points_in_polygon(points_to_add, row.geometry)

        for point in points:
            gf=gf.append({'dem': 0, 'KnnShrDem': None,
                          'GEOID10': row["GEOID10"], 'geometry': point}, ignore_index=True)


def random_points_in_polygon(number, polygon):
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
