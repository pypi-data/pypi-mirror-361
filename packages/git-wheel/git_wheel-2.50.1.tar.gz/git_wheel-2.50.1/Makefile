.PHONY: install
ifeq ($(OS),Windows_NT)
  EXE=.exe
endif
version=$(project_version).windows.1

git-$(version)/git$(EXE): git-$(version)/config.h
	$(MAKE) -j$(shell nproc) -C git-$(version) NO_REGEX=YesPlease NO_GETTEXT=YesPlease prefix=

install: git-$(version)/git$(EXE) scripts/chomp.sh
	DESTDIR=$(prefix) $(MAKE) -j$(shell nproc) -C git-$(version) NO_REGEX=YesPlease NO_GETTEXT=YesPlease prefix= install
	scripts/chomp.sh $(prefix)/libexec/git-core
	rm -rf $<

git-$(version)/config.h: v$(version).tar.gz
	tar xzf $<

v$(version).tar.gz:
	curl -LO https://github.com/git-for-windows/git/archive/refs/tags/$@
