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
        if polygon.contains(point):
            points.append(point)
            i += 1
    return points

def random_points_in_polygon(precincts, p=0.01,
                             dem_vote_count="D",
                             repub_vote_count="R",
                             dem_uniform_swing=0,
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
    # Make master dataframe
    gf = gpd.GeoDataFrame(columns=['Dem', 'geometry'])

    for index, row in precincts.iterrows():
        # Loop over dems and republicans
        for party in [dem_vote_count, repub_vote_count]:
            points_to_add = np.random.binomial(int(row[party]), p)
            points = _make_random_points(points_to_add, row.geometry)
            for point in points:
                if party == dem_vote_count:
                    dem_value = 1
                else:
                    dem_value = 0

                gf = gf.append({'Dem': dem_value, 'geometry': point}, ignore_index=True)

    gf['Dem'] = gf['Dem'].astype('int64')

    return gf

def calculate_voter_knn(voter_points, k, target_column='Dem'):
    """
        Calculation composition of nearest neigbhors.

        :param voter_points: :class:`geopandas.GeoDataFrame`.
              GeoDataFrame of voter points
        :param k: Num nearest neighbors to consider.
        :param target_column: Feature to average
    """

    voter_points[f'KnnShr{target_column}'] = np.nan

    tree = cKDTree(list(zip(voter_points['geometry'].x, voter_points['geometry'].y)))

    dd, ii = tree.query(list(zip(voter_points['geometry'].x, voter_points['geometry'].y)), k=k)

    its = 0
    for index, row in voter_points.iterrows():
        voter_points.at[index, f'KnnShr{target_column}'] = sum(voter_points[target_column][ii[its]]) / k
        its += 1

    return voter_points

def calculate_dislocation(voter_points, district, knn_column='KnnShrDem', dem_column='dem'):
    """
        Calculation difference between knn dem share
        and dem share of assigned district

        :param voter_points: :class:`geopandas.GeoDataFrame`.
              GeoDataFrame of voter points.
        :param voter_points: :class:`geopandas.GeoDataFrame`.
              GeoDataFrame of district polygons.
        :param knn_column: Column of `voter_points` with kNN scores
    """

    # Put both geodataframes in common projection
    districts = district.to_crs(voter_points.crs)

    # Calculate district dem share
    dist_voter_point = gpd.sjoin(districts, voter_points, how='inner')

    # Calculate democrat share for each district
    dist1 = dist_voter_point.groupby(['NAMELSAD']).agg(district_demshare=pd.NamedAgg(column='Dem', aggfunc=np.mean))
    dist1 = dist1.reset_index()

    # merge the dataframe with democrat share in each district to obtain district democrat share for each voter
    final_df = dist_voter_point.merge(dist1, how='left')

    # Calculate dislocation score
    final_df['dislocation'] = final_df['KnnShrDem'] - final_df['district_demshare']

    # Select relevant columns
    dislocation_score_df = final_df[['NAMELSAD', 'Dem', 'KnnShrDem', 'district_demshare', 'dislocation', 'geometry']]

    # final dataframe with dislocation score calculated for each voter
    return dislocation_score_df

# Uncomment following code to test all functions with NC state

#precinct_gdf, district_gdf = get_geodataframe("2008_presidential_precinct_counts.shp","US_cd114th_2014.shp" )
# nc = precinct_gdf[precinct_gdf.STATE == "37"]
# nc_random_points = random_points_in_polygon(precincts=nc)
# nc_voter_knn = calculate_voter_knn(voter_points = nc_random_points, k=10)
#nc_voter_knn.crs = nc.crs # Set crs attribute
# nc_dislocation = calculate_dislocation(voter_points=nc_voter_knn, district=district_gdf)

# to resolve
# convert polygon to geometry in final dislocation dataframe
# set crs attribute in function itself
