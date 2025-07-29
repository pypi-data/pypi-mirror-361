"""Test pruning parts."""
import igraph as ig
import pandas as pd
from scicom.historicalletters.agents import SenderAgent
from scicom.historicalletters.model import (
    HistoricalLetters,
)
from scicom.utilities.statistics import (
    PruneNetwork,
)

#####
# Test pruning setup
#####


def test_pruning() -> None:
    """Model initialization puts agents on sheduler."""
    model = HistoricalLetters(
        population=10,
    )
    model.run(10)
    columns = ["sender", "receiver", "sender_location", "receiver_location", "topic", "step"]
    network = pd.DataFrame(model.letterLedger, columns = columns)
    pruning = PruneNetwork(dataframe=network)

    graph = pruning.makeNet(dataframe=network)

    assert isinstance(graph, ig.Graph)

    dataagents = pruning.setSurvivalProb(
        graph=graph, method="agents",
    )

    assert isinstance(dataagents, pd.DataFrame)

    dataregions = pruning.setSurvivalProb(
        graph=graph, method="regions",
    )
    assert isinstance(dataregions, pd.DataFrame)

    datatimesteps = pruning.setSurvivalProb(
        graph=graph, method="time",
    )
    assert isinstance(datatimesteps, pd.DataFrame)


def test_model_initialization_with_pruning() -> None:
    """Model initialization puts agents on sheduler."""
    model = HistoricalLetters(
        population=10,
        runPruning=True,
        debug=True,
    )
    c1 = 10 # Number of agents in model
    c2 = 23 # Number of columns of pruned results
    assert len(model.agents_by_type[SenderAgent]) == c1
    model.run(10)
    data = pd.DataFrame(model.datacollector.get_model_vars_dataframe()['Ledger'][0])
    assert data.shape[1] == c2
