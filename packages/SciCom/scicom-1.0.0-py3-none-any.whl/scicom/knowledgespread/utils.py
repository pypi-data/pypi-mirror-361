"""Utility functions for initial condition generation."""
from itertools import combinations

import networkx as nx
import numpy as np
import pandas as pd


def epistemicRange(baseRange, age):
    """Return the age dependent search radius for epistemic discovery."""
    if age > 0:
        return baseRange / age  # Refine e.g. in direction of ageFuntion
    else:
        return baseRange


def ageFunction(agent, a, b, c, radius) -> float:
    """Return an age dependent radius.

    Bell-shaped function with center at c, slop and width
    of plateau defined by a, b.

    Can be used to show age-dependent activity of agents. 
    """
    if agent.age == 0:
        return 0.0
    else:
        return radius/(1 + abs((agent.age - c)/(a))**(2*b))


class GenerateInitalPopulation:
    """Generate sets of initial conditions."""

    def __init__(
        self,
        numScientists,
        timesteps,
    ):
        self.N = numScientists
        self.Tstep = timesteps

    def epistemicFunc(self, fc, x, y, beta=8):
        """Epistemic space initial sampling."""
        if fc == "complex":
            return np.sin(beta*x) + np.cos(beta*y)
        elif fc == "central":
            return np.exp(-(x**2 + y**2))
        elif fc == "polarized":
            return x * np.exp(- 3 * (x ** 2 + y ** 2))

    def timeFunc(self, dataframe, step, fcT="saturate", slope=5, base=5):
        """Population growth function."""
        if fcT == "saturate":
            n2step = round(step * (1 - step / self.Tstep))
        elif fcT == "linear":
            n2step = slope
        elif fcT == "exponential":
            n2step = base ** step
        try:
            dft = dataframe.sample(
                n2step,
                weights=abs(dataframe.z),
            )
            return dft
        except ValueError("Your sample size is larger then the data. Adjust exponential time."):
            raise

    def sample(self, fcE="complex", fcT="saturate", beta=8, slope=5, base=5):
        """Generate the sample population and add activation time."""
        dta = self._fullDist(fcE=fcE, beta=beta)
        initial_population = dta.sample(self.N, weights=abs(dta.z))
        initial_population["t"] = 0
        stepDF = []
        for step in range(1, self.Tstep + 1):
            temp = self.timeFunc(dta, step, fcT=fcT, slope=slope, base=base)
            temp["t"] = step
            stepDF.append(temp)
        joined = pd.concat(stepDF)
        initial_population = pd.concat(
            [initial_population, joined],
        )
        initial_population = initial_population.reset_index(drop=True)
        initial_population["id"] = initial_population.index + 1
        return initial_population

    def _fullDist(self, fcE, beta):
        """Full distribution to sample from."""
        x = np.linspace(-1, 1, 10000)
        y = np.linspace(-1, 1, 10000)
        X, Y = np.meshgrid(x, y)
        Z = self.epistemicFunc(fcE, X, Y, beta)
        dta = pd.DataFrame(
            {"x": X.flatten(), "y": Y.flatten(), "z": Z.flatten()},
        )
        return dta


class GenerateSocNet:

    def __init__(
        self,
        dataframe: pd.DataFrame,
        minDist: float = 0.0001,
    ):
        self.population = dataframe
        self.density = ""
        self.allEdges = ""
        self.socialNet = ""
        self.minDist = minDist

    def _getWeighted(self, row, degree):
        try:
            return degree[int(row["from_id"])] * row["dist"]
        except KeyError:
            return None

    def initSocNet(self):
        """Generates initial social network sample from population.

        The dataframe input should contain the colum names: id, x, y, z, t 
        Returns social network sample with from_id, to_id, dist, time
        """
        first_gen = self.population.query("t == 0").id.unique()
        initPopN = len(first_gen)
        coordinateDict = {
            row["id"]: np.array([row["x"], row["y"], row["z"]]) for ix, row in self.population.iterrows()
        }
        idCombinations = [tup for tup in combinations(self.population.id.unique(), 2)]
        edges = []
        for combi in idCombinations:
            dist = np.linalg.norm(
                coordinateDict[combi[0]] - coordinateDict[combi[1]],
            )
            if dist <= 0.0:
                dist = self.minDist
            edges.append(
                (combi[0], combi[1], dist),
            )
        self.allEdges = pd.DataFrame(edges, columns=["from_id", "to_id", "dist"])
        social_net = self.allEdges.query("from_id.isin(@first_gen) and to_id.isin(@first_gen)")
        social_net_sample = social_net.sample(
            round(self.density * (initPopN * (initPopN - 1) / 2)),
            weights=sum(social_net.dist) / social_net.dist,
        )
        social_net_sample.insert(0, "time", 0)
        self.socialNet = social_net_sample
        return social_net_sample

    def growNodes(self, time, nEdges):
        """Add nodes with weighted preferential attachment.
        
        For a time step select all new agents. For each
        agent query all potential edges to previously active
        agents. Weight these edges with the degree of the 
        previous social network and the distances. From this
        select N edges for each new agent.
        Return the concatenated new edges
        """
        addedEdges = []
        oldIDs = self.population.query("t < @time").id.unique()
        for newID in self.population.query("t == @time").id.unique():
            potEdges = self.allEdges.query(
                "from_id == @newID or to_id == @newID",
            ).query(
                "from_id.isin(@oldIDs) or to_id.isin(@oldIDs)",
            )
            socialGraph = nx.from_pandas_edgelist(
                self.socialNet,
                source="from_id",
                target="to_id",
            )

            degree = nx.degree(socialGraph)
            degreeDict = dict(degree)

            weightedDist = potEdges.apply(
                lambda x: self._getWeighted(x, degreeDict), axis=1,
            )
            potEdges.insert(
                0, "weighted", weightedDist,
            )

            potEdges = potEdges.dropna()
            sample = potEdges.sample(
                nEdges,
                weights=sum(potEdges.weighted) / potEdges.weighted,
            )
            sample.insert(0, "time", time)
            addedEdges.append(sample)
        return pd.concat(addedEdges)

    def growEdges(self, time, density, densityGrowth):
        """Add edges with weighted preferential attachement.
        
        For a given time, select the current social network,
        including newly added nodes. Add weights by current 
        degree and distances. 
        Sample a suffiecient number of edges to keep density
        at a given level. 
        """
        curSocEdges = self.socialNet.query("time <= time")
        curSocNet = nx.from_pandas_edgelist(
            curSocEdges, source="from_id", target="to_id",
        )
        edges2add = (
            (
                curSocNet.number_of_nodes() * (curSocNet.number_of_nodes() - 1) / 2
            ) * (density + densityGrowth * time)
        ) - curSocNet.number_of_edges()
        from_degree = pd.DataFrame(
            curSocNet.degree, columns=["from_id", "from_degree"],
        )
        to_degree = pd.DataFrame(
            curSocNet.degree, columns=["to_id", "to_degree"],
        )
        potEdges = self.allEdges.merge(
            from_degree, how="inner",
        ).merge(
            to_degree, how="inner",
        )
        weights = potEdges.from_degree * potEdges.to_degree * potEdges.dist
        potEdges.insert(0, "weighted", weights)
        try:
            sample = potEdges.sample(
                round(edges2add),
                weights=sum(potEdges.weighted) / potEdges.weighted,
            )
            sample = sample[["from_id", "to_id", "dist"]]
            sample.insert(0, "time", time)
            return sample
        except ValueError:
            print("Failed")
            return potEdges

    def run(self, nEdges=4, density=0.2, densityGrowth=0):
        self.density = density
        maxT = self.population.t.max()
        _ = self.initSocNet()
        for time in range(1, maxT + 1, 1):
            newNodeEdges = self.growNodes(time, nEdges)
            self.socialNet = pd.concat([self.socialNet, newNodeEdges])
            newPrefEdges = self.growEdges(time, density, densityGrowth)
            self.socialNet = pd.concat([self.socialNet, newPrefEdges])
        return self.socialNet

