from .network.IR import IR
from .network.IR import testnet_reduct1 as testnet
from .network.node import Node

#Takes Ir as an input at applies reduction on it by going through all nodes in rm
def reduce_network(ir: IR):
    #remNodes is the collection of nodes to remove
    remNodes = []

    #Iterate over all nodes in rm, to find applicable nodes to reduce
    for node in ir.rm:
        if similarity_reduction(ir, node):
            remNodes.append(node)
   
    #Removing nodes, this is done since we can't remove nodes from rm, while we iterate over it (we could maybe also copy the nodes)
    for node in remNodes:
        #if node in ir.rev_rm:
        #    for i in ir.rev_rm[node]:
        #        if i in ir.rm:
        #            ir.rm[i] = ir.r[node]
        del ir.r[node]
        del ir.rm[node]


def similarity_reduction(ir: IR, node: Node):
    #First, we want to return if node is target or it doesn't exist in the current route r
    if node == ir.target or node not in ir.r:
        return False
    #Check if the routing for the node is the same in r and rm
    if ir.r[node] == ir.rm[node]:
        #Make a ref to the next node, we only need one since the next node is the same in the routing tables r and rm
        nnode = ir.r[node]
        #Check if the current has a previous node in routing r and update where it points to
        if node in ir.rev_r and nnode in ir.rev_r:
            if node in ir.rev_r[nnode]:
                idx = ir.rev_r[nnode].index(node)
                del ir.rev_r[nnode][idx]
            for i in ir.rev_r[node]:
                if i in ir.rm or i in ir.r:
                    ir.r[i] = nnode
                if i in ir.r:
                    ir.rev_r[nnode].append(i)
        
        #Check if the current has a previous node in routing rm and update where it points to
        if node in ir.rev_rm:
            if node in ir.rev_rm[nnode]:
                idx = ir.rev_rm[nnode].index(node)
                del ir.rev_rm[nnode][idx]
            for i in ir.rev_rm[node]:
                if i in ir.rm:
                    ir.rm[i] = nnode
                if i in ir.rm:
                    ir.rev_rm[nnode].append(i)
       
        #If the current node is the source node, update it to be the next node "nnode"
        if node == ir.source:
            ir.source = nnode
        #Update the node collection for "nnode" to contain the current node and the current node's node collection
        nnode.Nodes.append(node)
        nnode.Nodes.extend(node.Nodes)
        node.Nodes = []
        
        #return true, to indicate that the current node needs to be removed
        return True
    #return false if the current node should not be removed
    return False
        

def chain_reduction_r(ir: IR):
    remNodes = []
    chainNodes = {}
    chainNodesId = []
    for node in ir.r:
        if node not in ir.rm:
            if node in ir.rev_r:
                for i in ir.rev_r[node]:
                    ir.r[i] = ir.r[node]
                    if i in ir.rm:
                        if i not in chainNodes:
                            chainNodes[i] = [node]
                            chainNodesId.append(node.id)
                        else:
                            chainNodes[i].append(node)
                            chainNodesId.append(node.id)
                for i in ir.rev_r[ir.r[node]]:
                    ir.rev_r[ir.r[i]] = ir.rev_r[node]
            remNodes.append(node)

    for n in remNodes:
        del ir.r[n]

    return chainNodes, chainNodesId
    #print("chainNodes:", chainNodes)

#This will maybe be implemented, but is outcommented, since i don't like to look at those errors...
#def chain_reduction(node1, node2, node3, node4):
#    node_collection = node1
#    return nodeCollection

if __name__ == "__main__":
    ir = testnet()
    print(ir.to_serial())
    print("ir nodes: ", ir.nodes)

    print("ir r: ", ir.r)
