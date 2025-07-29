"""Test utility functions."""
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pytest
import shapely
from scicom.historicalletters.agents import SenderAgent
from scicom.historicalletters.model import HistoricalLetters
from scicom.historicalletters.utils import createData, getNewTopic, getPositionOnLine, getRegion
from shapely import LineString, Point, contains

######
# Utility function testing
######


def test_initial_population_creation() -> None:
    """Test initial population.

    Initial population should contain
    lat/long and geometry information.
    The chosen CRS is essential since overlap
    calculation depends on the regions CRS.
    """
    scicomPath = Path(__file__).parent.parent.parent.parent.resolve()
    file = createData(
        population=30,
        populationDistribution=Path(scicomPath, "src/scicom/data/pone.0162678.s003.csv"),
    )
    c1 = 30
    assert isinstance(file, gpd.GeoDataFrame)
    assert file.shape[0] == c1
    for col in  ["longitude", "latitude", "geometry"]:
        assert col in list(file.columns)
    assert file.crs == "EPSG:3857"


def test_getPositionOnLine() -> None:
    """Test returning postion on line.

    Get random point on line between two points.
    Return type is a shaple geometry Point.
    """
    p1 = Point(0.3,0.2,0.3)
    p2 = Point(0.5, 0.4,0.9)
    p3 = getPositionOnLine(p1,p2)
    assert isinstance(p3, Point)
    line = LineString([p1,p2])
    assert contains(line, p3)
    p4 = getPositionOnLine(p1,p2)
    assert isinstance(p4, shapely.Point)

def test_getNewTopic() -> None:
    """Test new topic generation."""
    p1 = (0.3,0.5,0.7)
    p2 = (0.2,0.4,0.56)
    p3 = getNewTopic(p1,p2)
    assert isinstance(p3, tuple)


def test_getRegion() -> None:
    """Test getting the region id.

    Returns the id of the overlaping region
    for a given agent.
    """
    model = HistoricalLetters(10)
    a1 = model.agents_by_type[SenderAgent][0]
    ## New York coord
    coord = (40.712728, -74.006015)
    d1 = pd.DataFrame([coord], columns=["lat", "long"])
    geodf = gpd.GeoDataFrame(
            d1,
            geometry=gpd.points_from_xy(d1.long, d1.lat),
            crs="EPSG:4326",
        )
    geodf.to_crs("EPSG:3857")
    a2fail = geodf.geometry.iloc[0]
    reg = getRegion(a1.geometry, model)
    assert isinstance(reg, int)
    with pytest.raises(IndexError):
        getRegion(a2fail, model)
