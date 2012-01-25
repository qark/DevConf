#!/usr/bin/python
import csv
import json
import os
import sys
import time

def convertDate(date, start):
    t = time.strptime("%s %s" % (date, start), "%Y-%m-%d %H:%M")
    return int(time.mktime(t))

def csv2json(inp, out):
    result = list()
    for record in csv.DictReader(inp):
        record["timestamp"] = convertDate(record["date"], record["start"])
        result.append(record)
    out.write(json.dumps(dict(items = result)))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print >>sys.stderr, "Dirname expected"
        sys.exit(1)

    # convert csv to json
    inFile, outDir = sys.argv[1:]
    csv2json(open(inFile, "r"), open(os.path.join(outDir, "schedule.json"), "w"))
    
    # write timestamp
    open(os.path.join(outDir, "schedule-ts.json"), "w").write(json.dumps(int(time.time())))
