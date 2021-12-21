#This file contains utility functions, primarely to convert input file to IR
import os
import json
import csv
from src.network.IR import IR
from typing import Dict, List

def convert_node_path_to_IR(filePath: str) -> IR:
    file = open(filePath, "r")
    data = json.load(file)
    file.close()

    return IR.from_string_routes(data.get("r"), data.get("rm"), data.get("waypoints"))

def convert_edge_path_to_IR(filePath: str) -> IR:
    file = open(filePath, "r")
    data = json.load(file)
    file.close()

    return IR.from_dict_routes(data.get("Initial_routing"), data.get("Final_routing"), data.get("Properties"))

def write_stats_to_csv(outDir: str, statsName: str, data: List, csvFormat: List = ['network', 'elapsedTime', 'batches', 'numberOfBatch', 'networkSize']):
    if not os.path.isdir(outDir):
        os.makedirs(outDir)

    if outDir.endswith("/"):
        f = outDir + statsName
    else:
        f = outDir + "/" + statsName
    
    with open(f, mode="w") as csvFile:
        fieldNames = ['network', 'elapsedTime', 'batches', 'numberOfBatch', 'networkSize']
        w = csv.DictWriter(csvFile, fieldnames=fieldNames)

        w.writeheader()
        for i in data:
            w.writerow(i)
