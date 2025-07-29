import networkx as nx
import mesa
from scicom.knowledgespread.agents import ScientistAgent
from scicom.knowledgespread.utils import GenerateInitalPopulation, GenerateSocNet


def getActiveAgents(model):
    """Get all agents active at time t."""
    active = 0
    for x in model.schedule.agents:
        if x.birthtime <= model.schedule.time:
            active += 1
    return active


def getNetworkStructure(model):
    return [len(x) for x in nx.community.louvain_communities(model.socialNetwork)]


class KnowledgeSpread(mesa.Model):
    """A model for knowledge spread. 
    
    Agents have an initial topic vector and are positioned in epistemic space. 
    The number of agents can grow linearly, as a s-curve, or exponentially.
    Agents initial positions on epistemic space can be diverse (checker board-like),
    around a central position or in opossing camps. 

    Agents activation probability is age-dependent. After reaching a personal productivity end,
    agents are removed from the scheduler.

    """

    def __init__(
            self, 
            num_scientists: int = 100,
            num_timesteps: int = 20,
            epiDim:  float = 1.0001,  # This allows the boundary to be equal +/- one, will raise an exception otherwise
            epiRange: float = 0.01,  # Range of visibility in epistemic space.
            oppositionPercent: float = 0.05,  # Weight for random draw of opossing agents 
            loadInitialConditions: bool = False,
            epiInit: str = "complex",
            timeInit: str = "saturate",
            beta: int = 8,
            slope: int = 5,
            base: int = 2,
            ):

        self.numScientists = num_scientists
        self.numTimesteps = num_timesteps
        self.epiRange = epiRange
        self.opposPercent = oppositionPercent
        self.loadInitialConditions = loadInitialConditions
        self.epiInit = epiInit
        self.timeInit = timeInit
        self.beta = beta
        self.slope = slope
        self.base = base

        # Random Schedule
        self.schedule = mesa.time.RandomActivation(self)

        # Epistemic layer space       
        self.space = mesa.space.ContinuousSpace(
            epiDim, epiDim, False, -epiDim, -epiDim
        )
        
        # Create initial setup of agents
        # TODO: The topic vector could be a higher dimensional vector derived from text embeddings.
        self._setupAgents()
        
        # Create agents from initial conditions. 
        agents = []
        for ix, cond in self.initpop.iterrows():
            opose = self.random.choices([False, True], weights=[1 - self.opposPercent, self.opposPercent], k=1)
            # TODO: The distribution of productivity length could be empirically motivated. 
            prodlen = self.random.choices(list(range(15, 55, 1)), k=1) 
            agent = ScientistAgent(
                unique_id=cond["id"],
                model=self,
                pos=(cond["x"], cond["y"]),
                topicledger=[(cond["x"], cond["y"], cond["z"])],
                geopos=(45, 45),
                birthtime=cond["t"],
                opposition=opose[0],
                productivity=(7, 7, prodlen[0])
            )
            agents.append(agent)

        # Setup social layer connections and space
        edges = self._setupSocialSpace()
        self.socialNetwork = nx.from_pandas_edgelist(
            edges,
            source='from_id',
            target='to_id',
            edge_attr=["time", "dist"]
        )
        # TODO: What is the effect of the GRID dimensions on social dynamics?
        self.grid = mesa.space.MultiGrid(1000, 1000, torus=False) 

        # Add agents to epistemic space and schedule.
        for agent in agents:
            self.space.place_agent(
                agent, pos=agent.pos
            )
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(
                agent, (x, y)
            )
            self.schedule.add(agent)

        # Setup data collection
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Active Agents": lambda m: getActiveAgents(m),
                "Graph structure": lambda m: getNetworkStructure(m),
            },
        )

        # Start in running mode
        self.running = True

    def _setupAgents(self):
        """Create initial setup of agents."""
        if self.loadInitialConditions is False:
            epiInit = self.epiInit
            timeInit = self.timeInit
            beta = self.beta
            slope = self.slope
            base = self.base
        else:
            raise NotImplementedError("The reading-in of external initial conditions is not implemented yet. Come back later!") 
        epiOpt = ["complex", "central", "polarized"]
        timeOpt = ["saturate", "linear", "exponential"]
        if epiInit in epiOpt and timeInit in timeOpt:
            generate = GenerateInitalPopulation(self.numScientists, self.numTimesteps)
            initalPop = generate.sample(
                fcE=epiInit,
                fcT=timeInit,
                beta=beta,
                slope=slope,
                base=base
            )
            self.initpop = initalPop
        else:
            raise KeyError(f"Choose epiInit from {epiOpt} and timeInit from {timeOpt}.")

    def _setupSocialSpace(self, nEdges=4, density=0.2, densityGrowth=0):
        """Setup initial social connections."""
        genSoc = GenerateSocNet(self.initpop)
        socNet = genSoc.run(
            nEdges=nEdges,
            density=density,
            densityGrowth=densityGrowth
        )
        return socNet

    def step(self):
        """Run one simulation step."""
        if not len(self.schedule.agents) > 1:
            self.running = False
        else:
            self.schedule.step()
            self.datacollector.collect(self)

    def run(self, n):
        """Run model for n steps."""
        for _ in range(n):
            self.step()