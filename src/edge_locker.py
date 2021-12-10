from .IR import IR
from .IR import simple as testnet

def determine_locked(ir: IR, debug = False, debugMsg = {}):
    # Lets set up some state
    # Seen are the nodes we have seen while running over R
    seen = set()
    current = ir.source
    #locked = set()
    # Maps nodes with the one pointing at them.
    # Used to keep track of edges we can potentially add.
    potentials = {}

    while current in ir.r or current == ir.target:
        fnext = ir.rm.get(current, None)
        #print(f"at {current}, fn: {fnext}, pot: {potentials}, seen: {seen}, locked: {locked}")

        if current.id in potentials:
            # So we can reach the potential locked node
            # therefore it can be unlocked
            potentials.pop(current.id)

        if current.wpMark:
            # We reached a waypoint, so we lock all potentially locked
            # nodes.
            #locked = locked.union(set(potentials.values()))
            for i in potentials:
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
        elif fnext.id in seen:
            # Okay this will create a loop, lock it
            #locked.add(current.id)
            current.lockNode = True
            if 'loop' not in debugMsg:
                debugMsg['loop'] = []
            if debug:
                debugMsg['loop'].append(current.id)
                
        else:
            # Okay this points somewhere we haven't seen before.
            # Better save this for later.
            # We index with the fnext, so we can look it up by `currrent` later
            # and then lock the correct node.
            potentials[fnext.id] = current.id

        seen.add(current.id)
        if current in ir.r:
            current = ir.r[current]
        else:
            break


    for i in potentials:
        #if i in tree and tree[i]["reach"] == True and "path" in tree[i] and i not in seen:
        #    print("fish", i, potentials[i], tree[i]["path"], ir.target.id)
        #    continue
        ir.nodes[potentials[i]].lockNode = True
    if debug:
        locked = []
        for i in potentials:
            locked.append(potentials[i])

        if 'wp' not in debugMsg:
            debugMsg['wp'] = {}
        debugMsg['wp'][ir.target.id] = locked

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


if __name__ == "__main__":
    ir = testnet()
    print(ir.to_serial())
    print("heyho", ir.nodes)
