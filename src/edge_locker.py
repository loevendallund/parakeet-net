from types import NoneType
from .network.IR import IR
from .network.IR import simple as testnet

def determine_locked(ir: IR, debug = False, debugMsg = {}) -> bool:
    # Lets set up some state
    # Seen are the nodes we have seen while running over R
    seen = set()
    current = ir.source
    # Maps nodes with the one pointing at them.
    # Used to keep track of edges we can potentially add.
    potentials = {}

    while current in ir.r or current == ir.target:
        fnext = ir.rm.get(current, None)

        if current.id in potentials:
            # So we can reach the potential locked node
            # therefore it can be unlocked
            potentials.pop(current.id)

        if current.wpMark:
            # We reached a waypoint, so we lock all potentially locked
            # nodes.
            for i in potentials:
                #print(ir.nodes[potentials[i]].id, "is locked")
                ir.nodes[potentials[i]].lockNode = True
            if debug:
                locked = []
                for i in potentials:
                    locked.append(potentials[i])
                if 'wp' not in debugMsg:
                    debugMsg['wp'] = {}
                debugMsg['wp'][current.id] = locked
            potentials = {}

        if fnext is None:
            # Okay no node in R'
            pass
        else:
            # Okay this points somewhere we haven't seen before.
            # Better save this for later.
            # We index with the fnext, so we can look it up by `currrent` later
            # and then lock the correct node.
            potentials[fnext.id] = current.id
        if current not in ir.rm:
            current.lockNode = True

        seen.add(current.id)
        if current in ir.r:
            current = ir.r[current]
        else:
            break


    for i in potentials:
        ir.nodes[potentials[i]].lockNode = True
    if debug:
        locked = []
        for i in potentials:
            locked.append(potentials[i])

        if 'wp' not in debugMsg:
            debugMsg['wp'] = {}
        debugMsg['wp'][ir.target.id] = locked

    return stillCorrect(ir)

def determine_locked_new(ir: IR, debug = False, debugMsg = {}) -> bool:
    # Lets set up some state
    # Seen are the nodes we have seen while running over R
    seen = set()
    current = ir.source
    # Maps nodes with the one pointing at them.
    # Used to keep track of edges we can potentially add.
    potentials = {}
    print()
    while current in ir.r or current == ir.target:
        fnext = ir.rm.get(current, None)

        if current.id in potentials:
            # So we can reach the potential locked node
            # therefore it can be unlocked
            potentials.pop(current.id)

        if current.wpMark:
            # We reached a waypoint, so we lock all potentially locked
            # nodes.
            for i in potentials:
                #print(ir.nodes[potentials[i]].id, "is locked")
                ir.nodes[potentials[i]].lockNode = True
            if debug:
                locked = []
                for i in potentials:
                    locked.append(potentials[i])
                if 'wp' not in debugMsg:
                    debugMsg['wp'] = {}
                debugMsg['wp'][current.id] = locked
            potentials = {}

        if fnext is None:
            # Okay no node in R'
            pass
        else:
            # Okay this points somewhere we haven't seen before.
            # Better save this for later.
            # We index with the fnext, so we can look it up by `currrent` later
            # and then lock the correct node.
            potNode = search_path(fnext, ir)
            if type(potNode) != NoneType:
                potentials[potNode.id] = current.id
            else:
                potentials[fnext.id] = current.id
        if current not in ir.rm:
            current.lockNode = True

        seen.add(current.id)
        if current in ir.r:
            current = ir.r[current]
        else:
            break


    for i in potentials:
        ir.nodes[potentials[i]].lockNode = True
    if debug:
        locked = []
        for i in potentials:
            locked.append(potentials[i])

        if 'wp' not in debugMsg:
            debugMsg['wp'] = {}
        debugMsg['wp'][ir.target.id] = locked

    return stillCorrect(ir)

def search_path(node, ir: IR):
    if node not in ir.r or node not in ir.rm:
        return node
    else:
        if node.wpMark or node.id == ir.target.id:
            return node
        elif ir.r[node].id == ir.rm[node].id:
            return search_path(ir.r[node], ir)
        else:
            return node


def stillCorrect(ir: IR) -> bool:
    #First check if theres even something in rm
    if ir.rm != {}:
        for node in ir.rm:
            #We need to check the instance of the node in the nodes list, cause python is stupid af
            if ir.nodes[node.id].lockNode == False:
                #if one node is not locked just break, since we found a node that can be updated
                return True
            #If all nodes are locked then we wil throw an exception
        return False
        #raise Exception("Error, all nodes a locked, thus the network cannot be solved");
    return True
