.PHONY: setup test check demo sample import credentials serve lint
PYTHON ?= python3
VENV_PYTHON = .venv/bin/python
setup:
	$(PYTHON) -m venv .venv
	$(VENV_PYTHON) -m pip install -e .
test:
	$(VENV_PYTHON) -m unittest discover -s tests -v
check:
	$(VENV_PYTHON) scripts/check.py
demo:
	$(VENV_PYTHON) -m sentinel demo
sample:
	$(VENV_PYTHON) -m sentinel sample
import:
	$(VENV_PYTHON) -m sentinel import artifacts/sample.xlsx
credentials:
	$(VENV_PYTHON) -m sentinel credentials --tenant DEMO-ALPHA --tenant DEMO-BETA
serve:
	$(VENV_PYTHON) -m sentinel serve
lint:
	$(VENV_PYTHON) -m compileall -q src tests scripts
