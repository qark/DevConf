.PHONY: run all sync

all: mobileweb/schedule.json mobileweb/schedule-ts.json

mobileweb/schedule.json: data/schedule.csv tools/csv2json.py
	tools/csv2json.py data/schedule.csv mobileweb/

run :
	@cd mobileweb ; python -m SimpleHTTPServer

sync:
	rsync -av mobileweb/ lsmid@people.redhat.com:public_html/devconf
