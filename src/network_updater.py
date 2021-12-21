from typing import Dict, List
from .network.IR import IR

# Update network towards rm, by only updating non_locked nodes
def update_network(currR: Dict, ir: IR) -> List:
    #List of the nodes that is added to this update batch
    upd_nodes = []

    for n in ir.nodes:
        node = ir.nodes[n]
        if node.lockNode == True:
            node.lockNode = False
        elif node in ir.r or node in ir.rm:
            #Update the valid node and add it to the batch
            if node in ir.r and ir.r[node] in ir.rev_r and node in ir.rev_r[ir.r[node]]:
                ir.rev_r[ir.r[node]].remove(node)
            
            if node not in ir.rm and node in ir.r:
                del ir.r[node]
            else:
                currR[node] = ir.rm[node]

            upd_nodes.append(node.id)

    #Return the updated batch, and if there is no updates it will just return an empty batch
    return upd_nodes

# Update network towards rm, by only updating non_locked nodes
def update_network_new(currR: Dict, ir: IR) -> List:
    #List of the nodes that is added to this update batch
    upd_nodes = []

    for n in ir.nodes:
        node = ir.nodes[n]
        if node.lockNode == True:
            node.lockNode = False
        elif node in ir.r or node in ir.rm:
            if node in ir.r and node in ir.rm and ir.r[node] == ir.rm[node]:
                continue
            #Update the valid node and add it to the batch
            if node in ir.r and ir.r[node] in ir.rev_r and node in ir.rev_r[ir.r[node]]:
                ir.rev_r[ir.r[node]].remove(node)
            
            if node not in ir.rm and node in ir.r:
                del ir.r[node]
            else:
                currR[node] = ir.rm[node]
                ir.r[node] = ir.rm[node]

            upd_nodes.append(node.id)

    #Return the updated batch, and if there is no updates it will just return an empty batch
    return upd_nodes
