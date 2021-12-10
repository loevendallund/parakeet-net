import argparse
import json
from IR import IR
from batch_handler import find_batches

def conv_to_ir(metaLoc):
    file = open(metaLoc, "r")
    data = json.load(file)
    file.close()

    return IR.from_string_routes(data.get("r"), data.get("rm"), data.get("waypoints"))

def write_output(b):
    textfile = open("output.txt", "w")
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("metadata_location", help="Needs metadata file as input in json format")
    args = parser.parse_args()
    ir = conv_to_ir(args.metadata_location)

    rir, b, succ = find_batches(ir)

    print(f"Update batch sequence is: {b}")
    print(f"size of batch sequence is: {len(b)}")
    write_output(b)
