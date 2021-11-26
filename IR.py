from dataclasses import dataclass
from typing import List, Dict, Tuple, Set
import networkx as nx
import json

from node import Route, Node


def nodelist_do_dict(nodes):
    res = {}
    nlast = None
    for i, n in enumerate(nodes):
        if i != 0:
            assert nlast is not None
            res[nlast] = n

        nlast = n

    return res

def nodelist_to_rev_dict(nodes):
    res = {}
    nlast = None
    prev = None
    for i, n in enumerate(nodes):
        if i != 0:
            assert nlast is not None
            if prev is not None:
                l = [prev]
                res[nlast] = l
        prev = nlast
        nlast = n

    res[nlast] = [prev]

    return res


@dataclass
class IR:
    nodes: Dict[int, Node]
    source: Node
    target: Node
    r: Dict[Node, Node]
    rev_r: Dict[Node, List]
    rm: Dict[Node, Node]
    rev_rm: Dict[Node, List]
    wp: List

    @classmethod
    def from_string_routes(cls, r: List[int], rm: List[int], way: Set[int]):
        nodes = {}

        def int_to_node(id):
            node = Node(id, id in way)
            if id not in nodes:
                nodes[id] = node
            return nodes[id]

        sr = nodelist_do_dict(map(int_to_node, r))
        rev_sr = nodelist_to_rev_dict(map(int_to_node, r))
        srm = nodelist_do_dict(map(int_to_node, rm))
        rev_srm = nodelist_to_rev_dict(map(int_to_node, rm))


        return cls(
            nodes=nodes,
            source=nodes[r[0]],
            target=nodes[r[-1]],
            r=sr,
            rev_r=rev_sr,
            rm=srm,
            rev_rm=rev_srm,
            wp = []
        )
    @classmethod
    def from_dict_routes(cls, r: Dict, rm: Dict, properties: Dict):
        nodes = {}
        waypoints = []

        way = properties.get("Waypoint")
        reach = properties.get("Reachability")

        if type(way.get("waypoint")) == int:
            waypoints.append(way.get("waypoint"))
        else:
            for i in way.get("waypoint"):
                waypoints.append(i)


        def dict_to_nodes(dict):
            for n1, n2 in dict:
                node1 = Node(n1, n1 in waypoints)
                if n1 not in nodes:
                    nodes[n1] = node1
                node2 = Node(n2, n2 in waypoints)
                if n2 not in nodes:
                    nodes[n2] = node2

        def intDict_to_nodeDict(dict):
            res = {}
            for n1, n2 in dict:
                res[nodes[n1]] = nodes[n2]
            return res

        def intDict_to_rev_nodeDict(dict):
            res = {}
            for n1, n2 in dict:
                if nodes[n2] not in res:
                    res[nodes[n2]] = [nodes[n1]]
                else:
                    res[nodes[n2]].append(n1)
            return res

        dict_to_nodes(r)
        dict_to_nodes(rm)
        sr = intDict_to_nodeDict(r)
        rev_sr = intDict_to_rev_nodeDict(r)
        srm = intDict_to_nodeDict(rm)
        rev_srm = intDict_to_rev_nodeDict(rm)

        return cls(
            nodes = nodes,
            source=nodes[reach.get("startNode")],
            target=nodes[reach.get("finalNode")],
            r=sr,
            rev_r=rev_sr,
            rm=srm,
            rev_rm=rev_srm,
            wp = waypoints
        )

    def to_serial(self):
        def map_node_route(r):
            return {str(k.id): n.id for k, n in r.items()}

        return {
            "nodes": {k: n.to_serial() for k, n in self.nodes.items()},
            "source": self.source.id,
            "target": self.target.id,
            "r": map_node_route(self.r),
            "rm": map_node_route(self.rm),
        }


def next_node(self, list, current_node):
    if list.index(current_node) == len(list) - 1:
        return -1
    return list[list.index(current_node) + 1]


def prev_node(self, list, current_node):
    if list.index(current_node) == 0:
        return -1
    return list[list.index(current_node) - 1]


def testnet_arrow() -> IR:
    return IR.from_string_routes(
        [1, 2, 4, 5],
        [1, 3, 4, 2, 5],
        set([4]),
    )

def testnet_boat() -> IR:
    return IR.from_string_routes(
        [1, 2, 3, 4],
        [1, 2, 5, 6, 3, 4],
        set([2, 3]),
    )

def testnet_boat2() -> IR:
    return IR.from_string_routes(
        [1, 2, 3, 4],
        [1, 2, 5, 6, 4],
        set([1, 2]),
    )

def testnet_reduct1() -> IR:
    return IR.from_string_routes(
        [1, 2, 3, 4, 5],
        [1, 4, 2, 3, 5],
        set([4]),
    )

def testnet_test() -> IR:
    return IR.from_string_routes(
        [1, 7, 2, 3, 4, 5, 6],
        [1, 7, 4, 3, 2, 5, 6],
        set([7]),
    )
