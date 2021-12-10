import os
from tqdm import tqdm
import csv
import argparse
import copy
import time

from Compare.Verify.run_test import run
from src.main import runSingle
from src import util
from src.IR import IR

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
                tmp[i].remove(list[i][j])
        if tmp[i] == []:
            tmp.remove(tmp[i])
    return tmp

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--Folder", "-f", default="zoo_json/", help="Set to the desired folder to run test on (default is zoo_json)")
    parser.add_argument("--OneFile", "-of", default="", help="Set to true if only run on a single file")
    parser.add_argument("--Flip", default=False)
    args = parser.parse_args()

    succ = {}
    fail = {}
    numSucc = 0
    numFail = 0

    if args.Flip != False:
        net = args.OneFile
        verifyBatches = run("VerifierFromOtherGroup/main.jar", "VerifierFromOtherGroup/verifypn.269", net, False)
        exit()

    if args.OneFile != "":
        net = args.OneFile
        start = time.time()
        verifyBatches = run("VerifierFromOtherGroup/main.jar", "VerifierFromOtherGroup/verifypn.269", net, True)
        end = time.time()
        out = None
        if verifyBatches != None:
            verifyBatches = conv_string_to_list(verifyBatches)

        
        ir = util.convert_edge_path_to_IR(net)
        batches, __, t, success, Ids = runSingle(ir)
        if success == True and batches != None:
            sort_nested_list(batches)
        elif success == False:
            batches = None

        redBatch = rem_nodes_from_nlist(batches, Ids)
        redVerify = rem_nodes_from_nlist(verifyBatches, Ids)

        print("Status from our solution:", succ)

        print("Group to compare:", verifyBatches)
        print("Ours:", batches)
        
        print()
        print("Group to compare, without chain:", redVerify)
        print("Ours, without chain:", redBatch)

        print("Same solution?", redBatch == redVerify)
        if batches != None and verifyBatches != None:
            l = []
            if len(batches) < len(verifyBatches):
                maxLen = len(verifyBatches)
            else:
                maxLen = len(batches)
            for i in range(maxLen):
                if i >= len(redVerify):
                    l.append(False)
                elif i >= len(redBatch):
                    l.append(False)
                else:
                    l.append(redBatch[i] == redVerify[i])
            print("Same solution in lists?", l)
        print("Waypoints", ir.wp)
        print(f"Time difference, ours: {t}, verify: {end - start}")
        if batches != None and verifyBatches != None:
            print(f"Batch size difference, ours: {len(batches)}, verify: {len(verifyBatches)}")
        print(f"Num nodes in network {net}, is: {len(ir.nodes)}")
    else:
        folder = args.Folder
        numFiles = len([name for name in os.listdir(folder) if os.path.isfile(os.path.join(folder, name))])
        print("len", numFiles)
        pbar = tqdm(os.listdir(folder))
        for f in pbar:
            pbar.set_postfix({"succ:": f"{numSucc}/{numFiles}", "fail": f"{numFail}/{numFiles}"})
            filePath = folder + f
            batches, __, ir, __, t, success, Ids = runSingle(filePath)
            if success == True and batches != None:
                sort_nested_list(batches)
            elif success == False:
                batches = None

            start = time.time()
            verifyBatches = run("VerifierFromOtherGroup/main.jar", "VerifierFromOtherGroup/verifypn.269", filePath, True)
            end = time.time()
            if verifyBatches != None:
                verifyBatches = conv_string_to_list(verifyBatches)

            if batches != None:
                redBatch = rem_nodes_from_nlist(batches, Ids)
                batlen = len(batches)
            else:
                redBatch = None
                batlen = 0

            if verifyBatches != None:
                redVerify = rem_nodes_from_nlist(verifyBatches, Ids)
                verlen = len(verifyBatches)
            else:
                redVerify = None
                verlen = 0


        
            if redBatch == redVerify:
                numSucc = numSucc + 1
                if succ == {}:
                    succ = {f : {"network": f, "ours": batches, "oursTime" : t, "oursBatchSize": batlen, "verify": verifyBatches, "verifyTime": end - start, "verifyBatchSize": verlen, "numNodes": len(ir.nodes), "succ": True}}
                else:
                    succ[f] = {"network": f, "ours": batches, "oursTime" : t, "oursBatchSize": batlen, "verify": verifyBatches, "verifyTime": end - start, "verifyBatchSize": verlen, "numNodes": len(ir.nodes), "succ": True}
            else:
                numFail = numFail + 1
                if succ == {}:
                    succ  = {f : {"network": f, "ours": batches, "oursTime" : t, "oursBatchSize": batlen, "verify": verifyBatches, "verifyTime": end - start, "verifyBatchSize": verlen, "numNodes": len(ir.nodes), "succ": True}}
                else:
                    succ[f] = {"network": f, "ours": batches, "oursTime" : t, "oursBatchSize": batlen, "verify": verifyBatches, "verifyTime": end - start, "verifyBatchSize": verlen, "numNodes": len(ir.nodes), "succ": True}

    
        print(numSucc, numFail)
    
        with open("Compare/stats.csv", mode="w") as csvFile:
            fieldNames = ['network', 'ours', 'oursTime', 'oursBatchSize', 'verify', 'verifyTime', 'verifyBatchSize', 'numNodes', 'succ']
            w = csv.DictWriter(csvFile, fieldnames=fieldNames)

            w.writeheader()
            for key in succ:
                w.writerow(succ[key])
    
