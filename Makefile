PYTHONVERSION=3.3
PYTHON_SITEPACKAGES=~/.local/lib/python${PYTHONVERSION}

LOCAL_BIN=~/.local/bin
LOCAL_SHARE=~/.local/share

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
	rm -rv ./{pake/,pake/config/,pake/node/,pake/node/local/,pake/node/aliens/,pake/repository/}__pycache__/

install-backend:
	make test
	make clean
	cp -Rv ./pake/ ${PYTHON_SITEPACKAGES}/site-packages/

install-ui:
	@echo "Copying JSON descriptions of interfaces..."
	@cp -v ./ui/*.json ${LOCAL_SHARE}/pake/ui/
	@echo ""
	@echo "Installing interface logic code..."
	@cp -v ./ui/node.py ${LOCAL_BIN}/pakenode && chmod +x ${LOCAL_BIN}/pakenode
	@cp -v ./ui/repo.py ${LOCAL_BIN}/pakerepo && chmod +x ${LOCAL_BIN}/pakepackage
	@cp -v ./ui/unified.py ${LOCAL_BIN}/pake && chmod +x ${LOCAL_BIN}/pake

uninstall-ui:
	@echo "Removing interface logic code..."
	@rm -v ${LOCAL_BIN}/pake*
	@echo ""
	@echo "Removing JSON descriptions of interfaces..."
	@rm -rv ${LOCAL_SHARE}/pake/ui/

install:
	make install-backend
	make install-ui
