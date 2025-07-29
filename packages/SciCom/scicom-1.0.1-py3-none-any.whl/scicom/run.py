"""Run simulations."""
import argparse

parser = argparse.ArgumentParser(
    prog="Run SciCom Simulations",
    description="This script starts the server interfaces for the different ABM.",
    epilog="During the running of this script, the interfaces should be reachable at http://127.0.0.1:8521",
)

parser.add_argument(
    "simulation",
    choices=[
        "knowledgespread",
    ],
)

args = parser.parse_args()

if args.simulation == "knowledgespread":
    from scicom.knowledgespread.server import server
    server.launch()
