#!/usr/bin/python
import hashlib
import json
import os
import sys
import time
import urllib
import urllib2

SCHEDORG_URL = "http://developerconference2013.sched.org/api/"
SCHEDORG_RONLY_API_KEY = "001ce564d168d2c6a277616c8ef943b6"

def convertDate(text):
    t = time.strptime(text, "%Y-%m-%d %H:%M:%S")
    return int(time.mktime(t))

def removeHTMLTags(text):
    return text
    text = text.replace("<p>", "")
    text = text.replace("</p>", "\n")
    text = text.replace("<br />", "\n")
    text = text.replace("<ul>", "\n")
    text = text.replace("</ul>", "\n")
    text = text.replace("<li>", "- ")
    text = text.replace("</li>", "")
    text = text.replace("&nbsp;", " ")
    assert "<" not in text, text
    assert ">" not in text, text
    assert "&nbsp;" not in text, text
    return text.strip()

def schedule2json(inp, timestamp):
    result = list()
    date = None
    rooms = None
    topics = dict()
    hash = hashlib.sha256(inp)
    for record in json.loads(inp):
        print 80 * "-"
        print "IN:", record
        #print "DATE:", date
        #print "ROOMS:", rooms
        output = dict()
        output["type"] = "talk"
        output["date"] = record["event_start"][:10]
        output["start"] = record["event_start"][-8:-3]
        output["end"] = record["event_end"][-8:-3]
        output["room"] = record["venue"]
        output["speaker"] = record["speakers"]
        output["topic"] = record["name"]
        output["description"] = removeHTMLTags(record.get("description", "N/A"))
        output["tags"] = []
        if "event_type" in record:
            output["tags"].append(record["event_type"])
        output["location"] = "MUNI"
        output["timestamp"] = convertDate(record["event_start"])
        output["timestamp_end"] = convertDate(record["event_end"])
        if "CZ" in output["tags"]:
            output["language"] = "CZ"
        else:
            output["language"] = "EN"
        print
        print "OUT:", output
        result.append(output)
    # sort schedule by timestamp (primary key) and room name (secondary key)
    result.sort(key = lambda a: a["room"])
    result.sort(key = lambda a: a["timestamp"])
    return dict(items = result, timestamp = timestamp, checksum = hash.hexdigest())

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print >>sys.stderr, "Dirname expected"
        sys.exit(1)
    outDir = sys.argv[1]
    
    # convert schedule to json
    data = urllib.urlencode({
        "api_key": SCHEDORG_RONLY_API_KEY,
        "format": "json",
    })
    schedule = urllib2.urlopen(SCHEDORG_URL + "session/list", data).read()
    timestamp = int(time.time())
    data = schedule2json(schedule, timestamp)
    
    try:
        old = json.load(open(os.path.join(outDir, "schedule.json"), "r"))
    except IOError:
        old = dict(checksum = None)
    
    print 80 * "-"
    if old["checksum"] != data["checksum"] or True:
        print "Updading JSON files"
        # update schedule and timestamp
        open(os.path.join(outDir, "schedule.json"), "w").write(json.dumps(data))
    
        # write timestamp
        open(os.path.join(outDir, "schedule-ts.json"), "w").write(json.dumps(timestamp))

        # write checksum
        open(os.path.join(outDir, "schedule-cksum.json"), "w").write(json.dumps(data["checksum"]))

    else:
        print "NOT updating JSON files"
