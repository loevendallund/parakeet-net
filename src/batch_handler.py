import copy
from .IR import IR
from .IR import testnet_test as testnet
from .edge_locker import determine_locked
from .network_reducer import reduce_network, chain_reduction_r
from .network_updater import update_network

def find_batches(ir: IR, debug = False, msg = {}):
    batches = []
    next_batch_holder = []
    redNodesId = []
    chain = {}
    rir = copy.deepcopy(ir)
    first = True
    i = 0

    while True:
        #reduce
        reduce_network(rir)

        #If this is the first round, run chain reduction
        if first:
            chain, redNodesId = chain_reduction_r(rir)
            first = False
        
        if debug:
            #lock, and get debug messages from edge locker
            debugmsg = {}
            if not determine_locked(rir, debug, debugmsg):
                msg[i] = debugmsg
                return rir, batches, False, redNodesId
            msg[i] = debugmsg
            i = i + 1
        else:
            #lock
            if not determine_locked(rir, debug):
                return rir, batches, False, redNodesId

        #update
        b, next_batch_holder = update_network(rir.r, rir, chain, next_batch_holder)

        #Check if the batch is empty, if it is return the batches and the updated version of ir(debuggin purpose)
        if b == []:
            return rir, batches, True, redNodesId

        #Append the batch to the list of batches
        batches.append(b)
