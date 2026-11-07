#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
VENV="${VENV:-.venv}"
"${PYTHON:-python3}" -m venv "$VENV"
"$VENV/bin/python" -m pip install --upgrade pip
"$VENV/bin/python" -m pip install -r requirements-dev.txt
"$VENV/bin/python" -m pip install --no-deps -e .
mkdir -p .local-evidence prototype/output
printf 'Ready. Run make test without private data, then add your workbook to data/ and run make run.\n'
