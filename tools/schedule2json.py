#!/usr/bin/python

import csv
import hashlib
import json
import os
import re
import sys
import time
import urllib2

SCHEDULE_URL="https://docs.google.com/spreadsheet/pub?hl=en_US&hl=en_US&key=0ArpWuvdaFmPYdC15Tm0xWlZEVFp3UDhYWkM4eHlPRGc&single=true&gid=1&output=csv"

def convertDate(date, start):
    t = time.strptime("%s %s" % (date, start), "%Y-%m-%d %H:%M")
    return int(time.mktime(t))

def parseRooms(record):
    index = -1
    result = list()
    for name in record:
        index += 1
        if name.startswith("D") or name.startswith("Lab"):
            result.append((name, index)) 
    return result

EVENT_PATTERN = re.compile("^(?P<speaker>[\w\s,]+)-(?P<topic>[^[]+)(\[(?P<tags>[\w\s,]+)\])?$", flags = re.UNICODE)

def parseEventDesc(event):
    #@print "EVENT:", event
    event = unicode(event.strip(), "UTF-8")
    match = EVENT_PATTERN.match(event)
    if match:
        # pattern is OK, extract data
        return dict(
            speaker = match.group("speaker").strip().encode("UTF-8"),
            topic = match.group("topic").strip().encode("UTF-8"),
            tags = match.group("tags").strip().encode("UTF-8"),
        )
    else:
        # incorrect pattern, treat whole text as topic
        return dict(
            speaker = "",
            topic = event.encode("UTF-8"),
            tags = "",
        )

def schedule2json(inp, timestamp):
    result = list()
    date = None
    rooms = None
    topics = dict()
    hash = hashlib.sha256()
    for record in csv.reader(inp):
        print 80 * "-"
        print "IN:", record
        hash.update(str(record))
        #print "DATE:", date
        #print "ROOMS:", rooms
        # skip empty rows
        if not record:
            continue
        # detect beginnging of a day
        if record[0] == "Friday":
            date = "2012-02-17"
            rooms = parseRooms(record) 
            continue
        elif record[0] == "Saturday":
            date = "2012-02-18"
            rooms = parseRooms(record) 
            continue
        # parse the record (aka row)
        # parse time
        try:
            start, end = record[0].split("-")
        except ValueError:
            # this is not a valid start-end, ignore this row
            continue
        # parse individual talks/labs
        for name, index in rooms:
            output = dict()
            if index >= len(record) or not record[index].strip():
                # empty cell, skip
                continue
            if name.startswith("D"):
                output["type"] = "talk"
            elif name.startswith("Lab"):
                output["type"] = "lab"
            if record[index].startswith("Social event"):
                output["type"] = "social"
                name = "N/A"
            output["date"] = date
            output["start"] = start
            output["end"] = end
            output["room"] = name
            output["speaker"] = "N/A"
            output["topic"] = "N/A"
            output["tags"] = ""
            output["location"] = "FIMUNI"
            output["description"] = ""
            output["timestamp"] = convertDate(date, start)
            output.update(parseEventDesc(record[index]))
            if "CZ" in output["tags"]:
                output["language"] = "CZ"
            else:
                output["language"] = "EN"
            # check if this is continuation of a previous talk/lab
            if output["topic"].endswith("(cont)"):
                topic = output["topic"][:-7]
                print "CONTINUE: '%s'" % topic
                # find original topic to extend
                topics[topic]["end"] = output["end"]
                print
                print "OUT: EXTENDED EXISTING TOPIC", topic
                continue
            # record topic
            topics[output["topic"]] = output
            print
            print "OUT:", output
            result.append(output)
    digest = hash.hexdigest()
    return dict(items = result, timestamp = timestamp, checksum = digest)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print >>sys.stderr, "Dirname expected"
        sys.exit(1)
    outDir = sys.argv[1]
    
    # convert schedule to json
    fh = urllib2.urlopen(SCHEDULE_URL)
    print fh.info()
    timestamp = int(time.time())
    data = schedule2json(fh , timestamp)
    
    try:
        old = json.load(open(os.path.join(outDir, "schedule.json"), "r"))
    except IOError:
        old = dict(checksum = None)
    
    print 80 * "-"
    if old["checksum"] != data["checksum"]:
        print "Updading JSON files"
        # update schedule and timestamp
        open(os.path.join(outDir, "schedule.json"), "w").write(json.dumps(data))
    
        # write timestamp
        open(os.path.join(outDir, "schedule-ts.json"), "w").write(json.dumps(timestamp))

        # write checksum
        open(os.path.join(outDir, "schedule-cksum.json"), "w").write(json.dumps(data["checksum"]))

    else:
        print "NOT updating JSON files"