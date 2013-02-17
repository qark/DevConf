.PHONY: run all sync sync-people mobileweb/schedule.json mobileweb/schedule.xml

all: mobileweb/schedule.json mobileweb/schedule-ts.json mobileweb/schedule.xml

mobileweb/schedule.json: tools/schedorg2json.py
	tools/schedorg2json.py mobileweb/
	tools/schedorg2json.py dashboard/

#mobileweb/schedule.xml:
#	tools/devconf_schedule.py mobileweb/schedule.json > mobileweb/schedule.xml
	
run-dashboard :
	@cd dashboard ; python -m SimpleHTTPServer

run-mobileweb :
	@cd mobileweb ; python -m SimpleHTTPServer

sync:
	rsync -av --delete dashboard/ lsmid@people.redhat.com:public_html/devconf/dashboard
	rsync -av --delete mobileweb/ lsmid@people.redhat.com:public_html/devconf/mobileweb
	rsync -av --delete mobileweb/ root@ospace.cz:/var/www/m.devconf.cz/


