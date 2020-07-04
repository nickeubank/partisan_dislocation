# import libraries
import numpy as np
from scipy.spatial import cKDTree
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from shapely.geometry import Polygon
import random
import os

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


def random_points_in_polygon(precincts, p=0.01,
                             dem_vote_count_column="D",
                             repub_vote_count_column="R",
                             dem_uniform_swing=0,
                             random_seed=None):
    """
    :param precincts: :class:`geopandas.GeoDataFrame`
                      This is a polygon shapefile with vote totals.
    :param p: Sampling parameter.
              Probability of voter inclusion; inverse of number
              of actual voters represented by each representative
              voter.
    :param dem_vote_count_column: (default="dem")
              Name of column with Democratic vote counts per precinct.
    :param repub_vote_count_column: (default="rep")
              Name of column with Republican vote counts per precinct.
    :param random_seed: (default=None)
              Random state or seed passed to numpy.
    """
    # Make master dataframe
    gf = gpd.GeoDataFrame(columns=['Dem', 'KnnShrDem', 'geometry'])
    election = "P2008_"
    for index, row in precincts.iterrows():
        # Loop over dems and republicans
        for party in [dem_vote_count_column, repub_vote_count_column]:
            points_to_add = np.random.binomial(int(row[election + party]), p)
            points = _make_random_points(points_to_add, row.geometry)
            for point in points:
                if party == "D":
                    dem_value = 1
                else:
                    dem_value = 0

                gf = gf.append({'Dem': dem_value, 'KnnShrDem': None, 'geometry': point}, ignore_index=True)

    # Do string manipulations to separate out x and y coordinate from point attribute in geometry column
    gf['geometry'] = gf['geometry'].astype(str)
    gf['geometry'] = gf['geometry'].str.strip()
    gf['geometry'] = gf['geometry'].str.replace('POINT \(', '')
    gf['geometry'] = gf['geometry'].str.replace('\)', '')
    gf[['x', 'y']] = gf.geometry.str.split(' ', expand=True)
    gf.drop(columns=['geometry'], inplace=True)
    gf[['Dem', 'x', 'y']] = gf[['Dem', 'x', 'y']].apply(pd.to_numeric)
    gf['KnnShrDem'] = gf['KnnShrDem'].astype(None)

    return gf

df = gpd.GeoDataFrame({'P2008_D': [0, 1], 'P2008_R': [1, 0],
                               'geometry': [Polygon([(0, 0), (1, 1), (0, 1)]),
                                            Polygon([(0, 0), (1, 1), (0, 1)])]})
result = random_points_in_polygon(df, p=1)
benchmark = pd.Series([0, 1], name='Dem')
print(pd.Series.equals(result['Dem'], benchmark))
