import numpy as np
from scipy.spatial import cKDTree
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import random

def random_points_in_polygon(precincts, p,
                             dem_vote_count_column="dem",
                             repub_vote_count_column="rep",
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
    gf = pd.DataFrame(columns=['dem','KnnShrDem', 'geometry'])

    for index, row in precincts.iterrows():

        # Loop over dems and republicans
        for party in [dem_vote_count_column, repub_vote_count_column]:
            points_to_add =  np.random.binomial(int(row[party]), p)

            points = _make_random_points(points_to_add, row.geometry)

            for point in points:
                if party == "D":
                    dem_value = 1
                else: 
                    dem_value = 0
                
                gf=gf.append({'dem': dem_value, 'KnnShrDem': None,
                              'geometry': point}, 
                             ignore_index=True)

    # Return gf, which should be a geodataframe of points
    return gf
                
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
                          knn_column='KnnShrDem',
                          dem_column='dem'):
    """
        Calculation difference between knn dem share
        and dem share of assigned district

        :param voter_points: :class:`geopandas.GeoDataFrame`.
              GeoDataFrame of voter points.
        :param voter_points: :class:`geopandas.GeoDataFrame`.
              GeoDataFrame of district polygons.
        :param knn_column: Column of `voter_points` with kNN scores
    """

    # Put both geodataframes in a common projection
    districts = districts.to_crs(voter_points.crs)
    
    # Calculate district dem share
    districts.sjoin(voter_points[[dem_column]], how='left')
    
    # Collapse to one row per district with avg of `dem` as new column
    # Call new column district_demshare


    
    # Merge voters with districts to get 
    voter_points.sjoin(districts[['district_demshare']]
    voter_points['dislocation'] = voter_points[knn_column] -
                                  voter_points[district_voteshare]

    return voter_points
