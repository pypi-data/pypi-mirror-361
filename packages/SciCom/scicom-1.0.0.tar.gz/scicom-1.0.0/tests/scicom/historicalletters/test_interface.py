"""Test server initialization."""

from scicom.historicalletters.agents import SenderAgent
from scicom.historicalletters.model import (
    HistoricalLetters,
)
from scicom.historicalletters.interface import (
    page,
    agent_draw,
)

#####
# Test server setup
#####

def test_server() -> None:
    """Test server launch."""
    assert page
    #assert isinstance(server.description, str)

def test_region_draw() -> None:
    """Test drawing a region."""
    model = HistoricalLetters(15)
    region = model.regions[10]
    pot = agent_draw(region)
    color = pot.get("color")
    assert isinstance(color, str)
    assert color.startswith("#")

def test_agent_draw() -> None:
    """Test drawing a region."""
    model = HistoricalLetters(15)
    agent = model.agents_by_type[SenderAgent]
    pot2 = agent_draw(agent[0])
    for val in ["name", "marker_type", "icon_properties", "description"]:
        assert val in pot2
