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
    parser.add_argument("--Flip", default=False)
    args = parser.parse_args()

    succ = {}
    fail = {}
    numSucc = 0
    numFail = 0
