import os
import time
from typing import List, Tuple, Union
from tqdm import tqdm

from .network.IR import IR
from . import util
from .batch_handler import find_batches as batchCalc

###############################################################
#################### Parakeet node routing ####################
###############################################################
def run_parakeet_on_node_route(path: str, debug: bool = False):
    if os.path.isfile(path):
        if path.endswith(".json"):
            ir = util.convert_node_path_to_IR(path)
            rir, batches, succ, __ = batchCalc(ir, debug, {})
            print(batches)

    elif os.path.isdir(path):
        if not path.endswith("/"):
            path = path + "/"

        pbar = tqdm(os.listdir(path))
        for f in pbar:
            file = path + f
            if file.endswith(".json"):
                ir = util.convert_node_path_to_IR(file)
                rir, batches, succ, __ = batchCalc(ir, debug, {})

    return True

###############################################################
#################### Parakeet edge routing ####################
###############################################################
def run_parakeet_on_edge_route(path: str, outDir: str, statName: str, debug: bool = False):
    if os.path.isfile(path):
        if path.endswith(".json"):
            ir = util.convert_edge_path_to_IR(path)
            batches, rir, t, succ, __ = runSingle(ir, debug)
            print(f"Is network solvable? {succ}")
            print(batches, "Time taken: ", t)
    elif os.path.isdir(path):
        if not path.endswith("/"):
            path = path + "/"

        stats = []
        fNet = []
        pbar = tqdm(os.listdir(path))
        for f in pbar:
            file = path + f
            if file.endswith(".json"):
                ir = util.convert_edge_path_to_IR(file)
                b, rir, t, succ, __ = runSingle(ir)

                if succ:
                    stats.append({"network": f.removesuffix(".json"), "elapsedTime": t, "batches": b, "numberOfBatch": len(b), 'networkSize': len(ir.nodes)})
                else:
                    fNet.append(f.removesuffix(".json"))
                if t == -1:
                    print(f)

        if stats != []:
            print(f"Failed networks are: {fNet}")
            print(f"Number of failed networks {len(fNet)}")

        if stats != []:
            util.write_stats_to_csv(outDir, statName, stats)

    return True

def runSingle(ir: IR, OutputInfo: bool = False, msg = {}) -> Tuple[Union[List, None], IR, float, bool, List]:
    start = time.time()
    rir, b, succ, Ids = batchCalc(ir, True, msg)
    end = time.time()
    t = end - start

    start2 = time.time()
    rir2, b2, succ2, Ids2 = batchCalc(ir, True, msg, True)
    end2 = time.time()
    t2 = end2 - start2

    #print("\nBatches")
    #print(b)
    #print(b2)
    #print(t, t2)
    if b != None and b2 != None:
        if b != b2 and succ != succ2:
            print("Something wrong", succ, succ2)
            print(b)
            print(b2)
            return b, rir, -1, False, Ids
    

    if OutputInfo:
        if succ == False:
            print("Network Failed")
            print(f"length of r: {len(rir.r)}, and length of rm: {len(rir.rm)}")
            print(rir.r)
            print(rir.rm)
        print(f"Update batch sequence is: {b}")
        print(f"size of batch sequence is: {len(b)}")

    return b, rir, t, succ, Ids

def sort_nested_list(list):
    for l in list:
        l.sort()
