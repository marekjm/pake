VERSION = 0.0.5
OLD=0.0.2-alpha.2

LOCAL_BIN=~/.local/bin

.PHONY: doc test manual clean ui

doc:
	make clean
	pydoc3 ./pake/* > DOC
	echo '\n\n\n' >> DOC
	pydoc3 ./pakenode-ui.py >> DOC

manual:
	sed -i -e s/${OLD}/${VERSION}/ manual/*.markdown
	#pandoc -o ./manual/manual.pdf ./manual/*.markdown

test:
	python3 -m unittest --catch --failfast --verbose tests.py

clean:
	rm -rv ./{pake/,pake/config/,}__pycache__/

ui:
	python3 pakenode-ui.py
	cp pakenode-ui.py pakenode
	chmod +x pakenode
	python3 pakerepo-ui.py
	cp pakerepo-ui.py pakerepo
	chmod +x pakerepo
	python3 pake-ui.py
	cp pake-ui.py pakeui
	chmod +x pakeui

local-ui-install:
	make ui
	mv ./pakenode ${LOCAL_BIN}/pakenode
	mv ./pakerepo ${LOCAL_BIN}/pakerepo
	mv ./pakeui ${LOCAL_BIN}/pake

install:
	./install.sh
