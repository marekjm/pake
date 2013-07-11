VERSION = 0.0.2-alpha.2
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
	rm -rv ./{pake/,}__pycache__/

ui:
	python3 pakenode-ui.py
	cp ./pakenode-ui.py ./pakenode
	chmod +x ./pakenode

local-ui-install:
	make ui
	cp ./pakenode ${LOCAL_BIN}/pakenode

install:
	./install.sh
