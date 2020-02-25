import numpy as np
from scipy.spatial import cKDTree
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import random
import time

start_time = time.time()

df = gpd.read_file("../00_source_data/00_precinct_shapefiles/PA/VTD_FINAL.shp")

num_districts = 203
election="T16PRES"
num_voters = df[election+"D"].sum() + df[election+"R"].sum()


prob = 1000*num_districts/num_voters


#####Step 0 Helper functions

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

#####Step 1 generate points uniformly in each precinct


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

gdf = gpd.GeoDataFrame(gf, crs={'init': 'epsg:4326'}, geometry=gf["geometry"] )


print("finished building")

#####Steps 2 Compute nearest neighbors with cKDTree

tree = cKDTree(list(zip(gdf["geometry"].x, gdf["geometry"].y)))

dd, ii = tree.query(list(zip(gdf["geometry"].x, gdf["geometry"].y)), k=1000)

dd = None


its = 0 
for index, row in gdf.iterrows():
    row['KnnShrDem'] = sum(gdf["dem"][ii[its]])/1000
    its+=1
    
    
gdf["dem"] = pd.to_numeric(gdf["dem"])
gdf["KnnShrDem"] = pd.to_numeric(gdf["KnnShrDem"])

    
gdf.to_file("../20_intermediate_files/PA_test_HOU_shr.shp")

print("saved shapefile")

print(time.time() - start_time, "Seconds!")

