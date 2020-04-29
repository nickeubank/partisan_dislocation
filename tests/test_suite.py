import geopandas as gpd

df = gpd.read_file('/users/nick/dropbox/rodden/US_clustering/'
                   'source_data/precinct_returns/'
                   'precincts_w_countyid.shp')


df = df[df.STATE == "42"]
df = df[['P2008_D', 'P2008_R', 'geometry']]
