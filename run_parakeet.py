#This file will run the appropriate functions to run parakeet
import argparse

from src import main

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(title="Method", dest="method", help="Choose network format, as node route or edge route (Required)")
    node_route = subparser.add_parser("node", help="Run parakeet, where network route is defined as a list of nodes (only 1 route in R and R')")
    edge_route = subparser.add_parser("edge", help="Run parakeet, where network route is defined as a list of edges")

    parser.add_argument("Path", help="Path to the network file (json file) or folder containing the dataset")
    parser.add_argument("--OutDir", "-o", default="results", help="Output directory to write stats to")
    parser.add_argument("--StatsName", "-s", default="output.csv", help="filename of stats file (remember to include file extension) [default=output.csv]")

    subparser.required = True
    args = parser.parse_args()

    if args.method == "node":
        print("Choose node parser")
        main.run_parakeet_on_node_route(args.Path)
    else:
        print("Choose edge parser")
        main.run_parakeet_on_edge_route(args.Path, args.OutDir, args.StatsName)
