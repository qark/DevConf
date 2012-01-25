.PHONY: run all sync sync-people mobileweb/schedule.json

all: mobileweb/schedule.json mobileweb/schedule-ts.json

mobileweb/schedule.json: tools/schedule2json.py
	tools/schedule2json.py mobileweb/

run :
	@cd mobileweb ; python -m SimpleHTTPServer

sync-people:
	rsync -av mobileweb/ lsmid@people.redhat.com:public_html/devconf

sync:
	rsync -av mobileweb/ root@ospace.cz:/var/www/m.devconf.cz

