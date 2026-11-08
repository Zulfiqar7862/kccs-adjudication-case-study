#!/usr/bin/env bash
# One-command runner. Works on macOS and Linux; Windows users run run.ps1.
#
#   ./run.sh                 set up and prove everything works (tests + demo, fictional data)
#   ./run.sh pack FILE.xlsx  run everything against the supplied workbook
#   ./run.sh explain EXC-ID  explain one alert in plain English (after `pack`)
#   ./run.sh explain EXC-ID --known-at 2026-01-01T00:00:00+00:00
#   ./run.sh serve           start the local API on http://127.0.0.1:8080
#   ./run.sh help
set -euo pipefail
cd "$(dirname "$0")"

PY=${PYTHON:-python3}
if [ ! -x .venv/bin/python ]; then
  echo "Creating a private Python environment in .venv ..."
  "$PY" -m venv .venv
fi
if ! .venv/bin/python -c "import sentinel" 2>/dev/null; then
  echo "Installing the prototype (no network services, no API keys) ..."
  .venv/bin/python -m pip install -q -r requirements.txt
fi
V=.venv/bin/python

case "${1:-check}" in
  check)
    $V scripts/check.py
    echo
    echo "Everything works. Next: ./run.sh pack /path/to/KCCS_Sentinel_Reference_Data_Pack.xlsx"
    ;;
  demo)
    $V -m sentinel demo
    ;;
  pack)
    PACK="${2:?usage: ./run.sh pack /path/to/pack.xlsx}"
    [ -f "$PACK" ] || { echo "No such file: $PACK"; exit 1; }
    mkdir -p artifacts/private prototype/output
    # One database per workbook snapshot (the service refuses to mix snapshots); remember the last one for `explain`.
    DB="prototype/output/pack-$($V -c "from sentinel.ingestion.workbook import sha256; print(sha256('$PACK')[:12])").db"
    echo "$DB" > prototype/output/last-pack.txt
    echo "1/5  Running all tests against the workbook ..."
    SENTINEL_WORKBOOK="$(cd "$(dirname "$PACK")" && pwd)/$(basename "$PACK")" $V -m unittest discover -s prototype/tests 2>&1 | tail -3
    echo "2/5  Inspecting the workbook (data-quality report) ..."
    $V scripts/inspect_workbook.py "$PACK" --output-dir artifacts/private >/dev/null
    echo "3/5  Importing one snapshot into $DB ..."
    $V -m sentinel --db "$DB" import "$PACK" | grep -E '"created"|"replayed"'
    echo "4/5  Choosing real example alerts and running the replays ..."
    $V scripts/select_demo_cases.py --db "$DB" --output-dir artifacts/private >/dev/null
    echo "5/5  Assessing every alert ..."
    $V -m sentinel --db "$DB" assess-all --compare-history --output artifacts/private/assessment-summary.json >/dev/null
    $V - <<'EOF'
import json
s = json.load(open("artifacts/private/assessment-summary.json"))
d = json.load(open("artifacts/private/demo-cases.json"))
print()
print(f"Assessed {s['total']} alerts. Decisions proposed by the software: 0 (it always abstains).")
for k, v in s["readiness"].items():
    print(f"  {k:<22} {v}")
print("Most common blocking problems:")
for k, v in list(s["conflict_kinds"].items())[:5]:
    print(f"  {v:>4}  {k}")
print()
print("Example alerts chosen automatically, one per failure type:")
for mode, c in d["cases"].items():
    print(f"  {c['event_id']:<12} {mode.replace('_', ' ')}")
print()
print("Reports: artifacts/private/workbook-inspection.md, artifacts/private/assessment-summary.json")
first = next(iter(d["cases"].values()))["event_id"]
print(f"Next: ./run.sh explain {first}")
EOF
    ;;
  explain)
    shift
    $V scripts/explain.py "$@"
    ;;
  serve)
    [ -f prototype/output/sentinel.db ] || { $V -m sentinel sample >/dev/null; $V -m sentinel import prototype/output/sample.xlsx >/dev/null; }
    [ -f prototype/output/local-credentials.json ] || $V -m sentinel credentials --tenant DEMO-ALPHA --tenant DEMO-BETA >/dev/null
    echo "Credentials are in prototype/output/local-credentials.json (local only). Try: $V scripts/api_example.py"
    $V -m sentinel serve
    ;;
  help|-h|--help)
    sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'
    ;;
  *)
    $V -m sentinel "$@"
    ;;
esac
