from typing import List, Dict

class Node:
    id: int #Must be unique
    cycleMark: bool
    wpMark: bool
    lockNode: bool
    Nodes: List #Should be empty unless node represents a node collection

    def __init__(self, id, way: bool = False):
        self.id = id
        self.cycleMark = False
        self.wpMark = way
        self.lockNode = False
        self.Nodes = []

    def __repr__(self):
        string = ""
        if self.Nodes:
            string = ", nodes = ["
            for n in self.Nodes:
                string = string + str(n.id) + ","
            string = string[:-1] + "]"

        return "(id = " + str(self.id) + ", cM = " + str(self.cycleMark) + ", wpM = " + str(self.wpMark) + string + ")"

    def __str__(self):
        string = ""
        if self.Nodes:
            string = ", nodes = ["
            for n in self.Nodes:
                string = string + str(n.id) + ","
            string = string[:-1] + "]"

        return "(id = " + str(self.id) + ", cM = " + str(self.cycleMark) + ", wpM = " + str(self.wpMark) + ", locked = " + str(self.lockNode) + string + ")"

    def to_serial(self):
        return {"id": self.id, "wpMark": self.wpMark}

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id


class Route:
    nodes: Dict[Node, Node]

    @classmethod
    def from_seq_nodes(cls, nodes: List[Node]) -> "Route":
        self = cls()
        nlast = nodes[0]
        for n in nodes[1:]:
            self.nodes[nlast] = n
            nlast = n

        return self

    def __getitem__(self, key):
        return self.nodes.get(key)

    def __contains__(self, key):
        return key in self.nodes
