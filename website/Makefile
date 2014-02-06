.PHONY: all sync mobileweb/index.html

all: mobileweb/index.html

mobileweb/index.html: tools/schedorg2web.py
	tools/schedorg2web.py mobileweb/ WEB
	cp mobileweb/schedule*.json dashboard/

cordova: tools/schedorg2web.py
	tools/schedorg2web.py ../assets/www/ CORDOVA

run-dashboard :
	@cd dashboard ; python -m SimpleHTTPServer

run-mobileweb :
	@cd mobileweb ; python -m SimpleHTTPServer

sync:
	rsync -av --delete dashboard/ lsmid@people.redhat.com:public_html/devconf/dashboard
	rsync -av --delete mobileweb/ lsmid@people.redhat.com:public_html/devconf/mobileweb
	rsync -av --delete mobileweb/ root@ospace.cz:/var/www/m.devconf.cz/
