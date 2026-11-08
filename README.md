# Sentinel adjudication case study

A runnable, evidence-first adjudication prototype and anonymized case-study submission. The critical component is a durable evidence/review/clock kernel—not a dashboard. It preserves human authority, keeps regulatory clocks independent of case disposition, and records reviewable evidence and audit history.

**Privacy:** public code, fictional fixtures and anonymized analysis only. The supplied workbook and brief, identifying records, generated private reports, databases and credentials are not committed. No ZIP is required.

## Evaluation copy

| Requested section | Read |
|---|---|
| Where we land | [Executive summary](docs/00-executive-summary.md), [recommendation and source mapping](docs/01-where-we-land.md), [open questions](docs/09-risks-assumptions-and-open-questions.md), [rollout](docs/10-future-roadmap.md) |
| The design | [Architecture](docs/02-system-architecture.md), [data model](docs/03-data-model.md), [lifecycle](docs/04-case-lifecycle.md), [degradation](docs/05-degradation-and-regulatory-clock.md), [versioning/deployment](docs/06-versioning-and-deployment.md), [diagrams](diagrams/README.md) |
| Working prototype | [Prototype guide](prototype/README.md), [validation](docs/08-validation-and-test-strategy.md), [API](docs/API.md) |
| Working log | [Decisions and lessons](docs/07-working-log.md), [AI-assisted review corrections](docs/11-ai-review-corrections.md) |

Source references let evaluators with the original pack trace decisions without publishing identifying records. Proposed production architecture is explicitly separate from implemented local behavior.

## Project structure

```text
README.md                 Setup and evaluation index
.env.example              Optional, non-secret shell settings
requirements.txt          Editable prototype install from repository root
Dockerfile                Non-root local demo image
docker-compose.yml        Isolated, read-only fictional demo
Makefile                  Development shortcuts
.github/workflows/        Cross-platform tests and security checks
data/                     Local private input guidance; workbook ignored
docs/                     Numbered case-study sections and API/security guides
diagrams/                 Mermaid architecture and lifecycle diagrams
scripts/                  Portable check command and example API client
prototype/
  README.md
  pyproject.toml          Installable package and lint configuration
  requirements.txt        Pinned runtime dependency
  run.ps1                 Windows setup/CLI launcher
  src/sentinel/
    cli.py                Pipeline entry point and commands
    config.py             Local output configuration
    ingestion/            XLSX parser and source hashing
    evidence/             Tenant-scoped candidates, temporal lookup, blockers
    workflow/             Durable cases, approvals, clocks and audit history
    api/                  Authenticated loopback JSON API
    fixtures/             Fictional workbook generator
    demo.py               Running-HTTP lifecycle demonstration
  tests/
    unit/
    integration/
  output/                 Ignored reports, databases and credentials
```

The layout follows the supplied reference without copying empty layers. Identity and temporal analysis stay with evidence; transactions, audit and reminders stay together in the workflow service because their invariants must commit atomically. No fake AI component or unused domain scaffolding is included.

## Clone and run locally

Requires Git and **Python 3.11+**. From the repository root:

```sh
git clone https://github.com/Zulfiqar7862/kccs-adjudication-case-study.git
cd kccs-adjudication-case-study
# Until PR #1 is merged, select the submitted branch:
git switch hoplite/naukratis-184532b3
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/check.py
python -m sentinel demo
```

On Windows, use `py -3 -m venv .venv` and `.venv\Scripts\Activate.ps1`, or run:

```powershell
./prototype/run.ps1 demo
```

The launcher creates the environment if needed, installs the package and forwards arguments to the CLI. It does not change execution policy. All commands use the repository root as the working directory. The package can also be installed directly with `python -m pip install -e ./prototype`.

`check.py` compiles the source, runs the tests and executes the real HTTP demo. The demo uses temporary fictional data and verifies evidence blockers, independent dual approval, reopening, preserved audit history and reminder retry. It checks workflow mechanics, not clinical correctness.

## Start the local API

```sh
python -m sentinel sample
python -m sentinel import prototype/output/sample.xlsx
python -m sentinel credentials --tenant DEMO-ALPHA --tenant DEMO-BETA
python -m sentinel serve
```

Open `http://127.0.0.1:8080/health`. From another activated terminal:

```sh
python scripts/api_example.py --tenant DEMO-ALPHA
```

This is a JSON API, not a dashboard. The server binds only to loopback; Ctrl-C stops it. Data persists in `prototype/output/sentinel.db`. Generated credentials are local development stubs and refuse accidental overwrite. Never commit them or expose this server publicly.

## Execute against the supplied workbook

Keep the authorized workbook outside the checkout or in ignored `data/`. Never force-add it.

```sh
python -m sentinel --db prototype/output/private.db import /absolute/path/to/your-workbook.xlsx
python -m sentinel --db prototype/output/private.db report --output prototype/output/private-report.json
SENTINEL_WORKBOOK=/absolute/path/to/your-workbook.xlsx python -m unittest discover -s prototype/tests -v
```

PowerShell equivalent for the integration test:

```powershell
$env:SENTINEL_WORKBOOK = 'C:\private\your-workbook.xlsx'
python -m unittest discover -s prototype/tests -v
Remove-Item Env:SENTINEL_WORKBOOK
```

The private test imports the supplied events, checks tenant boundaries, fail-closed evidence, audit integrity, historical visibility and exact replay. A configured invalid path fails; only an unset variable skips. Public CI uses fictional fixtures and never receives the private workbook. Historical dispositions are not clinical ground truth.

Exact-file replay creates no duplicate cases. A different snapshot requires a new database rather than silently overwriting history. Reports and exports can contain private data and must remain local.

## Configuration and Docker

`.env.example` documents optional variables; Python does **not** automatically load `.env` files. `SENTINEL_OUTPUT` changes the default database, generated sample and credential directory. Explicit CLI paths override those defaults. Existing local files in `artifacts/` are not moved or deleted; select an existing compatible database with `--db` and credentials with `serve --credentials`, or use a fresh output directory. `SENTINEL_WORKBOOK` is only an opt-in integration-test input, not an automatic import.

Docker is optional; the normal Python workflow needs no daemon:

```sh
docker compose run --build --rm prototype
```

The container runs the fictional demo as a non-root user with a read-only filesystem, temporary scratch storage, and no external network. Dependencies download during image build. It mounts no private data and publishes no API port. This is not a production deployment. The Docker build context excludes workbooks, credentials and generated outputs.

## Scope and limitations

Implemented: durable SQLite transactions, authenticated tenant-scoped HTTP operations, idempotency, version conflicts, evidence review, independent single/dual approvals, reopening, alert-derived obligations, explicit reminder retries, human-attested receipts, and audit export/verification.

Not implemented: live source connectors, clinically validated rules, verified document interpretation, SSO/qualified signatures, regulator delivery, supervised scheduling, legal calendars, distributed availability or immutable seven-year retention. The application never autonomously releases or destroys product, calls a model, or files with a regulator. Text-based signatory selection is a prototype heuristic. Audit hashes detect alteration relative to a trusted copy, not malicious rewriting by a database administrator.

See [security](docs/SECURITY.md), [contributing](docs/CONTRIBUTING.md) and [validation](docs/08-validation-and-test-strategy.md).
