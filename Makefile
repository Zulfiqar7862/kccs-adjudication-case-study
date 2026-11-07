PYTHON ?= python3
VENV ?= .venv
PY := $(VENV)/bin/python
RUFF := $(VENV)/bin/ruff
export PYTHONPATH := $(CURDIR)/prototype/src
.PHONY: setup test test-unit test-integration run e2e lint docker-build docker-run
setup:
	PYTHON=$(PYTHON) VENV=$(VENV) bash scripts/setup_local_env.sh
test:
	$(PY) -m pytest --cov=adjudication --cov-branch --cov-report=term-missing --cov-report=json:.local-evidence/coverage.json --cov-fail-under=90
test-unit:
	$(PY) -m pytest prototype/tests/unit --cov=adjudication --cov-branch --cov-report=term-missing --cov-fail-under=90
test-integration:
	$(PY) -m pytest prototype/tests/integration
run:
	PYTHON=$(PY) bash scripts/run_prototype.sh
e2e:
	$(PY) -m pytest prototype/tests/unit/test_rules.py -k fixture_cli_reproducibility
	$(PY) -m pytest prototype/tests/integration/test_workbook_pipeline.py
lint:
	$(RUFF) check prototype scripts
	$(RUFF) format --check prototype scripts
docker-build:
	docker build -t kccs-adjudication:local .
docker-run:
	docker compose run --rm prototype
