PYTHONVERSION=3.3
LOCAL_BIN=~/.local/bin

.PHONY: doc test manual clean ui

doc:
	make clean
	pydoc3 ./pake/* > DOC

manual:
	sed -i -e s/${OLD}/${VERSION}/ manual/*.markdown
	#pandoc -o ./manual/manual.pdf ./manual/*.markdown

test:
	python3 -m unittest --catch --failfast --verbose tests.py

clean:
	rm -rv ./{pake/,pake/config/,pake/node/}__pycache__/

install-local-backend:
	make test
	make clean
	cp -Rv ./pake/ ~/.local/lib/python${PYTHONVERSION}/site-packages/

install-local-ui:
	@echo "Copying JSON descriptions of interfaces..."
	@cp -v ./ui/*.json ~/.local/share/pake/ui/
	@echo ""
	@echo "Installing interface logic code..."
	@cp -v ./ui/node.py ${LOCAL_BIN}/pakenode && chmod +x ${LOCAL_BIN}/pakenode
	@cp -v ./ui/repo.py ${LOCAL_BIN}/pakerepo && chmod +x ${LOCAL_BIN}/pakepackage
	@cp -v ./ui/unified.py ${LOCAL_BIN}/pake && chmod +x ${LOCAL_BIN}/pake

uninstall-local-ui:
	@echo "Removing interface logic code..."
	@rm -v ${LOCAL_BIN}/pake*
	@echo ""
	@echo "Removing JSON descriptions of interfaces..."
	@rm -rv ~/.local/share/pake/ui/

install-local:
	make install-local-backend
	make install-local-ui
