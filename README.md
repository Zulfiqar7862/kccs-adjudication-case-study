# Sentinel adjudication case study

A working prototype and written submission for the Kestrel Cold Chain Solutions adjudication brief. Given one temperature-excursion alert, it assembles and checks the evidence a qualified person needs — in that customer's records only, as of the moment it happened, with what was known at the time — and says plainly what is missing or contradictory. It never decides the outcome; a named human does.

Candidate: Zulfiqar. Built with heavy AI assistance; see the [working log](docs/07-working-log.md).

## Three ways in

| If you are… | Start here | Time |
|---|---|---|
| **Anyone** — no code needed | [The whole thing in plain English](docs/PLAIN_ENGLISH.md) | 10 min |
| **Someone who wants to run it** | [Quick start](#quick-start) below, then [step-by-step working](docs/17-step-by-step-working.md) | 15 min |
| **An evaluator** following the four requested sections | [Reading guide](docs/README.md) and [submission checklist](SUBMISSION_CHECKLIST.md) | 2–3 h |

## Quick start

You need Git and Python 3.11 or newer. Nothing else: no accounts, no API keys, no network services.

```sh
git clone https://github.com/Zulfiqar7862/kccs-adjudication-case-study.git
cd kccs-adjudication-case-study
./run.sh                                             # Windows: .\run.ps1
```

That creates a private Python environment, installs the prototype, runs all 54 tests and a full lifecycle demo on fictional data, and ends with `All requested checks passed.`

With the supplied workbook (keep it outside the repository; it is never committed):

```sh
./run.sh pack /path/to/KCCS_Sentinel_Reference_Data_Pack.xlsx     # tests, inspection, import, examples, all 420 assessments
./run.sh explain EXC-110336                                        # one alert, in plain English
./run.sh explain EXC-110336 --known-at 2026-01-01T00:00:00+00:00   # the same alert, as it was known in January
```

`pack` ends with a short summary and the example alerts it chose. `explain` prints what was identified, which procedure and study apply, whether the readings can be trusted, the conflicts, what is missing, what a person must do next, the regulator clock, and the result — always **abstain**. Full reports land in `artifacts/private/` (ignored by git).

Other commands: `./run.sh serve` (local API on `127.0.0.1:8080`), `./run.sh demo`, `./run.sh help`. Every `./run.sh X` not listed is passed to `python -m sentinel X`; the full command reference is in [prototype/README.md](prototype/README.md).

## What you get

```
docs/PLAIN_ENGLISH.md            the problem, the solution and a glossary, no jargon
docs/17-step-by-step-working.md  every command with real output; how one alert is processed
docs/README.md                   evaluator reading guide (four sections, in order)
docs/00 … 16                     the submission: decision, design (HLD + LLD), data findings,
                                 cost, operations, validation, working log, review walkthrough
prototype/                       the code (src/sentinel) and 54 tests
scripts/                         check, inspect the workbook, choose examples, explain an alert
artifacts/public/                real outputs from the anonymized workbook (committed)
data/anonymized-evaluation.xlsx  a structure-preserving, anonymized copy for people without the pack
```

## What is implemented

- **Assessment kernel** (`prototype/src/sentinel/evidence/assessment.py`): for one alert — tenant-scoped entity resolution (product, facilities, carrier contract) that abstains on ambiguity and surfaces alias observations as *unverified*; SOP selection as at the excursion start with overlapping revisions reported as conflicts and date-only boundary days flagged; stability checks for ownership (by `tenant_code`, not file path), presentation, readability and relevance; telemetry flags for gateway gaps, interpolation, untagged BMS sources (quarantine for attribution) and firmware under a calibration bulletin, with no assumed correction; a notification obligation whose clock starts at alert receipt; a knowledge cutoff (`known_at`) that hides facts recorded later; correction overlays with recorded time that produce a **new** assessment while the original stays byte-identical; an execution manifest and SHA-256 content hashes; evidence packages that can be verified.
- **Workflow service** (`workflow/service.py`): atomic SQLite import of one workbook snapshot, case revisions, evidence review, independent single/dual signatures, optimistic versions, idempotency keys, reopening with preserved history, hash-chained audit export/verify, alert-derived obligations with a reminder outbox and human-attested receipts.
- **Interfaces**: CLI (`python -m sentinel`), loopback-only authenticated JSON API, Docker demo.
- **Reproducible data investigation**: `scripts/inspect_workbook.py` (data-quality report) and `scripts/select_demo_cases.py` (programmatic selection of real cases per failure mode, knowledge-cutoff replay, correction replay).
- **Tests**: 54 `unittest` tests — unit tests on fictional tables, integration tests on the anonymized workbook, and an opt-in integration test on the supplied pack.

## What is not implemented

No live source connectors, no document OCR or interpretation, no language model, no regulator filing or receipt verification, no calendars or business-day policies, no SSO or qualified signatures, no PostgreSQL/regional deployment, no WORM retention. The application never releases or destroys product and never files with a regulator. These are designed in [docs/02](docs/02-system-architecture.md)–[06](docs/06-versioning-and-deployment.md) and the [LLD](docs/13-detailed-design-lld.md) and are labelled *proposed* throughout.

## Manual commands (what `run.sh` does for you)

Python 3.11, 3.12 and 3.13 are exercised in CI on Linux, macOS and Windows. The only runtime dependency is `defusedxml`.

```sh
python3 -m venv .venv && source .venv/bin/activate       # Windows: py -3 -m venv .venv; .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/check.py                                   # compile, 54 tests, HTTP lifecycle demo on fictional data
python -m sentinel demo                                   # the lifecycle demo on its own
```

Expected: `Ran 54 tests … OK (skipped=2)`, a JSON lifecycle report ending with `"audit_integrity": "PASS"` and `"regulators_not_notified": true`, then `All requested checks passed.`

## Execute against the supplied workbook

Place the pack **outside** the checkout or in `data/` (ignored except for the anonymized copy). Never commit it.

```sh
export PACK=/absolute/path/to/KCCS_Sentinel_Reference_Data_Pack.xlsx
SENTINEL_WORKBOOK=$PACK python scripts/check.py                                   # all 54 tests, including the private pack test
python scripts/inspect_workbook.py $PACK --output-dir artifacts/private           # data-quality report
python -m sentinel --db prototype/output/private.db import $PACK                   # 420 cases, atomic, replay-safe
python scripts/select_demo_cases.py --db prototype/output/private.db --output-dir artifacts/private
python -m sentinel --db prototype/output/private.db assess-all --compare-history --output artifacts/private/assessment-summary.json
python -m sentinel --db prototype/output/private.db assess --tenant T-VIRENT --event EXC-110336 --output artifacts/private/EXC-110336.json
python -m sentinel --db prototype/output/private.db assess --tenant T-VIRENT --event EXC-110336 --known-at 2026-01-01T00:00:00+00:00
python -m sentinel --db prototype/output/private.db verify-assessment artifacts/private/EXC-110336.json
```

Expected outputs (observed on the supplied pack, 2026-11-08):

- `import` → `"created": 420`; a second import → `"replayed": true, "created": 0`.
- `select_demo_cases` → `artifacts/private/demo-cases.json` naming one real event per failure mode (blank product reference, firmware bulletin, SOP overlap, untagged BMS source, unreadable study, unverified alias hint, recorded notification window, study absent from index, presentation mismatch) plus a knowledge-cutoff replay and a correction replay with hashes.
- `assess-all` → 420 assessments, all `ABSTAIN`; 234 `BLOCKED_BY_CONFLICTS`, 186 `INCOMPLETE_EVIDENCE`; conflict kinds and 118 review candidates. This is structural coverage of a stratified pack, **not** an accuracy or automated-closure estimate.
- `assess … --known-at 2026-01-01` → the TT-CB-114 bulletin is reported `NOT_KNOWN_AT_CUTOFF` and the assessment hash differs from the current-knowledge one.
- `verify-assessment` → `{"valid": true}`.

`artifacts/private/` is ignored by git. The same commands run on the anonymized copy produce `artifacts/public/`, which is committed so reviewers without the pack can inspect real output shapes (firmware, readability, tenant constraints and incidents are redacted in that copy, so those failure modes do not appear there).

## Local API

```sh
python -m sentinel sample
python -m sentinel import prototype/output/sample.xlsx
python -m sentinel credentials --tenant DEMO-ALPHA --tenant DEMO-BETA
python -m sentinel serve                                  # http://127.0.0.1:8080, loopback only
python scripts/api_example.py --tenant DEMO-ALPHA         # in another shell
```

Contract: [docs/API.md](docs/API.md). Credentials are local development stubs; do not expose the server.

## Inspect outputs

| Output | Where | Contains |
|---|---|---|
| Data-quality report | `artifacts/<private|public>/workbook-inspection.{json,md}` | sheet/column profiles, overlaps, resolution counts, firmware, timestamps |
| Demo case packages | `artifacts/<private|public>/cases/<event>.json` | full assessment, section hashes, package hash |
| Replay index | `artifacts/<private|public>/demo-cases.json` | selected cases, knowledge-cutoff replay, correction replay |
| Coverage summary | `artifacts/<private|public>/assessment-summary.json` | readiness, conflict kinds, review candidates |
| Audit bundle | `python -m sentinel export --tenant … --case … --output …` then `verify` | hash-chained case history |

## Troubleshooting

- `ModuleNotFoundError: sentinel` → activate the venv and run `python -m pip install -r requirements.txt` from the repo root.
- `Error: Only one workbook snapshot is supported` → you imported a different file into the same database; use a new `--db` path.
- `Error: … already exists` from `credentials` → pass `--output` with a new path or delete the old file.
- `Error: … not found; run python -m sentinel credentials` from `serve` → generate credentials first.
- `Error: Event … is not available to tenant …` → the event belongs to another tenant or does not exist; both are reported identically by design.
- `SENTINEL_WORKBOOK` set to a wrong path → the private test fails rather than silently skipping; unset it to skip.
- Port 8080 busy → `python -m sentinel serve --port 8081` and adjust `scripts/api_example.py` accordingly.

## Limitations and known risks

The pack has no raw temperature series, no documents, no batch history, no recorded-time history and no calendars; the prototype models each as an explicit missing input and never synthesizes evidence. The workbook is treated as known at its extract date (2026-09-14) because no better recorded time exists. Entity resolution is exact-match only; alias observations are surfaced, never applied. The notification window is taken from the record as a *provisional* policy input. Hash chains are tamper-evidence, not WORM retention. The anonymized copy is structurally faithful but not outcome-equivalent. Full register: [risks and open questions](docs/09-risks-assumptions-and-open-questions.md).

## Configuration and container

Configuration lives in `.env.example` (Python does not auto-load it). `docker compose run --build --rm prototype` runs the fictional demo in an isolated container.
