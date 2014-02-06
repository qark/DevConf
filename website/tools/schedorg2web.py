#!/usr/bin/python
import codecs
import hashlib
import jinja2
import json
import os
import sys
import time
import urllib
import urllib2

SCHEDORG_URL = "http://developerconference2014.sched.org/api/"
SCHEDORG_RONLY_API_KEY = "d0cfd220bb1bd8ed848b718def0a35f8"
OFFLINE_MODE = False

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
        #print 80 * "-"
        #print "IN:", record
        #print "DATE:", date
        #print "ROOMS:", rooms
        output = dict()
        output["type"] = "talk"
        output["date"] = record["event_start"][:10]
        output["start"] = record["event_start"][-8:-3]
        output["end"] = record["event_end"][-8:-3]
        output["room"] = record.get("venue", "N/A")
        output["speaker"] = record.get("speakers", "N/A")
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
        #print
        #print "OUT:", output
        result.append(output)
    # sort schedule by timestamp (primary key) and room name (secondary key)
    result.sort(key = lambda a: a["room"])
    result.sort(key = lambda a: a["timestamp"])
    return dict(items = result, timestamp = timestamp, checksum = hash.hexdigest())

def getVenue(d):
    return d.get("venue", "N/A")

def getStartTime(d):
    return d["start_time_ts"]

def schedule2html(schedule, users, cordova = False, directory = "mobileweb"):
    # download users's avatars
    for user in users:
        if user["avatar"] and not OFFLINE_MODE:
            print "Downloading", user["avatar"]
            try:
                f = urllib2.urlopen(user["avatar"])
                data = f.read()
                t = f.info()["Content-Type"]
            except urllib2.HTTPError:
                data = open("templates/avatar.gif").read()
                ext = "gif"
            if t == "image/jpeg":
                ext = "jpg"
            elif t == "image/png":
                ext = "png"
            elif t == "image/gif":
                ext = "gif"
            else:
                raise ValueError("Unknown content type %s" % t)
        else:
            data = open("templates/avatar.gif").read()
            ext = "gif"
        open("%s/avatars/%s.%s" % (directory, user["username"], ext), "w").write(data)
        user["avatar"] = "avatars/%s.%s" % (user["username"], ext)
    # transform users
    result = dict()
    for user in users:
        result[user["username"]] = user
    users = result
    # sort schedule
    schedule.sort(key = getVenue)
    schedule.sort(key = getStartTime)
    # generate web
    env = jinja2.Environment(loader = jinja2.FileSystemLoader("templates"))
    render(env, "index.html", "%s/index.html" % directory, schedule = schedule, users = users, cordova = cordova)
    render(env, "about.html", "%s/about.html" % directory, cordova = cordova)
    render(env, "schedule.html", "%s/schedule20140207.html" % directory, schedule = schedule, users = users, date = "2014-02-07", cordova = cordova)
    render(env, "schedule.html", "%s/schedule20140208.html" % directory, schedule = schedule, users = users, date = "2014-02-08", cordova = cordova)
    render(env, "schedule.html", "%s/schedule20140209.html" % directory, schedule = schedule, users = users, date = "2014-02-09", cordova = cordova)

def render(env, template, filename, **kwargs):
     template = env.get_template(template)
     f = codecs.open(filename, "w", encoding = "utf-8")
     f.write(template.render(**kwargs))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print >>sys.stderr, "Expected: DIRNAME CORDOVA"
        sys.exit(1)
    outDir = sys.argv[1]
    cordova = sys.argv[2] == "CORDOVA"
    
    if not OFFLINE_MODE:
        print "Getting schedule from sched.org"
        data = urllib.urlencode({
            "api_key": SCHEDORG_RONLY_API_KEY,
            "format": "json",
        })
        schedule = urllib2.urlopen(SCHEDORG_URL + "session/list", data).read()
        open("schedule.data", "w").write(schedule)
        scheduleFull = urllib2.urlopen(SCHEDORG_URL + "session/export", data).read()
        open("schedulefull.data", "w").write(scheduleFull)
    else:
        schedule = open("schedule.data", "r").read()
        scheduleFull = open("schedulefull.data", "r").read()

    if not OFFLINE_MODE:
        print "Getting users from sched.org"
        data = urllib.urlencode({
            "api_key": SCHEDORG_RONLY_API_KEY,
            "format": "json",
            "fields": "username,name,avatar"
        })
        users = urllib2.urlopen(SCHEDORG_URL + "user/list", data).read()
        open("users.data", "w").write(users)
    else:
        users = open("users.data", "r").read()
    users = json.loads(users)
    
    print "Generating data/web"

    # convert schedule to json
    timestamp = int(time.time())
    result = schedule2json(schedule, timestamp)
    # add user list
    result["users"] = users

    # generate json files (for old mobile application)
    try:
        old = json.load(open(os.path.join(outDir, "schedule.json"), "r"))
    except IOError:
        old = dict(checksum = None)
    
    if old["checksum"] != result["checksum"] or True:
        print "Updading JSON files"
        # update schedule and timestamp
        open(os.path.join(outDir, "schedule.json"), "w").write(json.dumps(result))
    
        # write timestamp
        open(os.path.join(outDir, "schedule-ts.json"), "w").write(json.dumps(timestamp))

        # write checksum
        open(os.path.join(outDir, "schedule-cksum.json"), "w").write(json.dumps(result["checksum"]))

    else:
        print "NOT updating JSON files"

    # format schedule into static page
    schedule2html(json.loads(scheduleFull), users, directory = outDir, cordova = cordova)

    print "DONE"
