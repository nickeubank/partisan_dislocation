# Partisan Dislocation

This package implements the partisan dislocation measure from [Deford, Eubank, Rodden](http://www.nickeubank.com/defordeubankrodden_dislocation/).

It takes as input a GeoDataframe of polygons with columns containing vote counts for both political parties for each polygon. it includes three functions which, when used sequentially, will return a GeoDataframe of representative voter point along with associated dislocation scores for each point.

In addition, the [repository for this package](http://www.github.com/nickeubank/partisan_dislocation) also include the shapefiles of US precincts and their vote totals from the 2008 presidential election used in Deford, Eubank, Rodden. these can be found in the folder "2008_presidential_precinct_data." Note that to download this data, you will have to first install [git-lfs](https://www.git-lfs.github.org) before cloning the repository.

The three functions provided by the package are:

- `random_points_in_polygon`: takes a polygon GeoDataframe with the number of votes cast democrats and republicans in each polygon and returns a GeoDataframe off of representative voter points.
- `calculate_voter_knn`: takes a voter point GeoDataframe and returns a voter point GeoDataframe with voter knn scores.
- `calculate_dislocation`: takes a voter point GeoDataframe with knn scores and a GeoDataframe with electoral district polygons and returns voter dislocation scores.

## Tutorial

Demonstration of how the package can be used can be found in [dislocation_tutorial.ipynb](https://github.com/nickeubank/partisan_dislocation/blob/master/dislocation_tutorial.ipynb).

## Installation

This package can be easily installed using `pip`:

```
pip install partisan_dislocation
```
