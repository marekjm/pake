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
	rm -rv ./{pake/,pake/config/,pake/node/}__pycache__/

local-install:
	make test
	make clean
	cp -Rv ./pake/ ~/.local/lib/python${PYTHONVERSION}/site-packages/

install:
	./install.sh
