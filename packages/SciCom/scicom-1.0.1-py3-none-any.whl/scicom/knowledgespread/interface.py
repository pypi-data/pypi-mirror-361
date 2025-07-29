"""The interface to control and run the Knowledgespread ABM."""
from mesa.experimental import JupyterViz

from scicom.knowledgespread.model import (
    KnowledgeSpread,
)
from scicom.knowledgespread.server import (
    agent_draw_altair,
    chart_draw_altair_agents,
    chart_draw_altair_communities,
    epiSpace_draw_altair,
    socialNetwork_draw_altair,
)

model_params = {
    "num_scientists": {
        "type": "SliderInt",
        "value": 50,
        "label": "Initial number of scientists",
        "min": 10,
        "max": 200,
        "step": 10,
    },
    "num_timesteps": {
        "type": "SliderInt",
        "value": 10,
        "label": "How long is the number of agents growing?",
        "min": 5,
        "max": 100,
        "step": 5,
    },
    "epiInit": {
        "type": "Select",
        "value": "complex",
        "label": "Choose initial conditions for epistemic space",
        "values": ["complex", "central", "polarized"],
    },
    "timeInit": {
        "type": "Select",
        "value": "saturate",
        "label": "Choose initial conditions for population growth.",
        "values": ["saturate", "linear", "exponential"],
    },
    "epiRange": {
        "type": "SliderFloat",
        "value": 0.01,
        "label": "Basic range of visibility in epistemic space",
        "min": 0.005,
        "max": 0.3,
        "step": 0.005,
    },
}


page = JupyterViz(
    KnowledgeSpread,
    model_params,
    measures=[socialNetwork_draw_altair, chart_draw_altair_agents, chart_draw_altair_communities],
    name="Knowledge spread",
    agent_portrayal=agent_draw_altair,
    space_drawer=epiSpace_draw_altair,
)
