from maup import assign
import geopandas as gpd

df = gpd.read_file("../00_source_data/00_precinct_shapefiles/PA/VTD_FINAL.shp")
gf = gpd.read_file("../00_source_data/00_representative_voter_points/Pennsylvania_USHouse.shp")

gf = gf.to_crs({'init': 'epsg:4269'})
assignment = assign(gf, df)

gf["precinct"] = assignment #maybe should be assignment.map(geoid10)
gf["GEOID10"] = gf["precinct"].map(df["GEOID10"])

gf.to_file("../00_source_data/00_merged_points/Pennsylvania_USHouse_merged_geoid.shp")





