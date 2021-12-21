import os
import re
import csv
import argparse
import copy
import time
import json
from typing import Dict, List
from tqdm import tqdm
import networkx as nx

from Compare.Verify.run_test import run as runSingleVerify
from Compare.flip import flip
from src.main import runSingle
from src import util
from src.network.IR import IR

def conv_flip_to_list(flipData):
    res = []
    for s in sorted(flipData._poset.keys()):
        l = []
        for i in flipData._poset[s]:
            l.append(int(re.findall('\<(.*?)\>', i.__str__())[0]))
        res.append(l)

    sort_nested_list(res)
    return res

def conv_string_to_list(stringList):
    if stringList[0] == "[":
        return conv_string_to_list(stringList[1:])
    else:
        acc = ""
        for i in range(len(stringList)):
            if stringList[i] == "]":
                a = []
                for e in acc.split(","):
                    a.append(int(e))
                a.sort()
                if i+3 > len(stringList):
                    return [a]
                return [a] + conv_string_to_list(stringList[len(acc) + 3:])
            acc = acc + stringList[i]

def sort_nested_list(list):
    for l in list:
        l.sort()

def rem_nodes_from_nlist(list, nodes):
    tmp = copy.deepcopy(list)
    for i in range(len(list)):
        for j in range(len(list[i])):
            if list[i][j] in nodes:
                if list[i][j] in tmp[i]:
                    tmp[i].remove(list[i][j])
        if tmp[i] == []:
            tmp.remove(tmp[i])
            return rem_nodes_from_nlist(tmp, nodes)
    return tmp

def printDebug(ir: IR, network: str, batch: List, redBatch: List, vBatch: List, redVBatch: List, fBatch: List, redFBatch: List, oTime: float, vTime: float, fTime: float):
    print("Group to compare:", vBatch)
    print("Flip to compare:", fBatch)
    print("Ours:", batch)

    print()
    print("Group to compare, without chain:", redVBatch)
    print("Flip to compare, without chain:", redFBatch)
    print("Ours, without chain:", redBatch)

    print("Same solution?", redBatch == redVBatch and redBatch == redFBatch)
    if batch != None and vBatch != None:
        l = []
        if len(batch) < len(vBatch):
            maxLen = len(vBatch)
        else:
            maxLen = len(batch)
        for i in range(maxLen):
            if i >= len(redVBatch):
                l.append(False)
            elif i >= len(redBatch):
                l.append(False)
            else:
                l.append(redBatch[i] == redVBatch[i])
        print("Same solution in lists?", l)
    print("Waypoints", ir.wp)
    print(f"Time difference, ours: {oTime}, verify: {vTime}, flip: {fTime}")
    if batch != None and vBatch != None and fBatch != None:
        print(f"Batch size difference, ours: {len(batch)}, verify: {len(vBatch)}, flip: {len(fBatch)}")
    print(f"Num nodes in network {network}, is: {len(ir.nodes)}")

def printCSV(data: Dict):
    with open("Compare/stats.csv", mode="w") as csvFile:
        fieldNames = ['network', 
                'oursTime', 'oursBatchSize', 'oursSolved',
                'verifyTime', 'verifyBatchSize', 'verifySolved',
                'flipTime', 'flipBatchSize', 'flipSolved',
                'numNodes']
        w = csv.DictWriter(csvFile, fieldnames=fieldNames)

        w.writeheader()
        for key in data:
            w.writerow(data[key])

def printCSTime(data: Dict, dir: str):
    with open("Compare/stats_" + dir.split("/")[0] + ".csv", mode="w") as csvFile:
        fieldNames = ['network', 'oursTime', 'flipTime', 'artefactTime', 'numNodes']
        w = csv.DictWriter(csvFile, fieldnames=fieldNames)

        w.writeheader()
        for key in data:
            w.writerow(data[key])

def printCSVBatch(data: Dict, dir: str):
    with open("Compare/stats_batchSize_" + dir.split("/")[0] + ".csv", mode="w") as csvFile:
        fieldNames = ['network', 'ourLen', 'flipLen']
        w = csv.DictWriter(csvFile, fieldnames=fieldNames)

        w.writeheader()
        for key in data:
            w.writerow(data[key])

def add_data_to_dict(data: Dict, ir: IR, network: str, match: bool, blen: List, ot: float, osolv: bool, vblen: List, vt: float, vsolv: bool, fblen: List, ft: float, fsolv: bool):
    if data == {}:
        data = {network : {"network": network, 
            "oursTime" : ot, "oursBatchSize": blen, "oursSolved": osolv,
            "verifyTime": vt, "verifyBatchSize": vblen, "verifySolved": vsolv,
            "flipTime": ft, "flipBatchSize": fblen, "flipSolved": fsolv,
            "numNodes": len(ir.nodes)}}
    else:
        data[network] = {"network": network, 
            "oursTime" : ot, "oursBatchSize": blen, "oursSolved": osolv,
            "verifyTime": vt, "verifyBatchSize": vblen, "verifySolved": vsolv,
            "flipTime": ft, "flipBatchSize": fblen, "flipSolved": fsolv,
            "numNodes": len(ir.nodes)}

    return data

def runOurs(netPath: str):
    ir = util.convert_edge_path_to_IR(netPath)
    batches, rir, t, succ, Ids = runSingle(ir)

    reducedBatches = []
    batchLen = 0
    if succ == True and batches != None:
        sort_nested_list(batches)
        batchLen = len(batches)
        reducedBatches = rem_nodes_from_nlist(batches, Ids)
    else:
        batches = None

    return batches, reducedBatches, batchLen, t, ir, Ids, succ
    
def runVerify(netPath, nodeIds):
    start = time.time()
    batches = runSingleVerify("Compare/Verify/main.jar", "Compare/Verify/verifypn.269", netPath, True)
    end = time.time()

    reducedBatches = []
    batchLen = 0
    if batches != None:
        batches = conv_string_to_list(batches)
        batchLen = len(batches)
        reducedBatches = rem_nodes_from_nlist(batches, nodeIds)

    return batches, reducedBatches, batchLen, end - start

def readFlip(filename: str, dir: str, ir: IR, nodeIds: List):
    filePath = "Compare/flip_res/" + dir + filename
    if os.path.isfile(filePath):
        batches = []
        batch = []
        read = False
        time = None
        with open(filePath) as file:
            lines = file.readlines()
            for l in lines:
                res = re.findall('\*POSTUPDATE', l)
                if res != []:
                    read == False
                    break
                res = re.findall('Finished in (.*?) seconds', l)
                if res != []:
                    time = res[0]
                    continue
                res = re.findall('\*STEP', l)
                if res != []:
                    read = True
                    if batch != []:
                        batches.append(batch)
                    batch = []
                    continue
                if read:
                    res = re.findall('\<(.*?)\>', l)
                    if res != []:
                        batch.append(int(res[0]))
            if batch != []:
                batches.append(batch)
        
        reducedBatches = []
        batchLen = 0
        if batches != None:
            sort_nested_list(batches)
            removeNonUpdNodes(batches, ir)
            batchLen = len(batches)
            reducedBatches = rem_nodes_from_nlist(batches, nodeIds)

        return batches, reducedBatches, batchLen, time
    else:
        return None, None, 0, 0

def readArtefact(filename: str, dir: str) -> float:
    filePath = "Compare/artefact_res/" + dir + filename + ".verifypn.269"
    if os.path.isfile(filePath):
        time = None
        with open(filePath) as file:
            lines = file.readlines()
            for l in lines:
                res = re.findall('Time \(seconds\)', l)
                if res != []:
                    time = re.findall(': (.*?)\n', l)
                    return float(time[0])
        return 0
    else:
        return 0

def runFlip(netPath: str, ir: IR, nodeIds: List):
    init = nx.DiGraph()
    fin = nx.DiGraph()
    with open(netPath) as file:
        data = json.load(file)
        for i in data['Initial_routing']:
            init.add_edge(str(i[0]), str(i[1]))
        for f in data['Final_routing']:
            fin.add_edge(str(f[0]), str(f[1]))

        reach = data['Properties']['Reachability']
        
        flipGraph = flip.Graph(init, fin, dst=str(reach['finalNode']), srcs=[str(reach['startNode'])])
        SubPaths(flipGraph, ir)
        

        start = time.time()
        order = flip.compute_sequence(flipGraph)
        end = time.time()

        batches = conv_flip_to_list(order)
        reducedBatches = []
        batchLen = 0
        if batches != None:
            removeNonUpdNodes(batches, ir)
            batchLen = len(batches)
            reducedBatches = rem_nodes_from_nlist(batches, nodeIds)

        return batches, reducedBatches, batchLen, end - start

def removeNonUpdNodes(batches: List, ir: IR):
    curr = ir.source
    while curr in ir.r:
        if curr in ir.rm and ir.r[curr] == ir.rm[curr]:
            for i in range(len(batches)):
                if curr.id in batches[i]:
                    del batches[i][batches[i].index(curr.id)]
                    if batches[i] == []:
                        del batches[i]
                        break
        curr = ir.r[curr]
    
    for batch in batches:
        if ir.target.id in batch:
            del batch[batch.index(curr.id)]

def SubPaths(flipGraph: flip.Graph, ir: IR):
    curr = ir.source
    subPaths = []
    while curr in ir.r or curr == ir.target:
        if curr.id in ir.wp:
            subPaths.append(str(curr.id))
            flipGraph.subpaths.append(subPaths)
            subPaths = []
        elif curr == ir.target:
            subPaths.append(str(curr.id))
            flipGraph.subpaths.append(subPaths)
        else:
            subPaths.append(str(curr.id))
        if curr != ir.target:
            curr = ir.r[curr]
        else:
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("Path", help="Path to the network file (json file) or to the folder dataset")
    parser.add_argument("--Flip", "-f", default=False)
    args = parser.parse_args()

    datasets = ["zoo_json/", "nested_json/", "synthethic_json/"]

    succ = {}
    fail = {}
    numSucc = 0
    numFail = 0
    maxLen = 0

    if os.path.isfile(args.Path):
        if args.Path.endswith(".json"):
            net = args.Path
            #bO, rBO, tO, bOLen, ir, ids = runOurs(net)
            #bV, rBV, bVLen, tV = runVerify(net, ids)
            #bF, rBF, bFLen, tF = runFlip(net, ir, ids)

            file = args.Path.split("/")
            file = os.path.splitext(file[len(file) - 1])[0]
            #bF, rBF, bFLen, tF = readFlip(file, ir, ids)
            readArtefact(file)

            #printDebug(ir, net, bO, rBO, bV, rBV, bF, rBF, tO, tV, tF)
        else:
            raise Exception("The input either doesn't exist or is not the correct file format (json)")
    else:
        folder = args.Path
        for i in datasets:
            if os.path.isdir(args.Path + i):
                data = {}
                batchS = {}
                fNet = []
                ours = 0
                ours2 = 0
                flip = 0
                flip2 = 0
                petri = 0
                petri2 = 0
                numFiles = len([name for name in os.listdir(folder + i) if os.path.isfile(os.path.join(folder, name))])
                pbar = tqdm(os.listdir(folder + i))
                flipMaxTime = 0
                for f in pbar:
                    pbar.set_postfix({"succ:": f"{numSucc}/{numFiles}", "fail": f"{numFail}/{numFiles}"})
                    filePath = folder + i + f
                    bO, rBO, bOLen, tO, ir, ids, succ = runOurs(filePath)
                    #bV, rBV, bVLen, tV = runVerify(filePath, ids)
                    #bF, rBF, bFLen, tF = runFlip(filePath, ir, ids)
                    file = os.path.splitext(f)[0]
                    bF, rBF, bFLen, tF = readFlip(file, i, ir, ids)
                    tA = readArtefact(file, i)

                    if type(bOLen) == int and bOLen > maxLen:
                        maxLen = bOLen

                    if batchS == {}:
                        if bO == None:
                            batchO = []
                        else:
                            batchO = bO
                        if bF == None:
                            batchF = []
                        else:
                            batchF = bF
                        batchS = {file: {'network': file, 'ourLen': len(batchO), 'flipLen': len(batchF)}}
                    else:
                        if bO == None:
                            batchO = []
                        else:
                            batchO = bO
                        if bF == None:
                            batchF = []
                        else:
                            batchF = bF
                        batchS[file] = {'network': file, 'ourLen': len(batchO), 'flipLen': len(batchF)}

                    if succ:
                        ours = ours + 1
                    else:
                        fNet.append(file)
                        ours2 = ours2 + 1
                    if tF != 0:
                        flip = flip + 1
                    if tF == 0:
                        flip2 = flip2 + 1
                    if tA != 0:
                        petri = petri + 1
                    if tA == 0:
                        petri2 = petri2 + 1

                    if tO == 0 or tF == 0 or tA == 0:
                        continue

                    if data == {}:
                        data = {file: {'network': file, 'oursTime': tO, 'flipTime': tF, 'artefactTime': tA, 'numNodes': len(ir.nodes)}}
                    else:
                        data[file] = {'network': file, 'oursTime': tO, 'flipTime': tF, 'artefactTime': tA, 'numNodes': len(ir.nodes)}

                if fNet != []:
                    print(f"Failed networks are: {fNet}")
                    print(f"Number of networks failed are {len(fNet)}")

                print(i)
                print(maxLen)
                print(f"Ours: {ours}, {ours2}, Flip: {flip}, {flip2}, Petri: {petri}, {petri2}")

                printCSTime(data, i)
                printCSVBatch(batchS, i)
