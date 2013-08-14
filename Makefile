PYTHONVERSION=3.3
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
	rm -rv ./{pake/,pake/config/,pake/ui/,}__pycache__/

ui:
	python3 pakenode-ui.py
	cp pakenode-ui.py pakenode
	chmod +x pakenode
	python3 pakerepo-ui.py
	cp pakerepo-ui.py pakerepo
	chmod +x pakerepo
	python3 pakemanager-ui.py
	cp pakemanager-ui.py pakemanager
	chmod +x pakemanager

local-install:
	make test
	cp -Rv ./pake/ ~/.local/lib/python${PYTHONVERSION}/site-packages/
	make ui
	mv ./pakenode ${LOCAL_BIN}/pakenode
	mv ./pakerepo ${LOCAL_BIN}/pakerepo
	mv ./pakemanager ${LOCAL_BIN}/pakemanager
	make clean

install:
	./install.sh
