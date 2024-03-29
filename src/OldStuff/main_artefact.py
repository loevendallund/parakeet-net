import os
from networkx.readwrite import text
from tqdm import tqdm
import time
import csv
import argparse
import json
from IR import IR
from batch_handler import find_batches
from edge_locker import determine_locked
from network_reducer import reduce_network, chain_reduction_r
from network_updater import update_network

def conv_artefact_to_ir(jsonLoc):
    file = open(jsonLoc, "r")
    data = json.load(file)
    file.close()

    return IR.from_dict_routes(data.get("Initial_routing"), data.get("Final_routing"), data.get("Properties"))

def write_output(outputDir, inputFolder, fname, b):
    if not os.path.isdir(outputDir):
        os.mkdir(outputDir)
    if not os.path.isdir(outputDir + "/" + inputFolder):
        os.mkdir(outputDir + "/" + inputFolder)
    f = fname.removesuffix(".json")

    textfile = open(outputDir + "/" + inputFolder + "/" + f + ".txt", "w")
    textfile.write("[")
    for i in range(len(b)):
        textfile.write("[")
        for j in range(len(b[i])):
            e = b[i][j]
            if j < len(b[i]) - 1:
                textfile.write(str(e) + ", ")
            else:
                textfile.write(str(e))
        if i < len(b) - 1:
            textfile.write("], ")
        else:
            textfile.write("]")
    textfile.write("]")
    textfile.close()

def write_debug(outputDir, inputFolder, fname, b, msg, cycles = []):
    if not os.path.isdir(outputDir):
        os.mkdir(outputDir)
    if fname != "":
        if not os.path.isdir(outputDir + "/" + inputFolder):
            os.mkdir(outputDir + "/" + inputFolder)
    f = fname.removesuffix(".json")
    if fname != "":
        dir = outputDir + "/" + inputFolder + "/" + f + "_debug.txt"
    else:
        dir = outputDir + "/" + inputFolder + "_debug.txt"

    textfile = open(dir, "w")

    for i in msg:
        textfile.write("Batch " + str(i + 1) + ":\n")
        if i < len(b):
            b[i].sort()
            textfile.write("    [")
            for j in range(len(b[i])):
                e = b[i][j]
                if j < len(b[i]) - 1:
                    textfile.write(str(e) + ", ")
                else:
                    textfile.write(str(e))
            textfile.write("]\n")
        
        tmp = msg[i]
        if 'loop' in tmp and tmp['loop'] != {}:
            loop = tmp['loop']
            textfile.write("Loop lock:\n    [")
            for j in range(len(loop)):
                e = loop[j]
                if j < len(loop) - 1:
                    textfile.write(str(e) + ", ")
                else:
                    textfile.write(str(e))
            textfile.write("]\n")
        if 'wp' in tmp and tmp['wp'] != {}:
            textfile.write("Nodes not reach before waypoint or target:\n")
            for key, val in tmp['wp'].items():
                textfile.write("  " + str(key) + ": ")
                textfile.write("[")
                for j in range(len(val)):
                    e = val[j]
                    if j < len(val) - 1:
                        textfile.write(str(e) + ", ")
                    else:
                        textfile.write(str(e))
                textfile.write("]\n")
        textfile.write("\n")

    if cycles != []:
        textfile.write("Known waypoint cycles: ")
        textfile.write("[")
        for j in range(len(cycles)):
            e = cycles[j]
            if j < len(cycles) - 1:
                textfile.write(str(e) + ", ")
            else:
                textfile.write(str(e))
        textfile.write("]\n")

    textfile.close()
    print(f"written debug file to: {dir}")

def runSingle(filePath, OutputData = False):
    ir = conv_artefact_to_ir(filePath)
    debugmsg = {}
    start = time.time()
    rir, b, succ, Ids = find_batches(ir, True, debugmsg)
    end = time.time()

    reduce_network(rir)
    if OutputData:
        if succ == False:
            print("Network Failed")
            print(f"length of r: {len(rir.r)}, and length of rm: {len(rir.rm)}")
            print(rir.r)
            print(rir.rm)
        print(f"Update batch sequence is: {b}")
        print(f"size of batch sequence is: {len(b)}")

    return b, debugmsg, ir, rir, end - start, succ, Ids

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("folder_to_test", help="Needs folder location for networks to test")
    parser.add_argument("--outputDir", default="output", help="Name of the desired output dir")
    parser.add_argument("--csv", default="output", help="Name of the desired output dir")
    parser.add_argument("--onlyOne", default=False, help="Set to true if only run on a single file")
    args = parser.parse_args()

    errorFiles = []
    stats = []
    biggestBatch = ["", 0]
    errorWP = []
    
    if args.onlyOne:
        #ir = conv_artefact_to_ir(args.folder_to_test)

        #debugmsg = {}
        #start = time.time()
        #rir, b, succ = find_batches(ir, True, debugmsg)
        #end = time.time()

        #reduce_network(rir)
        #if succ == False:
        #    print("Network Failed")
        #    print(f"length of r: {len(rir.r)}, and length of rm: {len(rir.rm)}")
        #    print(rir.r)
        #    print(rir.rm)
        #print(f"Update batch sequence is: {b}")
        #print(f"size of batch sequence is: {len(b)}")
        #print()

        b, debugmsg, ir, rir, time, succ, __ = runSingle(args.folder_to_test, True)


        slashSplit = args.folder_to_test.split('/')
        write_output(args.outputDir, slashSplit[0], slashSplit[1], b)

        write_debug(args.outputDir, args.folder_to_test, "", b, debugmsg)
        
        f = slashSplit[1].removesuffix("/")
        stats.append({"network": f.removesuffix(".json"), "elapsedTime": time, "batches": b, "numberOfBatch": len(b), 'networkSize': len(ir.nodes)})
        with open(args.outputDir + "/" + "stats_" + f + ".csv", mode="w") as csvFile:
            fieldNames = ['network', 'elapsedTime', 'batches', 'numberOfBatch', 'networkSize']
            w = csv.DictWriter(csvFile, fieldnames=fieldNames)

            w.writeheader()
            for i in stats:
                w.writerow(i)

        reduce_network(ir)
        chain_reduction_r(ir)
        determine_locked(ir, False, {}, {})
        __, __ = update_network(ir.r, ir, {}, [])
        reduce_network(ir)
        ir.draw_network()

        exit()

    for f in tqdm(os.listdir(args.folder_to_test)):
        ir = conv_artefact_to_ir(args.folder_to_test + "/" + f)
        
        start = time.time()
        rir, b, succ, __ = find_batches(ir)
        end = time.time()

        if succ:
            write_output(args.outputDir, args.folder_to_test, f, b)
            stats.append({"network": f.removesuffix(".json"), "elapsedTime": end - start, "batches": b, "numberOfBatch": len(b), 'networkSize': len(ir.nodes)})
            if biggestBatch[1] < len(b):
                biggestBatch = [f, len(b)]
        else:
            #errorFiles.append(f)
            out = [f]
            nest = []
            for wp in ir.wp:
                cycR = [ir.rev_r[ir.rev_r[ir.nodes[wp]][0]][0].id, ir.rev_r[ir.nodes[wp]][0].id, wp, ir.r[ir.nodes[wp]].id, ir.r[ir.r[ir.nodes[wp]]].id]
                cycRM = [ir.rev_rm[ir.rev_rm[ir.nodes[wp]][0]][0].id, ir.rev_rm[ir.nodes[wp]][0].id, wp, ir.rm[ir.nodes[wp]].id, ir.rm[ir.rm[ir.nodes[wp]]].id]
                nest.append([cycR, cycRM])
            out.append(nest)
            errorFiles.append(out)

    
    for f in errorFiles:
        print(f[0])
        print("This network is unsolvable")

        debugmsg = {}

        ir = conv_artefact_to_ir(args.folder_to_test + "/" + f[0])
        rir, b, succ = find_batches(ir, True, debugmsg)

        cycles = []
        for err in f[1]:
            if err[0][1] == err[1][3] and err[0][3] == err[1][1]:
                cycles.append(err[0][2])

        write_debug(args.outputDir, args.folder_to_test, f[0], b, debugmsg, cycles)
        print()

    
    f = args.folder_to_test.removesuffix("/")
    with open(args.outputDir + "/" + "stats_" + f + ".csv", mode="w") as csvFile:
        fieldNames = ['network', 'elapsedTime', 'batches', 'numberOfBatch', 'networkSize']
        w = csv.DictWriter(csvFile, fieldnames=fieldNames)

        w.writeheader()
        for i in stats:
            w.writerow(i)

    print("The max amount of batches found is:", biggestBatch)
