# Working prototype

The installable `sentinel` package implements the critical evidence/lifecycle/clock core. This is the working component, not a collection of architectural placeholders.

**First visit?** Follow the [step-by-step walkthrough](WALKTHROUGH.md) for installation, expected output, API exploration and optional private-workbook validation. For the written submission, start with the [reading guide](../docs/README.md).

From the **repository root**:

```sh
python -m pip install -e ./prototype
python scripts/check.py
python -m sentinel demo
```

On Windows, `./prototype/run.ps1 demo` creates the environment, installs and runs the same command. The tests use Python's built-in `unittest`, so no pytest configuration or dependency is needed.

## Boundaries

- `ingestion/workbook.py`: hardened XLSX parsing, source row provenance and digest.
- `evidence/analysis.py`: tenant/identity matching, temporal candidates and fail-closed blockers used at import; not clinical decisions.
- `evidence/assessment.py`: the assessment kernel. Turns one imported alert into a tenant-scoped, temporally explicit evidence assessment with entity resolution that abstains on ambiguity, SOP/stability/telemetry checks, a knowledge cutoff (`known_at`), correction overlays with recorded time, an execution manifest and content hashes; packages and verifies it.
- `workflow/service.py`: SQLite transaction boundary for case revisions, reviews, independent signatures, audit events, obligations and reminder outbox.
- `api/http.py`: authenticated loopback requests, input limits and domain-error responses.
- `cli.py`, `config.py`: local administrative commands and explicit output settings.
- `fixtures/sample.py`, `demo.py`: deterministic fictional input and real HTTP demonstration.
- `tests/unit/`: parsing/candidate/assessment/configuration checks; `tests/integration/`: persistence, concurrency, CLI, HTTP, lifecycle, public workbook assessment and opt-in private workbook.

The service remains cohesive so changes to case state, audit history and idempotency commit together. Splitting those into independent storage services would weaken the critical invariant without helping this prototype.

## Authorized workbook

```sh
python -m sentinel --db prototype/output/private.db import /absolute/path/to/workbook.xlsx
SENTINEL_WORKBOOK=/absolute/path/to/workbook.xlsx python -m unittest discover -s prototype/tests -v
```

All supplied records are exercised by the private integration test; public CI runs fictional fixtures and the reviewed anonymized evaluation workbook. Keep the workbook and generated reports private. `output/` is ignored except for its directory marker. Default paths are relative to the invocation directory; use repository-root commands or explicit absolute paths.

## More commands

```sh
python -m sentinel --help
python -m sentinel --db prototype/output/private.db report
python -m sentinel --db prototype/output/private.db assess --tenant T-CODE --event EXC-ID --output artifacts/private/EXC-ID.json
python -m sentinel --db prototype/output/private.db assess --tenant T-CODE --event EXC-ID --known-at 2026-01-01T00:00:00+00:00
python -m sentinel --db prototype/output/private.db verify-assessment artifacts/private/EXC-ID.json
python -m sentinel --db prototype/output/private.db assess-all --compare-history --output artifacts/private/assessment-summary.json
python -m sentinel tick --help
```

`--db` is a global option and goes before the subcommand. `assess` requires the principal's tenant; an event belonging to another tenant is reported as not found, the same answer as a missing event. `--corrections` accepts a JSON list of overlays (`recorded_at`, `sheet`, `row`, `field`, `value`); overlays recorded after `--known-at` are ignored, and the original assessment is never modified.

Notification statuses are part of `report`; use `tick --tenant TENANT` for the internal reminder stub. Neither operation contacts a regulator. Use `export --tenant TENANT --case CASE --output PATH` and `verify PATH` for audit bundles. See the [API contract](../docs/API.md) and [root guide](../README.md) for the complete workflow and limitations.
