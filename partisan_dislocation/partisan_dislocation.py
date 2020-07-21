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
    "Generates number of uniformly distributed points in polygon"
    points = []
    min_x, min_y, max_x, max_y = polygon.bounds
    i= 0
    while i < number:
        point = Point(random.uniform(min_x, max_x), random.uniform(min_y, max_y))
        attempt = 0
        if polygon.contains(point):
            points.append(point)
            i += 1
            attempt += 1
            if attempt > 100000:
                raise ValueError("Could not generate a random point in one of your precincts."\
                                 " Check for zero-area precincts or invalid geometries.")
    return points

def random_points_in_polygon(precincts, p=0.01,
                             dem_vote_count="dem",
                             repub_vote_count="rep",
                             random_seed=None):
    """
    :param precincts: :class:`geopandas.GeoDataFrame`
                      This is a polygon shapefile with vote totals.
    :param p: Sampling parameter.
              Probability of voter inclusion; inverse of number
              of actual voters represented by each representative
              voter.
    :param dem_vote_count: (default="dem")
              Name of column with Democratic vote counts per precinct.
    :param repub_vote_count: (default="rep")
              Name of column with Republican vote counts per precinct.
    :param random_seed: (default=None)
              Random state or seed passed to numpy.

    """
    
    # Make sure projected!
    if precincts.crs is None: 
        raise ValueError("Precincts must have a defined CRS")
    
    # Set seed if passed.
    if random_seed is not None:
        np.random.seed(random_seed)
    
    # Make master dataframe
    gf = gpd.GeoDataFrame(columns=['dem', 'geometry'])

    for index, row in precincts.iterrows():
        # Loop over dems and republicans
        for party in [dem_vote_count, repub_vote_count]:
            points_to_add = np.random.binomial(int(row[party]), p)
            points = _make_random_points(points_to_add, row.geometry)

            new_points = gpd.GeoDataFrame(columns=['dem', 'geometry'],
                                          dtype='object',
                                          index=range(points_to_add))

            # Set dem values for points
            if party == dem_vote_count: 
                d_value = 1
            else: 
                d_value = 0
                
            new_points['dem'] = d_value
            
            for i, point in enumerate(points):            
                new_points.iloc[i, 1] = point
                    
            gf = pd.concat([gf, new_points])

    gf['dem'] = gf['dem'].astype('int64')
    
    # Make sure using original CRS
    gf.crs = precincts.crs.to_proj4()
    gf = gf.reset_index(drop=True)

    return gf

def calculate_voter_knn(voter_points, k, target_column='dem'):
    """
        Calculation composition of nearest neigbhors.

        :param voter_points: :class:`geopandas.GeoDataFrame`.
              GeoDataFrame of voter points
        :param k: Num nearest neighbors to consider.
        :param target_column: Feature to average across nearest neighbors.
    """

    voter_points = voter_points.copy()
    voter_points[f'knn_shr_{target_column}'] = np.nan

    tree = cKDTree(list(zip(voter_points['geometry'].x, voter_points['geometry'].y)))

    dd, ii = tree.query(list(zip(voter_points['geometry'].x, voter_points['geometry'].y)), k=k)

    its = 0
    for index, row in voter_points.iterrows():
        voter_points.at[index, f'knn_shr_{target_column}'] = sum(voter_points[target_column]
                                                                 [ii[its]]) / k
        its += 1
    return voter_points

def calculate_dislocation(voter_points, districts, 
                          knn_column='knn_shr_dem', dem_column='dem'):
    """
        Calculation difference between knn dem share
        and dem share of assigned district

        :param voter_points: :class:`geopandas.GeoDataFrame`.
              GeoDataFrame of voter points.
        :param districts: :class:`geopandas.GeoDataFrame`.
              GeoDataFrame of electoral district polygons.
        :param knn_column: (default="knn_shr_dem")
              Column of `voter_points` with kNN scores
        :param dem_column: (default="dem")
                Column with voter attribute to be averaged (usually "dem").
    """

    # Put both geodataframes in common projection
    districts = districts.to_crs(voter_points.crs.to_proj4())

    # Add district ID column
    new_id = 'partisan_dislocation_district_id'
    if new_id in districts.columns:
        raise ValueError(f"District GeoDataFrame may not have column "\
                         f"named {new_id}")
    districts = districts[['geometry']].reset_index(drop=True)
    districts[new_id] = districts.index
    assert districts[new_id].is_unique

    # Calculate district dem share
    dislocation = gpd.sjoin(voter_points, districts, how='inner')

    # Calculate democrat share for each district
    dislocation[f'district_{dem_column}_share'] = dislocation.groupby([new_id])[[dem_column]].transform(np.mean)
        
    # Calculate dislocation score
    dislocation['partisan_dislocation'] = (dislocation[knn_column] - 
                                           dislocation[f'district_{dem_column}_share'])

    # clean
    dislocation = dislocation[[dem_column, knn_column, 
                               f'district_{dem_column}_share', 
                               'partisan_dislocation',
                               'geometry']]

    
    # final dataframe with dislocation score calculated for each voter
    return dislocation
