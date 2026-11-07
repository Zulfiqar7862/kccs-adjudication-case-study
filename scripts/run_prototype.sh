#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON="${PYTHON:-.venv/bin/python}"
WORKBOOK="${ADJUDICATION_WORKBOOK:-data/KCCS_Sentinel_Reference_Data_Pack.xlsx}"
OUTPUT="${ADJUDICATION_OUTPUT:-prototype/output}"
if [[ ! -f "$WORKBOOK" ]]; then
  printf 'Workbook absent. Place your authorised copy at %s, or use --fixtures via the CLI.\n' "$WORKBOOK" >&2
  exit 2
fi
"$PYTHON" -m adjudication.cli --workbook "$WORKBOOK" --out "$OUTPUT"
