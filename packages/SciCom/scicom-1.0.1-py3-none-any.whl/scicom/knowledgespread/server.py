import altair as alt
import mesa
import networkx as nx
import nx_altair as nxa
import pandas as pd
import solara
from matplotlib import colors
from mesa.visualization.modules import ChartVisualization

from scicom.knowledgespread.model import KnowledgeSpread
from scicom.knowledgespread.SimpleContinuousModule import SimpleCanvas
from scicom.knowledgespread.utils import ageFunction

model_params = {
    "num_scientists": mesa.visualization.Slider(
        "Initial number of scientists",
        100, 10, 200, 10,
    ),
    "num_timesteps": mesa.visualization.Slider(
        "How long is the number of agents growing?",
        20, 5, 100, 5,
    ),
    "oppositionPercent": mesa.visualization.Slider(
        "Percentage of opposing agents",
        0.05, 0, 0.5, 0.05,
    ),
    "epiInit": mesa.visualization.Choice(
        "Choose initial conditions for epistemic space",
        value=("complex"),
        choices=["complex", "central", "polarized"],
    ),
    "timeInit": mesa.visualization.Choice(
        "Choose initial conditions for population growth.",
        value=("saturate"),
        choices=["saturate", "linear", "exponential"],
    ),
    "epiRange": mesa.visualization.Slider(
        "Basic range of visibility in epistemic space",
        0.005, 0.001, 0.03, 0.001,
    ),
}


def agent_draw_altair(agent) -> dict:
    """Represent agents."""
    colortuple = set(agent.topicledger[-1])
    color = colors.to_hex(colortuple)
    size = ageFunction(agent, agent.a, agent.b, agent.c, 10) if agent.age > 0 else 0.001
    return {
        "opposition": agent.opposition,
        "size": size,
        "Color": color,
        "color": color,
    }

def chart_draw_altair_agents(model):
    data = model.datacollector.get_model_vars_dataframe().reset_index()
    chart = (
        alt.Chart(data)
        .mark_bar(color="orange")
        .encode(
            x=alt.X("index", title="Step"),
            y=alt.Y(
                "Active Agents",
                title="Active agents",
            ),
        )
    )
    return solara.FigureAltair(chart)


def chart_draw_altair_communities(model):
    data = model.datacollector.get_model_vars_dataframe().reset_index()
    data.insert(0, "compLen", data["Graph structure"].apply(lambda x: len(x)))
    chart = (
        alt.Chart(data)
        .mark_bar(color="orange")
        .encode(
            x=alt.X("index", title="Step"),
            y=alt.Y(
                "compLen",
                title="Communities in social network",
            ),
        )
    )
    return solara.FigureAltair(chart)


def epiSpace_draw_altair(model, agent_portrayal):
    isOpposed = (False, True)
    shape_range = ("circle", "triangle-up")
    all_agent_data = []
    if not model.schedule.agents:
        return solara.Markdown("## Finished run")
    else:
        for agent in model.schedule.agents:
            cur_agent = agent_draw_altair(agent)
            cur_agent["x"] = agent.pos[0]
            cur_agent["y"] = agent.pos[1]
            all_agent_data.append(cur_agent)
        df = pd.DataFrame(all_agent_data)
        colors = list(set(a["color"] for a in all_agent_data))
        chart_color = alt.Color("color").legend(None).scale(domain=colors, range=colors)
        chart = (
            alt.Chart(df)
            .mark_point(filled=True)
            .encode(
                x=alt.X("x", axis=None),  # no x-axis label
                y=alt.Y("y", axis=None),  # no y-axis label
                size=alt.Size("size", title="current activity"),  # relabel size for legend
                color=chart_color,
                shape=alt.Shape(  # use shape to indicate choice
                    "opposition", scale=alt.Scale(domain=isOpposed, range=shape_range),
                ),
            )
            .configure_view(strokeOpacity=0)  # hide grid/chart lines
        )
        return solara.FigureAltair(chart)


def socialNetwork_draw_altair(model):
    currentTime = model.schedule.time
    H = model.socialNetwork
    Graph = nx.Graph(((u, v, e) for u, v, e in H.edges(data=True) if e["time"] <= currentTime))
    pos = nx.kamada_kawai_layout(Graph)
    between = nx.betweenness_centrality(Graph)
    nx.set_node_attributes(Graph, between, "between")
    communities = list(nx.community.label_propagation_communities(Graph))
    for f in Graph.nodes():
        for i, c in enumerate(communities):
            if f in c:
                Graph.nodes()[f].update(
                    {
                        "community": str(i),
                        "name": f,
                    },
                )
    chart = nxa.draw_networkx(
        G=Graph,
        pos=pos,
        node_color="between",
        edge_color="time",
        cmap="viridis",
    )
    chart.configure_view(strokeOpacity=0)  # hide grid/chart lines
    return solara.FigureAltair(chart)


def agent_draw(agent):
    colortuple = set(agent.topicledger[-1])
    color = "#" + "".join(format(int(round(val * 255)), "02x") for val in colortuple)
    probDict = {
        "Shape": "circle",
        "r": ageFunction(agent),
        "Filled": "true",
        "Color": color,
    }
    return probDict


chart = ChartVisualization.ChartModule(
    [
        {"Label": "Active Agents", "Color": "#000000"},
        {"Label": "Graph components", "Color": "black"},
    ],
    data_collector_name="datacollector",
)


epistemic_canvas = SimpleCanvas(agent_draw, 720, 720)


server = mesa.visualization.ModularServer(
    KnowledgeSpread,
    [epistemic_canvas, chart],
    "Knowledge spread",
    model_params,
)
