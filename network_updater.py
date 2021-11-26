from typing import Dict
from IR import IR

# Update network towards rm, by only updating non_locked nodes
def update_network(currR: Dict, ir: IR):
    #List of the nodes that is added to this update batch
    upd_nodes = []
    
    #Iterate over all nodes in network to check if it should be updated, still needs further clamping, to make sure that only valid nodes are removed
    for node in ir.rm:
        #node = ir.nodes[i]
        #Check if the node exist in rm and isn't locked
        if node.lockNode != True and node in ir.rm:
            #Update the valid node and add it to the batch
            currR[node] = ir.rm[node]
            upd_nodes.append(node.id)
        else:
            #Make sure the node is unlocked, so that we can check it again later
            node.lockNode = False

    #Return the updated batch, and if there is no updates it will just return an empty batch
    return upd_nodes
