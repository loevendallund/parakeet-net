import copy
from .network.IR import IR
from .network.IR import testnet_test as testnet
from .edge_locker import determine_locked, determine_locked_new
from .network_reducer import reduce_network
from .network_updater import update_network, update_network_new

def find_batches(ir: IR, debug = False, msg = {}, newHandler = False):
    batches = []
    next_batch_holder = []
    redNodesId = []
    chain = {}
    rir = copy.deepcopy(ir)
    first = True
    i = 0
    updSet = set()

    if newHandler:
        while True:
            if debug:
                #lock, and get debug messages from edge locker
                debugmsg = {}
                if not determine_locked_new(rir, debug, debugmsg):
                    msg[i] = debugmsg
                    return rir, batches, False, redNodesId
                msg[i] = debugmsg
                i = i + 1
            else:
                #lock
                if not determine_locked_new(rir, debug):
                    return rir, batches, False, redNodesId

            #update
            b = update_network_new(rir.r, rir)

            #Check if the batch is empty, if it is return the batches and the updated version of ir(debuggin purpose)
            if b == []:
                return rir, batches, True, redNodesId

            #Append the batch to the list of batches
            batches.append(b)

    while True:
        #reduce
        reduce_network(rir)

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
        b = update_network(rir.r, rir)

        #Check if the batch is empty, if it is return the batches and the updated version of ir(debuggin purpose)
        if b == []:
            return rir, batches, True, redNodesId

        #Append the batch to the list of batches
        batches.append(b)
