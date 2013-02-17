#!/usr/bin/python

import csv
import hashlib
import json
import os
import re
import sys
import time
import urllib2

SCHEDULE_URL = "https://docs.google.com/spreadsheet/pub?key=0AhQ3e-COC8cadHR2anJEU3lZZV9QcGp4cnpmNF80dmc&single=true&gid=0&output=csv"

FLOORS = {
  "Tower Big": "5th floor",
  "Tower Small": "5th floor",
  "Visitors": "4th floor",
  "Spring": "4th floor",
  "Autumn": "4th floor",
  "Winter": "4th floor",
  "Enclave": "3rd floor",
  "Red": "2nd floor",
  "Mint": "ground floor",
  "Apple": "ground floor",
  "Cherry": "ground floor",
}

def convertDate(date, start):
    t = time.strptime("%s %s" % (date, start), "%Y-%m-%d %H:%M")
    return int(time.mktime(t))

def parseRooms(record):
    index = -1
    result = list()
    for name in record:
        index += 1
        if name.startswith("DATE") or "[IGNORE]" in name:
            continue
        result.append((name, index))
    return result

def parseRoomName(name):
    if "-" in name:
        print name
        room, location = name.split("-")
        room = room.strip()
        return room, FLOORS[room]
    else:
        return name, "REDHAT"

EVENT_PATTERN1 = re.compile("^(?P<speaker>[\w\s,]+)-(?P<topic>[^[]+)(\[(?P<tags>[\w\s,]+)\])?$", flags = re.UNICODE)
EVENT_PATTERN2 = re.compile("^(?P<topic>[^[]+)(\[(?P<tags>[\w\s,]+)\])?$", flags = re.UNICODE)

def parseEventDesc(event):
    description = "N/A"
    if "\n" in event:
        description = event[event.index("\n") + 1:]
        event = event[:event.index("\n")]
    print "EVENT:", event
    print "DESCRPTION:", description
    event = unicode(event.strip(), "UTF-8")
    match1 = EVENT_PATTERN1.match(event)
    match2 = EVENT_PATTERN2.match(event)
    if match1:
        # pattern is OK, extract data
        tags = ""
        if match1.group("tags"):
            tags = match1.group("tags").strip().encode("UTF-8")
        return dict(
            speaker = match1.group("speaker").strip().encode("UTF-8"),
            topic = match1.group("topic").strip().encode("UTF-8"),
            tags = tags,
            description = description,
        )
    elif match2:
        # pattern is OK, extract data
        tags = ""
        if match2.group("tags"):
            tags = match2.group("tags").strip().encode("UTF-8")
        return dict(
            speaker = "N/A",
            topic = match2.group("topic").strip().encode("UTF-8"),
            tags = tags,
            description = description,
        )        
    else:
        # treat whole text as topic
        return dict(
            speaker = "N/A",
            topic = event.encode("UTF-8"),
            tags = "",
            description = description,
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
        # detect beginning of a day
        if record[0].startswith("DATE:"):
            date = "2012-04-04"
            rooms = parseRooms(record) 
            continue
        # parse the record (aka row)
        # parse time
        try:
            start, end = [i.strip() for i in record[0].split("-")]
        except ValueError:
            # this is not a valid start-end, ignore this row
            continue
        # parse individual talks/labs
        for name, index in rooms:
            output = dict()
            if index >= len(record) or not record[index].strip():
                # empty cell, skip
                continue
            output["type"] = "talk"
            room, location = parseRoomName(name)
            output["date"] = date
            output["start"] = start
            output["end"] = end
            output["room"] = room
            output["speaker"] = "N/A"
            output["topic"] = "N/A"
            output["description"] = "N/A"
            output["tags"] = ""
            output["location"] = location
            output["timestamp"] = convertDate(date, start)
            output["timestamp_end"] = convertDate(date, end)
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
                topics[topic]["timestamp_end"] = convertDate(date, output["end"])
                print
                print "OUT: EXTENDED EXISTING TOPIC", topic
                continue
            # get description
            if output["description"] == "N/A":
                print "WARNING: MISSING DESCRIPTION FOR", output["topic"]
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
    timestamp = int(time.time())
    data = schedule2json(fh, timestamp)
    del fh
    
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
