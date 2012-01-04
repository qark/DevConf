import csv
import json
import sys

def csv2json(inp, out):
    result = list()
    for record in csv.DictReader(inp):
        result.append(record)
    out.write(json.dumps(dict(items = result)))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print >>sys.stderr, "Filename expected"
        sys.exit(1)
    csv2json(open(sys.argv[1], "r"), sys.stdout)

