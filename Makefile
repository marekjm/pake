PYTHONVERSION=3.3
PYTHON_SITEPACKAGES=~/.local/lib/python${PYTHONVERSION}

BINDIR=~/.local/bin
SHAREDIR=~/.local/share

.PHONY: doc test manual clean ui


doc:
	make clean
	pydoc3 ./pake/* > DOC

manual:
	sed -i -e s/${OLD}/${VERSION}/ manual/*.markdown
	#pandoc -o ./manual/manual.pdf ./manual/*.markdown

test: tests.py
	python3 -m unittest --catch --failfast --verbose tests.py

clean:
	@rm -rv ./{pake/,pake/config/,pake/node/,pake/aliens/,pake/nest/,pake/packages/,pake/transactions/}__pycache__/

install-backend:
	make test
	make clean
	cp -Rv ./pake/ ${PYTHON_SITEPACKAGES}/site-packages/

install-ui:
	@cp -v ./ui/*.json ${SHAREDIR}/pake/ui/
	@cp -v ./ui/node.py ${BINDIR}/pakenode && chmod +x ${BINDIR}/pakenode
	@cp -v ./ui/nest.py ${BINDIR}/pakenest && chmod +x ${BINDIR}/pakenest
	@cp -v ./ui/unified.py ${BINDIR}/pake && chmod +x ${BINDIR}/pake

install-env-descriptions:
	@cp -Rv ./env/ ${SHAREDIR}/pake

install:
	make install-backend
	make install-ui
	make install-env-descriptions
