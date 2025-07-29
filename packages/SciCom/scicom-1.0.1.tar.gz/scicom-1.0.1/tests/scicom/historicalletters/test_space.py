"""Test space initialization."""
from pathlib import Path

import mesa_geo as mg
from scicom.historicalletters.agents import (
    RegionAgent,
)
from scicom.historicalletters.model import (
    HistoricalLetters,
)
from scicom.historicalletters.space import (
    Nuts2Eu,
)

#####
# Test space setup
#####

def test_space() -> None:
    """Test space init."""
    scicomPath = Path(__file__).parent.parent.parent.parent.resolve()
    regionData = Path(scicomPath, "src/scicom/data/NUTS_RG_60M_2021_3857_LEVL_2.geojson")
    space = Nuts2Eu()
    ac = mg.AgentCreator(RegionAgent, model=HistoricalLetters())
    regions = ac.from_file(
            regionData,
    )
    space.add_regions(regions)
