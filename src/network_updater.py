from typing import Dict, List
from .IR import IR

# Update network towards rm, by only updating non_locked nodes
def update_network(currR: Dict, ir: IR, chain: Dict, current_batch: List):
    #List of the nodes that is added to this update batch
    upd_nodes = []
    for i in current_batch:
        upd_nodes.append(i.id)
    next_batch = []
    
    #Iterate over all nodes in network to check if it should be updated, still needs further clamping, to make sure that only valid nodes are removed
    for node in ir.rm:
        #Check if the node exist in rm and isn't locked
        if node.lockNode != True and node in ir.rm:
            if node in chain:
                for i in chain[node]:
                    next_batch.append(i)
            #Update the valid node and add it to the batch
            if node in ir.r and ir.r[node] in ir.rev_r and node in ir.rev_r[ir.r[node]]:
                ir.rev_r[ir.r[node]].remove(node)
            
            currR[node] = ir.rm[node]

            upd_nodes.append(node.id)
        else:
            #Make sure the node is unlocked, so that we can check it again later
            node.lockNode = False

    #Return the updated batch, and if there is no updates it will just return an empty batch
    return upd_nodes, next_batch
