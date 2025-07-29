"""The geographical space for HistoricalLetters."""

import mesa
import mesa_geo as mg

from scicom.historicalletters.agents import RegionAgent, SenderAgent


class Nuts2Eu(mg.GeoSpace):
    """Define regions containing senders of letters.

    The space model is initialized with all EU NUTS2 regions.
    The movement of one agent during the model run consitst of
    the removing the sender from the old region, setting the
    new sender position and then adding the sender to the new
    region.

    This is modified from a mesa-geo example, here
    https://github.com/projectmesa/mesa-examples/blob/main/gis/geo_schelling_points/geo_schelling_points/space.py
    """

    def __init__(self) -> None:
        """Initialize space model."""
        super().__init__(warn_crs_conversion=True)
        self._id_region_map = {}

    def add_regions(self, agents: RegionAgent) -> None:
        """Add regions to space."""
        super().add_agents(agents)
        for agent in agents:
            self._id_region_map[agent.unique_id] = agent

    def add_sender_to_region(self, agent: SenderAgent, region_id: str) -> None:
        """Add sender to region."""
        agent.region_id = region_id
        self._id_region_map[region_id].add_sender(agent)

    def remove_sender_from_region(self, agent: SenderAgent) -> None:
        """Remove sender from region."""
        self._id_region_map[agent.region_id].remove_sender(agent)
        agent.region_id = None

    def add_sender(self, agent: SenderAgent, regionID: str) -> None:
        """Add sender to specific region."""
        super().add_agents([agent])
        self.add_sender_to_region(agent, regionID)

    def move_sender(
        self, agent: SenderAgent, pos: mesa.space.FloatCoordinate, regionID: str,
    ) -> None:
        """Move sender from old to new region."""
        self.__remove_sender(agent)
        agent.geometry = pos
        self.add_sender(agent, regionID)

    def __remove_sender(self, agent: SenderAgent) -> None:
        """Remove sender."""
        super().remove_agent(agent)
        self.remove_sender_from_region(agent)
