VERSION = 0.0.2-alpha.2
OLD=0.0.2-alpha.2

.PHONY: doc test manual clean

doc:
	make clean
	pydoc3 ./pake/* > DOC
	echo '\n\n\n' >> DOC
	pydoc3 ./pakenode-ui.py >> DOC

manual:
	sed -i -e s/${OLD}/${VERSION}/ manual/*.markdown
	#pandoc -o ./manual/manual.pdf ./manual/*.mdown

test:
	python3 -m unittest --catch --failfast --verbose tests.py

clean:
	rm -rv ./{pake/,}__pycache__/

install:
	./install.sh
