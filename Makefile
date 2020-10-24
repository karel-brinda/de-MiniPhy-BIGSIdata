.PHONY: all help clean cleanall pypi install test edit

SHELL=/usr/bin/env bash -eo pipefail
PIP=/usr/bin/env pip
PYTHON=/usr/bin/env python3

.SECONDARY:

.SUFFIXES:

all:

install: ## Install ProPhyle using PIP
	$(PIP) uninstall -y mof || true
	$(PIP) install .


pypi: ## Upload ProPhyle to PyPI
	$(MAKE) clean
	$(PYTHON) setup.py sdist bdist_wheel upload

help: ## Print help message
	@echo "$$(grep -hE '^\S+:.*##' $(MAKEFILE_LIST) | sed -e 's/:.*##\s*/:/' -e 's/^\(.\+\):\(.*\)/\\x1b[36m\1\\x1b[m:\2/' | column -c2 -t -s : | sort)"

clean: ## Clean
	$(PYTHON) setup.py clean --all

cleanall: clean ## Clean all

test:
	$(MAKE) -C tests

edit:
	nvim mof/mof.py
