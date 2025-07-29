"""Solara interface for all simulations."""
import os

import solara

from scicom.historicalletters.interface import page as historical_letters_page


@solara.component
def Home() -> str:
    return solara.Markdown(r"""
# Historical Letters Simulation

## The model
A letter sending model with historically informed initial positions to reconstruct communication and archiving processes in the Republic of Letters, the 15th to 17th century form of scholarship.

## The audience
The model is aimed at historians, willing to formalize historical assumptions about the letter sending process itself and allows in principle to set heterogeneous social roles, e.g. to evaluate the role of gender or social status in the formation of letter exchange networks. The model furthermore includes a pruning process to simulate the loss of letters to critically asses the role of biases e.g. in relation to gender, geographical regions, or power structures, in the creation of empirical letter archives.

## What are the essentials?
Each agent has an initial random topic vector, expressed as a RGB value. The initial positions of the agents are based on a weighted random draw based on data from [2]. In each step, agents generate two neighbourhoods for sending letters and potential targets to move towards. The probability to send letters is a self-reinforcing process. After each sending the internal topic of the receiver is updated as a movement in abstract space by a random amount towards the letters topic.

## What is the output?
All send letters are tracked in a ledger which is the basis for further research on archival processes by performing random or targeted deletion of records. Changes in network measures are compared to results from empirical letter networks to find likely biases underlying the archive creation. The deletion can be selected as part of the agent-based simulation. In this case a range of network measures is calculated on copies of the ledger where letters have been deleted by different deletion strategies.

## Where can I find more information?

> Malte Vogl, Bernardo Buarque, Jascha Merijn Schmitz, Aleksandra Kaye (2024, May 24).
>“Historical Letters” (Version 1.1.0).
>CoMSES Computational Model Library.
>URL: Retrieved from: https://doi.org/10.25937/x2ve-rc93

""")


@solara.component
def historicalletters():
    return historical_letters_page

@solara.component
def lesson():
     with open(os.path.join(os.path.dirname(__file__), "simulations.md")) as file:
        return solara.Markdown("\n".join(file.readlines()))

routes = [
    solara.Route(path="/", component=Home, label="The model"),
    solara.Route(
        path="historicalletters", component=historicalletters, label="Historical Letters",
    ),
    solara.Route(path="lesson", component=lesson, label="Background"),
]
