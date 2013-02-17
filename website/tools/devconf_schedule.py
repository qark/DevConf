#!/usr/bin/python3
import argparse
import csv
import datetime
import io
import json
import logging
import re
import sys
import urllib.request
import xml.etree.ElementTree as et
logging.basicConfig(format='%(levelname)s:%(funcName)s:%(message)s',
    level=logging.INFO)

Track_RE = re.compile("[\[\]]")
DeTitle_RE = re.compile("[ /:?]")


class Persons(dict):
    def __init__(self):
        self._pers_counter = self._pers_counter_gen()

    def _pers_counter_gen(self):
        static_counter = 2000
        while True:
            static_counter += 1
            yield static_counter

    def parse_title(self, in_title):
        split_title = in_title.strip().split('-', 2)
        speakers = [speaker.strip()
            for speaker in split_title[0].split(',')]
        logging.debug("speakers = %s", str(speakers))
        logging.debug("split_title = %s", str(split_title))
        if len(split_title) > 1:
            title = split_title[1].strip()
            for person in speakers:
                if person not in self:
                    counter = next(self._pers_counter)
                    self[person] = counter
        else:
            title = ", ".join(speakers)
            speakers = []
        return title, speakers

    def parse_speakers(self, title, speak_str):
        speakers = [speaker.strip()
            for speaker in speak_str.split(',')]
        if len(speakers) > 0:
            for person in speakers:
                if person not in self:
                    counter = next(self._pers_counter)
                    self[person] = counter
        else:
            title = ", ".join(speakers)
            speakers = []
        return title, speakers


class Schedule_data(dict):
    _compute_date_dict = {
        'Friday': '2012-02-17',
        'Saturday': '2012-02-18'
    }

    def __init__(self, fname):
        self.fn = fname
        self.pers = Persons()
        self._parse()

    def _parse(self):
        if self.fn.startswith("http"):
            with io.TextIOWrapper(urllib.request.urlopen(self.fn)) as inf:
                self._parse_json(inf)
        elif self.fn.endswith(".json"):
            with open(self.fn) as inf:
                self._parse_json(inf)
        else:
            with open(self.fn) as inf:
                self._parse_csv(inf)

    def _fix_time_format(self, time_str):
        if len(time_str) == 4:
            time_str = "0" + time_str
        return time_str

    def _parse_json(self, inf):
        json_data = json.load(inf)
        for item in json_data['items']:
            logging.debug("item = %s", item)
            day = item['date']
            from_time = self._fix_time_format(item['start'])
            to_time = self._fix_time_format(item['end'])
            if day not in self:
                self[day] = {}
            title = item['topic']
            track = item.get('tags', "")
            speakers_str = item.get('speaker', '')
            place = item['room']
            if place not in self[day]:
                self[day][place] = {}
            title, speakers = self.pers.parse_speakers(title,
                speakers_str)
            self[day][place][from_time, to_time] = \
                title, speakers, track.strip()

    def _parse_csv(self, inf):
        tab_reader = csv.DictReader(inf, dialect="excel-tab")
        for line in tab_reader:
            day = self._compute_date_dict[line['day']]
            from_time, to_time = [self._fix_time_format(time)
                for time in line['hour'].split('-')]
            if day not in self:
                self[day] = {}
            self[day][from_time, to_time] = {}
            del line['hour']
            del line['day']
            for place in line:
                line_split = Track_RE.split(line[place])
                if line_split and len(line_split) > 1:
                    title, track = line_split[:2]
                if place not in self[day]:
                    self[day][place] = {}
                title, speakers = self.pers.parse_title(title)
                self[day][place][from_time, to_time] = \
                    title, speakers, track.strip()


class Pentabarf_schedule():
    def __init__(self, data):
        self.day_idx = 0
        self.event_idx = 3000
        #self.schedule = et.Element("schedule")
        self.schedule = et.XML("""<schedule>
        <conference>
            <title>Developer Conference</title>
            <subtitle/>
            <venue>Faculty of Informatics at Masaryk University</venue>
            <city>Brno</city>
            <start>2012-02-17</start>
            <end>2012-02-18</end>
            <days>2</days>
            <release>0.2</release>
            <day_change>04:00</day_change>
            <timeslot_duration>00:15</timeslot_duration>
        </conference>
    </schedule>""")
        self.sch_data = data

    def _tag_from_title(self, title):
        out = title.split("-")[-1].strip().lower()
        out = DeTitle_RE.sub('_', out).split("_", 6)[:-1]
        out = "_".join(out)
        out = out.replace("__", "_")
        return out

    def _xml_indent(self, elem, level=0):
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            for e in elem:
                self._xml_indent(e, level + 1)
            if not e.tail or not e.tail.strip():
                e.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def __str__(self):
        self._xml_indent(self.schedule)
        return et.tostring(self.schedule, encoding="unicode")

    def generate_schedule(self):
        for day in self.sch_data:
            self.day_idx += 1
            logging.debug("self.day_idx = %s, day = %s", self.day_idx, day)
            day_elem = et.SubElement(self.schedule, "day",
                attrib={'index': str(self.day_idx),
                    'date': day})
            logging.debug("sch_data[day] = %s", self.sch_data[day])
            for place in self.sch_data[day]:
                if not self.sch_data[day][place]:
                    continue
                logging.debug("sch_data[day][place] = %s",
                    self.sch_data[day][place])
                term_elem = et.SubElement(day_elem, "room",
                    attrib={'name': place})
                for from_t, to_t in self.sch_data[day][place]:
                    title, speakers, track = \
                        self.sch_data[day][place][from_t, to_t]
                    logging.debug("from_t, to_t, title, track " \
                        + "= %s - %s: %s // %s",
                        from_t, to_t, title, track)
                    self.event_idx += 1
                    event_elem = et.SubElement(term_elem, "event",
                        attrib={'id': str(self.event_idx)})
                    et.SubElement(event_elem, "start").text = from_t
                    from_time = datetime.datetime.strptime(from_t.strip(),
                        "%H:%M")
                    to_time = datetime.datetime.strptime(to_t.strip(),
                        "%H:%M")
                    duration = to_time - from_time
                    duration_str = "0" + str(duration).replace(":00", "")
                    et.SubElement(event_elem, "duration").text = duration_str
                    et.SubElement(event_elem, "tag").text = \
                        self._tag_from_title(title)
                    et.SubElement(event_elem, "title").text = title
                    et.SubElement(event_elem, "track").text = track
                    et.SubElement(event_elem, "language").text = "en"
                    et.SubElement(event_elem, "type").text = "lecture"
                    if len(speakers) > 0:
                        persons_elem = et.SubElement(event_elem, "persons")
                        for pers in speakers:
                            et.SubElement(persons_elem, "person",
                                attrib={'id': \
                                    str(self.sch_data.pers[pers])}).text = pers


if __name__ == "__main__":
    desc = "Generate Pentabarf compatible schedule from devconf sources."
    sourcename_help = "Either filename (CSV or JSON) or " \
        + "(only JSON) URL of the source."
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("sourcename", nargs="?",
            help=sourcename_help)
    options = parser.parse_args(sys.argv[1:])

    data = Schedule_data(options.sourcename)
    sched = Pentabarf_schedule(data)
    sched.generate_schedule()
    print(sched)
