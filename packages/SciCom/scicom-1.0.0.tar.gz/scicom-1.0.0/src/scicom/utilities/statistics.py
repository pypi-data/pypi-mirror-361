"""Prune a network."""
import igraph as ig
import numpy as np
import pandas as pd


class PruneNetwork:
    """Create statistics for communication networks by deletion.

    For a given dataset with sender and receiver information,
    create a weighted network with igraph. For a given number
    of iterations, deletion amounts, and deletion types, the
    algorithm then generates network statistics for randomly
    sampled subnetworks.
    """

    def __init__(self, dataframe:pd.DataFrame) -> None:
        """Initialize pruning."""
        self.inputDF = dataframe

    def makeNet(self, dataframe:pd.DataFrame) -> ig.Graph:
        """Create network from dataframe.

        Assumes the existence of sender, receiver and step
        column names.
        """
        networkdata = dataframe.groupby(["sender", "receiver"]).agg({"step": lambda x: x.to_list()}).reset_index()
        counts = networkdata.step.apply(lambda x : len(x))
        networkdata.insert(3, "weight", counts)
        graph = ig.Graph.TupleList(
            networkdata.itertuples(index=False), directed=True, edge_attrs=["step", "weight"],
        )
        for node in graph.vs:
            agent = node["name"]
            edgSend = self.inputDF.query("sender == @agent")
            maxSend = edgSend.step.max()
            edgRec = self.inputDF.query("receiver == @agent")
            maxRec = edgRec.step.max()
            if maxSend > maxRec or np.isnan(maxRec):
                lastLoc = edgSend.query("step == @maxSend")["sender_location"].iloc[0]
            elif maxSend < maxRec or maxSend == maxRec or np.isnan(maxSend):
                lastLoc = edgRec.query("step == @maxRec")["receiver_location"].iloc[0]
            else:
                text = f"No location for agent {agent}, got max send {maxSend} and max rec {maxRec}."
                raise ValueError(text)
            node["location"] = lastLoc
        return graph

    def setSurvivalProb(self, graph:ig.Graph, *, method:str = "agents", ranked:bool = True) -> pd.DataFrame:
        """Generate probabilities for different survival modes."""
        if method == "agents":
            tempData = pd.DataFrame(
                {"id": graph.vs["name"], "degree": graph.indegree()},
            )
            tempData = tempData.sort_values("degree", ascending=False) if ranked else tempData.sample(frac=1)
        elif method == "regions":
            tempData = pd.DataFrame(
                pd.concat(
                    [self.inputDF.sender_location, self.inputDF.receiver_location],
                ).unique(), columns = ["location"],
            )
            locations = pd.DataFrame({"id":graph.vs["name"], "location":graph.vs["location"]})
            locations = locations.groupby("location")["id"].nunique().reset_index(name = "count")
            tempData = tempData.merge(locations, how="left").fillna(0)
            tempData = tempData.sort_values("count", ascending = False) if ranked else tempData.sample(frac=1)
        elif method == "time":
            tempData = pd.DataFrame({"step": range(self.inputDF.step.max() + 1)})
            tempData = tempData.sort_values("step", ascending = False) if ranked else tempData.sample(frac=1)
        rng = np.random.default_rng()
        probabilities = pd.DataFrame(
            {
                "unif": -np.sort(-rng.uniform(0, 1, len(tempData))),
                "log_normal1": -np.sort(-rng.lognormal(0, 1/2, len(tempData))),
                "log_normal2": -np.sort(-rng.lognormal(0, 1, len(tempData))),
                "log_normal3": -np.sort(-rng.lognormal(0, 2, len(tempData))),
                "exp": -np.sort(-rng.exponential(10, len(tempData))),
                "beta": -np.sort(-rng.beta(a=4, b=5, size=len(tempData))),
            },
        )
        return pd.concat([tempData, probabilities], axis = 1)

    def scaleSurvivalProb(self, probabilities:pd.DataFrame, *, method:str = "agents") -> pd.DataFrame:
        """Scale survival for methods agents and regions."""
        colsType = ["unif", "beta", "exp", "log_normal1", "log_normal2", "log_normal3"]
        if method == "time":
            return probabilities
        if method == "agents":
            cols = ["sender", "receiver"]
            cols.extend(colsType)
            tempData = self.inputDF[["sender", "receiver"]].drop_duplicates().merge(
                probabilities, left_on="sender", right_on="id",
            )
            tempData = tempData.merge(probabilities, left_on="receiver", right_on="id")
        if method == "regions":
            cols = ["sender_location", "receiver_location"]
            cols.extend(colsType)
            tempData = self.inputDF[["sender_location", "receiver_location"]].drop_duplicates().merge(
                probabilities, left_on="sender_location", right_on="location",
            )
            tempData = tempData.merge(probabilities, left_on="receiver_location", right_on="location")
        for i in colsType:
            tempData[i] = tempData[i + "_x"]  * tempData[i + "_y"] / np.dot(tempData[i + "_x"], tempData[i + "_y"])
        return tempData[cols]

    def basicNetStats(self, graph:ig.Graph) -> pd.DataFrame:
        """Generate base statistics of network."""
        #Find the degree centrality
        tempData = pd.DataFrame({"Degree":graph.degree()})

        #Find the ranking
        tempData["Rank"] = tempData["Degree"].rank(method = "min", ascending = False)

        #Adding other types of centrality
        tempData["Betweenness"] = graph.betweenness()
        tempData["Closeness"] = graph.closeness()
        tempData["Eigenvector"] = graph.eigenvector_centrality()
        tempData["Page_Rank"] = graph.pagerank()

        return tempData

    def netStats(self, G:ig.Graph) -> pd.DataFrame:
        """Generate network statistics."""
        #Number of components:
        no_components = len(G.components())
        #Number of maximal cliques:
        # TODO(Malte): Consider if these are necessary. Performance!
        # no_cliques = len(G.maximal_cliques())
        #Size of the largest clique:
        # size_clique = G.omega()
        #Average path length:
        avg_path = G.average_path_length()
        #Diameter:
        diameter = G.diameter()
        #Modularity:
        modularity = G.modularity(G.components())
        #Transitivity:
        transitivity = G.transitivity_undirected()
        #Cohesion
        cohesion = G.cohesion()
        #Degree assortativity:
        assortativity = G.assortativity_degree()
        #Find the in-degree centrality for each node:
        indegrees = G.indegree()
        #Average relative degree:
        N = len(G.vs)
        avg_rel_degree = np.mean([x/N for x in indegrees])
        #Tail estimator (Hill):
        try:
            hill = ig.statistics.power_law_fit(
                indegrees,
                xmin=1,
                method = "hill",
            ).alpha
        except:
            # TODO: power law estimation fails for small samples
            # This is especially the case in the tests.
            hill = 1
        #Centralization:
        max_indegree = max(indegrees)
        centralization = float(N*max_indegree - sum(indegrees))/(N-1)**2

        return pd.DataFrame([{
            "no_components":no_components,
            # "no_cliques":no_cliques,
            # "size_clique":size_clique,
            "diameter":diameter,
            "avg_path":avg_path,
            "modularity":modularity,
            "transitivity":transitivity,
            "cohesion":cohesion,
            "assortativity":assortativity,
            "avg_degree":avg_rel_degree,
            "centralization":centralization,
            "hill":hill,
        }])

    def deleteFromNetwork(
        self,
        iterations: int = 10,
        delAmounts: tuple = (0.1, 0.25, 0.5, 0.75, 0.9),
        delTypes: tuple = ("unif", "log_normal1", "exp", "beta", "log_normal2", "log_normal3"),
        delMethod: tuple = ("agents", "regions", "time"),
        rankedVals: tuple = (True, False),
    ) -> pd.DataFrame:
        """Run the deletion by sampling."""
        results = []
        fullNet = self.makeNet(
            self.inputDF,
        )
        fullStats = self.netStats(fullNet)
        fullStats = fullStats.assign(
            delVal=0, delType="NA", delIteration=0, delMethod="NA", rankedVal="NA",
        )
        results.append(fullStats)
        for idx in range(1, iterations + 1):
            for method in delMethod:
                for ranked in rankedVals:
                    probVals = self.setSurvivalProb(
                        fullNet, method=method, ranked=ranked,
                    )
                    prunVals = self.scaleSurvivalProb(
                        probVals, method=method,
                    )
                    tempDF = self.inputDF.merge(
                        prunVals,
                    )
                    for val in list(delAmounts):
                        for deltype in list(delTypes):
                            delDF = tempDF.sample(
                                frac = (1 - val),
                                weights=deltype,
                            )
                            delNet = self.makeNet(delDF)
                            delStats = self.netStats(delNet)
                            delStats = delStats.assign(
                                delVal=val, delType=deltype, delIteration=idx, delMethod=method, rankedVal=ranked,
                            )
                            results.append(delStats)
        return pd.concat(results)



def prune(
    modelparameters: dict,
    network: tuple,
    columns: list,
    iterations: int = 10,
    delAmounts: tuple = (0.1, 0.25, 0.5, 0.75, 0.9),
    delTypes: tuple = ("unif", "log_normal1", "exp", "beta", "log_normal2", "log_normal3"),
    delMethod: tuple = ("agents", "regions", "time"),
    rankedVals: tuple = (True, False)) -> pd.DataFrame:
    """Generate pruned networks from input.

    Assumes existence of columns "sender", "receiver",
    "sender_location", "receiver_location" and "step".
    """
    runDf = pd.DataFrame(network, columns = columns)
    pruning = PruneNetwork(runDf)
    result = pruning.deleteFromNetwork(
        iterations=iterations,
        delAmounts=delAmounts,
        delTypes=delTypes,
        delMethod=delMethod,
        rankedVals=rankedVals,
    )
    return result.assign(**modelparameters)
