import numpy as np
from scipy.spatial import cKDTree
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import random


def random_points_in_polygon(precincts, num_districts,
                             k, p=1,
                             dem_vote_count_column="dem",
                             repub_vote_count_column="rep",
                             random_seed=None):
    """
    :param precincts: :class:`geopandas.GeoDataFrame`
    :param k: Effecive num nearest neighbors to consider.
              This is the number of voters you would want to
              consider if you were NOT down sampling.
              If you set k=1,000 and p=0.1, then the actual
              number of representative voter points considered
              in nearest neighbor analysis will be 100.
    :param p: Sampling parameter. (default=1).
              Probability of voter inclusion; inverse of number
              of actual voters represented by each representative
              voter.
    :param dem_vote_count_column: (default="dem")
              Name of column with Democratic vote counts per precinct.
    :param repub_vote_count_column: (default="rep")
              Name of column with Republican vote counts per precinct.
    """

    pass
