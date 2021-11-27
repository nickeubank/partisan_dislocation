# import libraries
import numpy as np
from scipy.spatial import cKDTree
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point


def _make_random_points(number, polygon):
    "Generates number of uniformly distributed points in polygon"
    points = []
    min_x, min_y, max_x, max_y = polygon.bounds

    i = 0
    attempt = 0

    while i < number:
        point = Point(np.random.uniform(min_x, max_x), np.random.uniform(min_y, max_y))

        # If its in polygon, keep. Otherwise we keep going.
        if polygon.contains(point):
            points.append(point)
            i += 1
            attempt = 0

        # Count how many times we've tried for this point
        attempt += 1
        if attempt > 10000:
            raise ValueError(
                "Could not generate a random point in one of your precincts."
                " Check for zero-area precincts or invalid geometries."
            )
    return points


def random_points_in_polygon(
    precincts,
    p=0.01,
    dem_vote_count="dem",
    repub_vote_count="rep",
    uniform_swing_to_dems=0,
    random_seed=None,
):
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
    :param uniform_swing_to_dems: (default=0)
              Swing in expected vote share for dems.
              A value of 0.05 would move a 45% dem 55%
              repub vote share to 50% / 50%.
    :param random_seed: (default=None)
              Random state or seed passed to numpy.

    """

    # Make sure projected!
    if precincts.crs is None:
        raise ValueError("Precincts must have a defined CRS")

    # Set seed if passed.
    if random_seed is not None:
        np.random.seed(random_seed)

    # Check people don't get confused by uniform swing.
    if uniform_swing_to_dems < -1 or uniform_swing_to_dems > 1:
        raise ValueError("Uniform swing should be in SHARES and lie between -1 and 1.")

    # Make master dataframe
    gf = gpd.GeoDataFrame(columns=["dem", "geometry"])

    for index, row in precincts.iterrows():
        # Get num seats for each
        voters = int(row[dem_vote_count]) + int(row[repub_vote_count])
        if voters != 0:
            dem_share = int(row[dem_vote_count]) / voters
            swung_dem_share = dem_share + uniform_swing_to_dems
        if voters == 0:
            swung_dem_share = 0.5

        # Num votes from which to draw after swing
        votes = {
            dem_vote_count: int(swung_dem_share * voters),
            repub_vote_count: int((1 - swung_dem_share) * voters),
        }

        # Split integer residual probabilistically:
        residual_dem = (votes[dem_vote_count] + votes[repub_vote_count]) - voters
        if residual_dem != 0:
            dem_prob = votes[dem_vote_count] - int(votes[dem_vote_count])
            extra_dem = np.random.binomial(1, dem_prob)
            if extra_dem == 1:
                votes[dem_vote_count] = votes[dem_vote_count] + 1
            if extra_dem == 0:
                votes[repub_vote_count] = votes[repub_vote_count] + 1
        assert voters == votes[repub_vote_count] + votes[dem_vote_count]

        # Start adding seats
        for party in [dem_vote_count, repub_vote_count]:
            points_to_add = np.random.binomial(votes[party], p)
            points = _make_random_points(points_to_add, row.geometry)

            new_points = gpd.GeoDataFrame(
                columns=["dem", "geometry"], dtype="object", index=range(points_to_add)
            )

            # Set dem values for points
            if party == dem_vote_count:
                d_value = 1
            else:
                d_value = 0

            new_points["dem"] = d_value

            for i, point in enumerate(points):
                new_points.iloc[i, 1] = point

            gf = pd.concat([gf, new_points])

    gf["dem"] = gf["dem"].astype("int64")

    # Make sure using original CRS
    gf = gf.set_crs(precincts.crs)
    gf = gf.reset_index(drop=True)

    return gf


def calculate_voter_knn(voter_points, k, target_column="dem"):
    """
    Calculation composition of nearest neigbhors.

    :param voter_points: :class:`geopandas.GeoDataFrame`.
          GeoDataFrame of voter points
    :param k: Num nearest neighbors to consider.
    :param target_column: Feature to average across nearest neighbors.
    """

    voter_points = voter_points.copy()
    voter_points = voter_points.reset_index(drop=True)
    voter_points[f"knn_shr_{target_column}"] = np.nan

    tree = cKDTree(list(zip(voter_points["geometry"].x, voter_points["geometry"].y)))

    # Note this will pull the point itself, which we don't want.
    # So do k+1, then remove "self" later.
    dd, ii = tree.query(
        list(zip(voter_points["geometry"].x, voter_points["geometry"].y)), k=k + 1
    )

    for index, row in voter_points.iterrows():

        # Extract self.
        neighbors = [i for i in ii[index] if i != index]
        if not len(neighbors) < len(ii[index]):
            raise ValueError(
                "You should never get this error. If you do, please post an issue on the github"
                " repository for this package at www.github.com/nickeubank/partisan_dislocation"
            )

        voter_points.at[index, f"knn_shr_{target_column}"] = (
            voter_points[target_column].iloc[neighbors].sum() / k
        )

    return voter_points


def calculate_dislocation(
    voter_points,
    districts,
    knn_column="knn_shr_dem",
    dem_column="dem",
    district_id_col=None,
):
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
    :param district_id_col: (default=None)
          Column with district identifier to include in voter data.
          Optional.
    """

    # Put both geodataframes in common projection
    districts = districts.to_crs(voter_points.crs)

    # Add new district index column
    new_id = "partisan_dislocation_district_id"
    if new_id in districts.columns:
        raise ValueError(
            f"District GeoDataFrame may not have column " f"named {new_id}"
        )

    to_keep = ["geometry"]

    # Add in district name if wanted
    if district_id_col is not None:
        to_keep.append(district_id_col)

    districts = districts[to_keep].reset_index(drop=True)

    districts[new_id] = districts.index
    assert districts[new_id].is_unique

    # Calculate district dem share
    dislocation = gpd.sjoin(voter_points, districts, how="inner")

    # Calculate democrat share for each district
    dislocation[f"district_{dem_column}_share"] = dislocation.groupby([new_id])[
        [dem_column]
    ].transform(np.mean)

    # Calculate dislocation score
    dislocation["partisan_dislocation"] = (
        dislocation[f"district_{dem_column}_share"] - dislocation[knn_column]
    )

    # clean
    clean_cols = [
        dem_column,
        knn_column,
        f"district_{dem_column}_share",
        "partisan_dislocation",
        "geometry",
    ]

    # Add in district name if wanted
    if district_id_col is not None:
        clean_cols.append(district_id_col)

    dislocation = dislocation[clean_cols]

    # final dataframe with dislocation score calculated for each voter
    return dislocation
