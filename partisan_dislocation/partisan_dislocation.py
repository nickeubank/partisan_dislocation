# import libraries
import numpy as np
from scipy.spatial import cKDTree
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import random
import os

def get_geodataframe(precinct_file, district_file, data_path="../data"):
    "Read the precinct and district files from the defined data path and return precinct and district geodataframes"
    
    # read the geopandas precinct file
    fpath_precinct = os.path.join(data_path, precinct_file)
    precinct_gdf = gpd.read_file(fpath_precinct)

    # read the geopandas district file
    fpath_district = os.path.join(data_path, district_file)
    district_gdf = gpd.read_file(fpath_district)

    return precinct_gdf, district_gdf

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
    gf = gpd.GeoDataFrame(columns=['Dem','KnnShrDem', 'geometry'])
    election = "P2008_"
    for index, row in precincts.iterrows():
        # Loop over dems and republicans
        for party in [dem_vote_count_column, repub_vote_count_column]:
            points_to_add =  np.random.binomial(int(row[election + party]), p)
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

def calculate_voter_knn(voter_points, k, target_column='Dem'):
    """
        Calculation composition of nearest neigbhors.

        :param voter_points: :class:`geopandas.GeoDataFrame`.
              GeoDataFrame of voter points
        :param k: Num nearest neighbors to consider.
        :param target_column: Feature to average
    """

    tree = cKDTree(list(zip(voter_points.x, voter_points.y)))

    dd, ii = tree.query(list(zip(voter_points.x, voter_points.y)), k=k)

    its = 0
    for index, row in voter_points.iterrows():
        row[f'KnnShr{target_column}'] = sum(voter_points[target_column][ii[its]])/k
        its+=1
        
    voter_points[target_column] = pd.to_numeric(voter_points[target_column])
    voter_points[f"KnnShr{target_column}"] = pd.to_numeric(voter_points[f"KnnShr{target_column}"])

    voter_points['x'] = voter_points['x'].astype(float)
    voter_points['y'] = voter_points['y'].astype(float)
    
    return gpd.GeoDataFrame(voter_points, geometry=gpd.points_from_xy(voter_points.x, voter_points.y))

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
    dist_voter_point= gpd.sjoin(districts, voter_points, how='inner')

    #Calculate democrat share for each district
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

precinct_gdf, district_gdf = get_geodataframe("2008_presidential_precinct_counts.shp","US_cd114th_2014.shp" )
nc = precinct_gdf[precinct_gdf.STATE == "37"]
nc_random_points = random_points_in_polygon(precincts=nc)
nc_voter_knn = calculate_voter_knn(voter_points = nc_random_points, k=10)
nc_voter_knn.crs = nc.crs # Set crs attribute
nc_dislocation = calculate_dislocation(voter_points=nc_voter_knn, district=district_gdf)

# to resolve
# convert polygon to geometry in final dislocation dataframe
# set crs attribute in function itself