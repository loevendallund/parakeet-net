from typing import List, Set, Dict
import itertools
from IR import IR
from node import Node


def generate_combinations(batches: List[Set[Node]], func, args):
    thispart = set()
    while len(thispart) == 0:
        if len(batches) == 0:
            return True
        thispart = batches[0]
        batches = batches[1:]

    for node in thispart:
        newargs = func(args, node)
        if newargs == None:
            return False
        next = [thispart.difference(set([node]))] + batches
        if generate_combinations(next, func, newargs) == False:
            return False


def update_route(r: Dict[Node, Node], rm: Dict[Node, Node], batch: Set[Node]):
    res = r.copy()
    for node in batch:
        res[node] = rm[node]

    return res


def check_route(r: Dict[Node, Node], source: Node, target: Node, ways: Set[Node]):
    at = source
    while at:
        if at in ways:
            ways.remove(at)
        if at == target:
            return len(ways) == 0

        at = r.get(at, None)

    return False


def check_batch_seq(ir: IR, batches_int: List[List[int]]):
    batches = []
    for batch in batches_int:
        batches.append(
            {ir.nodes[nid] for nid in batch})
    checked = 0

    ways = set()
    for id, node in ir.nodes.items():
        if node.wpMark:
            ways.add(node)

    print("Checking network with ways:", ways)

    def pretty(thing):
        return [n.id for n in thing]

    def testfunc(pre, new):
        nonlocal checked, ir

        (pre, state) = pre

        comb = pre + [new]
        checked += 1

        if (checked % 10000) == 0:
            print("\rat:", checked, end="")

        state = update_route(state, ir.rm, set([new]))
        okay = check_route(state, ir.source, ir.target, ways)
        if not okay:
            print(f"\nFailed with applied nodes: {comb}")
            return None
        return (comb, state)

    generate_combinations(batches, testfunc, ([], ir.r))

    print(f"\nOkay after {checked} checks")
    return True
