"""Utility functions for HistoricalLetters."""
import random

import geopandas as gpd
import mesa
import numpy as np
import pandas as pd
import shapely
from shapely import LineString, contains


def createData(population: int, populationDistribution: str) -> gpd.GeoDataFrame:
    """Create random coordinates of historically motivated choices.

    The routine samples a population sample based on estimated
    population density of that coordinate.

    The original CSV dataset is retrieved from
    https://doi.org/10.1371/journal.pone.0162678.s003
    """
    initial_population_choices = pd.read_csv(
        populationDistribution,
        encoding="latin1", index_col=0,
    )

    # Calculate relative population ratio to estimated settlement area.
    # This will correspont to the probabilities to draw an agent from
    # these coordinates.
    relPop = []

    for _, row in initial_population_choices.iterrows():
        relPop.append(
            row["Area"] / row["Pop"],
        )

    initial_population_choices.insert(0, "relPop", relPop)

    # Four costal cities can not be considered, since the modern NUTS regions
    # give zero overlap to their coordinates, leading to potential errors when
    # agents move.
    excludeCoastal = ["Great Yarmouth", "Kingston-upon-Hull", "Calais", "Toulon"]
    initial_population_choices = initial_population_choices.query("~Settlement.isin(@excludeCoastal)")

    loc_probabilities = []
    loc_values = []
    for _, row in initial_population_choices.iterrows():
        loc_probabilities.append(row["relPop"])
        loc_values.append(
            (row["longitude"], row["latitude"]),
        )

    coordinates = random.choices(
        loc_values,
        loc_probabilities,
        k=population,
    )

    data = pd.DataFrame(
        coordinates,
        columns=["longitude", "latitude"],
    )

    #data.insert(
    #    0,
    #    "unique_id",
    #    [
    #        "P" + str(x) for x in list(range(population))
    #    ],
    #)

    # Read the Geodataframe with EPSG:4326 projection.
    geodf = gpd.GeoDataFrame(
        data,
        geometry=gpd.points_from_xy(data.longitude, data.latitude),
        crs="EPSG:4326",
    )

    # Transform to EPSG:3857, since the NUTS shape files are in
    # that projection.
    return geodf.to_crs("EPSG:3857")


def getRegion(geometry: shapely.geometry.point.Point, model:mesa.Model) -> str:
    """Get region ID overlaping with input geometry.

    Might e.g. fail if line of connection crosses international
    waters, since there is no NUTS region assigned then.
    """
    regionID = [
        x.unique_id for x in model.regions if contains(x.geometry, geometry)
    ]
    if regionID:
        return regionID[0]
    text = f"Can not find overlaping region to geometry {geometry}"
    raise IndexError(text)


def getPositionOnLine(start:shapely.Point, target:shapely.Point) -> shapely.Point:
    """Interpolate movement along line between two given points.

    The amount of moving from start to target is random.
    """
    segment = LineString([start, target])
    return segment.interpolate(random.uniform(0.0, 1.0), normalized=True)

def getNewTopic(start: tuple, target:tuple) -> tuple:
    """Interpolate new topic between two topics.

    The amount of moving from start to target is random.
    """
    p1 = np.array(start)
    p2 = np.array(target)
    p3 = p1 + random.uniform(0, 1) * (p2 -p1)
    return tuple(p3)
