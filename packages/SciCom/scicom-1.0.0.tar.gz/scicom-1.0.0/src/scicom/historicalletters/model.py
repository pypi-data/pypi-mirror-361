"""The model class for HistoricalLetters."""
import random
from pathlib import Path

import mesa
import mesa_geo as mg
import networkx as nx
import pandas as pd
from numpy import mean
from shapely import contains
from tqdm import tqdm

from scicom.historicalletters.agents import RegionAgent, SenderAgent
from scicom.historicalletters.space import Nuts2Eu
from scicom.historicalletters.utils import createData
from scicom.utilities.statistics import prune


def getPrunedLedger(model: mesa.Model) -> pd.DataFrame:
    """Model reporter for simulation of archiving.

    Returns statistics of ledger network of model run
    and various iterations of statistics of pruned networks.

    The routine assumes that the network contains fields of sender,
    receiver and step information.
    """
    if model.runPruning is True:
        ledgerColumns = ["sender", "receiver", "sender_location", "receiver_location", "topic", "step"]
        modelparams = {
            "population": model.population,
            "moveRange": model.moveRange,
            "letterRange": model.letterRange,
            "useActivation": model.useActivation,
            "useSocialNetwork": model.useSocialNetwork,
            "similarityThreshold": model.similarityThreshold,
            "longRangeNetworkFactor": model.longRangeNetworkFactor,
            "shortRangeNetworkFactor": model.shortRangeNetworkFactor,
        }
        result = prune(
            modelparameters=modelparams,
            network=model.letterLedger,
            columns=ledgerColumns,
            iterations=3,
            delAmounts=(0.1, 0.25, 0.5, 0.75, 0.9),
            delTypes=("unif", "exp", "beta", "log_normal1", "log_normal2", "log_normal3"),
            delMethod=("agents", "regions", "time"),
            rankedVals=(True, False),
        )
    else:
        result = model.letterLedger
    return result


def getComponents(model: mesa.Model) -> int:
    """Model reporter to get number of components.

    The MultiDiGraph is converted to undirected,
    considering only edges that are reciprocal, ie.
    edges are established if sender and receiver have
    exchanged at least a letter in each direction.
    """
    newg = model.socialNetwork.to_undirected(reciprocal=True)
    return nx.number_connected_components(newg)


def getScaledLetters(model: mesa.Model) -> float:
    """Return relative number of send letters."""
    return len(model.letterLedger)/model.steps if model.steps > 0 else 0


def getScaledMovements(model: mesa.Model) -> float:
    """Return relative number of movements."""
    return model.movements/model.steps if model.steps > 0 else 0


class HistoricalLetters(mesa.Model):
    """A letter sending model with historical informed initital positions.

    Each agent has an initial topic vector, expressed as a RGB value. The
    initial positions of the agents is based on a weighted random draw
    based on data from [1].

    Each step, agents generate two neighbourhoods for sending letters and
    potential targets to move towards. The probability to send letters is
    a self-reinforcing process. During each sending the internal topic of
    the sender is updated as a random rotation towards the receivers topic.

    [1] J. Lobo et al, Population-Area Relationship for Medieval European Cities,
        PLoS ONE 11(10): e0162678.
    """

    def __init__(
        self,
        population: int = 100,
        moveRange: float = 0.05,
        letterRange: float = 0.2,
        similarityThreshold: float = 0.2,
        longRangeNetworkFactor: float = 0.3,
        shortRangeNetworkFactor: float = 0.4,
        regionData: str = Path(Path(__file__).parent.parent.resolve(), "data/NUTS_RG_60M_2021_3857_LEVL_2.geojson"),
        populationDistributionData: str = Path(Path(__file__).parent.parent.resolve(), "data/pone.0162678.s003.csv"),
        *,
        useActivation: bool = False,
        useSocialNetwork: bool = False,
        runPruning: bool = False,
        debug: bool = False,
    ) -> None:
        """Initialize a HistoricalLetters model."""
        super().__init__()

        # Parameters for agents
        self.population = population
        self.moveRange = moveRange
        self.letterRange = letterRange
        # Parameters for model
        self.runPruning = runPruning
        self.useActivation = useActivation
        self.similarityThreshold = similarityThreshold
        self.useSocialNetwork = useSocialNetwork
        self.longRangeNetworkFactor = longRangeNetworkFactor
        self.shortRangeNetworkFactor = shortRangeNetworkFactor
        # Initialize social network
        self.socialNetwork = nx.MultiDiGraph()
        # Output variables
        self.letterLedger = []
        self.movements = 0
        # Internal variables
        self.scaleSendInput = {}
        self.updatedTopicsDict = {}
        self.updatedPositionDict = {}
        self.space = Nuts2Eu()
        self.debug = debug

        #######
        # Initialize region agents
        #######

        # Set up the grid with patches for every NUTS region
        # Create region agents
        ac = mg.AgentCreator(RegionAgent, model=self)
        self.regions = ac.from_file(
            regionData,
        )
        # Add regions to Nuts2Eu geospace
        self.space.add_regions(self.regions)

        #######
        # Initialize sender agents
        #######

        # Draw initial geographic positions of agents
        initSenderGeoDf = createData(
            population,
            populationDistribution=populationDistributionData,
        )

        # Calculate mean of mean distances for each agent.
        # This is used as a measure for the range of exchanges.
        meandistances = []
        for idx in initSenderGeoDf.index.to_numpy():
            geom = initSenderGeoDf.loc[idx, "geometry"]
            otherAgents = initSenderGeoDf.query("index != @idx").copy()
            geometries = otherAgents.geometry.to_numpy()
            distances = [geom.distance(othergeom) for othergeom in geometries]
            meandistances.append(mean(distances))
        self.meandistance = mean(meandistances)

        # Populate factors dictionary
        self.factors = {
            "similarityThreshold": similarityThreshold,
            "moveRange": moveRange,
            "letterRange": letterRange,
        }

        # Set up agent creator for senders
        ac_senders = mg.AgentCreator(
            SenderAgent,
            model=self,
            agent_kwargs=self.factors,
        )

        # Create agents based on random coordinates generated
        # in the createData step above, see util.py file.
        senders = ac_senders.from_GeoDataFrame(
            initSenderGeoDf,
        )

        # Create random set of initial topic vectors.
        topics = [
            tuple(
                [random.random() for x in range(3)],
            ) for x in range(self.population)
        ]

        # Setup senders
        for idx, sender in enumerate(senders):
            # Add to social network
            self.socialNetwork.add_node(
                sender.unique_id,
                numLettersSend=0,
                numLettersReceived=0,
            )
            # Give sender topic
            sender.topicVec = topics[idx]
            # Add current topic to dict
            self.updatedTopicsDict.update(
                {sender.unique_id: topics[idx]},
            )
            # Set random activation weight
            if useActivation is True:
                sender.activationWeight = random.random()
            # Add sender to its region
            regionID = [
                x.unique_id for x in self.regions if contains(x.geometry, sender.geometry)
            ]
            try:
                self.space.add_sender(sender, regionID[0])
            except IndexError as exc:
                text = f"Problem finding region for {sender.geometry}."
                raise IndexError(text) from exc
            # Prepopulate positions dict
            self.updatedPositionDict.update(
                {sender.unique_id: [sender.geometry, regionID[0]]},
            )

        # Create social network
        if useSocialNetwork is True:
            for agent in self.agents_by_type[SenderAgent]:
                self._createSocialEdges(agent, self.socialNetwork)

        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Ledger": getPrunedLedger,
                "Letters": getScaledLetters ,
                "Movements": getScaledMovements,
                "Clusters": getComponents,
            },
        )

    def _createSocialEdges(self, agent: SenderAgent, graph: nx.MultiDiGraph) -> None:
        """Create social edges with the different wiring factors.

        Define a close range by using the moveRange parameter. Among
        these neighbors, create a connection with probability set by
        the shortRangeNetworkFactor.

        For all other agents, that are not in this closeRange group,
        create a connection with the probability set by the longRangeNetworkFactor.
        """
        closerange = [x for x in self.space.get_neighbors_within_distance(
            agent,
            distance=self.moveRange * self.meandistance,
            center=False,
        ) if isinstance(x, SenderAgent)]
        for neighbor in closerange:
            if neighbor.unique_id != agent.unique_id:
                connect = random.choices(
                    population=[True, False],
                    weights=[self.shortRangeNetworkFactor, 1 - self.shortRangeNetworkFactor],
                    k=1,
                )
                if connect[0] is True:
                    graph.add_edge(agent.unique_id, neighbor.unique_id, step=0)
        longrange = [x for x in self.agents_by_type[SenderAgent] if x not in closerange]
        for neighbor in longrange:
            if neighbor.unique_id != agent.unique_id:
                connect = random.choices(
                    population=[True, False],
                    weights=[self.longRangeNetworkFactor, 1 - self.longRangeNetworkFactor],
                    k=1,
                )
                if connect[0] is True:
                    graph.add_edge(agent.unique_id, neighbor.unique_id, step=0)

    def step(self) -> None:
        """One simulation step with data collection."""
        self.step_no_data()
        self.datacollector.collect(self)

    def step_no_data(self) -> None:
        """One simulation step without data collection."""
        self.scaleSendInput.update(
            **{str(x.unique_id): x.numLettersReceived for x in self.agents_by_type[SenderAgent]},
        )
        # Update the currently held topicVec for each agent, based
        # on potential previouse communication events and the position
        # based on a previous movement.
        for agent in self.agents_by_type[SenderAgent]:
            agent.topicVec = self.updatedTopicsDict[agent.unique_id]
            newGeom = self.updatedPositionDict[agent.unique_id]
            if newGeom[0] != agent.geometry:
                self.space.move_sender(agent, newGeom[0], newGeom[1])
        self.agents_by_type[SenderAgent].shuffle_do("step")

    def run(self, n:int) -> None:
        """Run the model for n steps.

        Data collection is only run at the end of n steps.
        This is useful for batch runs accross different
        parameters.
        """
        if self.debug is True:
            for _ in tqdm(range(n)):
                self.step_no_data()
        else:
            for _ in range(n):
                self.step_no_data()
        self.datacollector.collect(self)
