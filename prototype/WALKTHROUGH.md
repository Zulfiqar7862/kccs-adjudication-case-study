# Step-by-step prototype walkthrough

[Repository overview](../README.md) · [Four-section reading guide](../docs/README.md) · [Prototype reference](README.md)

Start with the fictional demo. It requires no private workbook, external service, model API key or Docker daemon. All commands below run from the **repository root**. This is a CLI and JSON API, not a browser dashboard.

## Step 1 — Get the project and install it

You need Git and Python 3.11 or newer. If you already cloned the repository, open its root directory instead of cloning again.

```sh
git clone https://github.com/Zulfiqar7862/kccs-adjudication-case-study.git
cd kccs-adjudication-case-study
```

**macOS / Linux:**

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**Windows PowerShell:**

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

On Windows, replace `python` in subsequent commands with `.\.venv\Scripts\python.exe`. This avoids changing PowerShell execution policy or requiring environment activation.

**Check:** `python -m sentinel --help` lists commands including `demo`, `import`, `report`, `serve`, `export` and `verify`.

## Step 2 — Run the automated checks

```sh
python scripts/check.py
```

**Expect:** compilation succeeds, the tests finish with `OK`, and the HTTP demo finishes successfully. With no `SENTINEL_WORKBOOK` configured, the private-workbook test is explicitly skipped. The current suite discovers 27 tests: 26 pass and one is skipped in the public-only run. The final line says `All requested checks passed`.

A configured but invalid workbook path is an error, not an expected skip. Test counts may change as coverage grows; failed checks must be investigated rather than ignored.

## Step 3 — Watch the complete workflow

```sh
python -m sentinel demo
```

The demo generates fictional input, starts an actual loopback HTTP server on a temporary port, exercises the workflow, and shuts down. Its temporary database is removed automatically; it does not modify your persistent local database.

Read `http_lifecycle` in the JSON output in order:

| Stage | Expected result | Why it matters |
|---|---|---|
| Attempt to sign immediately | HTTP `409` | Missing evidence blocks premature disposition; this rejection is intentional. |
| Add six evidence categories | HTTP `200`, still `WAITING_EVIDENCE` | Recorded stubs do not themselves authorize a decision. |
| Resolve blockers in review | `READY_FOR_REVIEW` | Review is a distinct human action. |
| First approval for the dual-signature tenant | Still `READY_FOR_REVIEW` | One approver cannot bypass the required quorum. |
| Second independent approval | `DISPOSED` | The required approvals bind the reviewed packet. |
| Reopen for late evidence | `WAITING_EVIDENCE` | A new revision preserves the prior signed history. |

Also expect `result: "PASS"`, `audit_integrity: "PASS"`, `prior_revision_preserved: true`, `reminder_failure_and_retry: "PASS"` and `regulators_not_notified: true`.

**Interpretation:** the demo verifies workflow mechanics using explicitly fictional source stubs. It neither validates clinical evidence nor files with a regulator.

## Step 4 — Explore a persistent local case database (optional)

The previous step is enough to demonstrate the complete workflow. Use this step if you want to inspect a server yourself. The commands use a dedicated `walkthrough` directory so they do not overwrite the default database or credentials. If you have used that directory before with different data, select a new directory consistently in every command; do not delete a database containing records you need.

```sh
python -m sentinel sample --output prototype/output/walkthrough/sample.xlsx
python -m sentinel --db prototype/output/walkthrough/cases.db import prototype/output/walkthrough/sample.xlsx
python -m sentinel --db prototype/output/walkthrough/cases.db report --output prototype/output/walkthrough/report.json
python -m sentinel credentials --tenant DEMO-ALPHA --tenant DEMO-BETA --output prototype/output/walkthrough/credentials.json
python -m sentinel --db prototype/output/walkthrough/cases.db serve --credentials prototype/output/walkthrough/credentials.json
```

**Expect:** sample generation, import and report succeed; the server remains running on `127.0.0.1:8080`. Credential creation intentionally refuses to overwrite an existing file. When revisiting the same walkthrough, reuse the credentials by skipping that creation command.

In a **second terminal**, return to the repository root and activate the environment as in Step 1 (or use the Windows interpreter path). Then run:

```sh
python scripts/api_example.py --tenant DEMO-ALPHA --credentials prototype/output/walkthrough/credentials.json
```

**Expect:** a JSON list of cases scoped to the selected tenant. The client reads the bearer credential locally without displaying it. You can also open `http://127.0.0.1:8080/health` for the JSON health response; there is no dashboard. Stop the server with **Ctrl+C** when finished. The local database and report remain in the ignored walkthrough directory.

For mutation payloads and role requirements, read the [API contract](../docs/API.md); Step 3 already exercises those actions automatically.

## Step 5 — Validate the supplied workbook (authorized reviewers only)

This is separate from the fictional demo. Obtain the supplied workbook through the private evaluation channel; it is intentionally not downloadable from this public repository. Replace the example path with its actual local path.

```sh
python -m sentinel --db prototype/output/reviewer-private.db import "/absolute/path/to/workbook.xlsx"
python -m sentinel --db prototype/output/reviewer-private.db report --output prototype/output/reviewer-private-report.json
```

Then run the integration checks with the input configured:

**macOS / Linux:**

```sh
SENTINEL_WORKBOOK="/absolute/path/to/workbook.xlsx" python scripts/check.py
```

**Windows PowerShell:**

```powershell
$env:SENTINEL_WORKBOOK = 'C:\path\to\workbook.xlsx'
.\.venv\Scripts\python.exe scripts/check.py
Remove-Item Env:SENTINEL_WORKBOOK
```

**Expect:** all 27 current tests pass, including the configured-workbook integration test. Import preserves evidence blockers rather than making implicit dispositions. Exact-file replay does not duplicate cases; a different snapshot requires a new database. Keep the workbook, database, credentials and generated report private. Never attach these outputs to a public issue or PR.

## Step 6 — Read the implementation in execution order

| Order | Source | What to follow |
|---|---|---|
| 1 | [CLI](src/sentinel/cli.py) | Command parsing and explicit input/output paths |
| 2 | [Workbook ingestion](src/sentinel/ingestion/workbook.py) | Safe XML parsing, source rows and snapshot digest |
| 3 | [Evidence analysis](src/sentinel/evidence/analysis.py) | Tenant matching, temporal candidates and fail-closed blockers |
| 4 | [Workflow service](src/sentinel/workflow/service.py) | Atomic state, review, signatures, audit, obligations and retry behavior |
| 5 | [HTTP adapter](src/sentinel/api/http.py) | Authentication, role enforcement and error responses |
| 6 | [Demo](src/sentinel/demo.py) and [tests](tests/) | The executable examples and regression evidence |

Finish with the [validation strategy](../docs/08-validation-and-test-strategy.md) and [working log](../docs/07-working-log.md). Production qualification, live connectors, verified regulator delivery and immutable long-term retention are proposed work, not capabilities proved by this walkthrough.

## Troubleshooting

| Symptom | What to check |
|---|---|
| `No module named sentinel` | Use the installed environment's Python and repeat Step 1 from the repository root. |
| Workbook path not found | Use an existing absolute path; quote paths containing spaces. |
| Different snapshot rejected | Choose a fresh database path; do not overwrite historical records. |
| Credentials file already exists | Reuse it and skip creation, or select a fresh walkthrough directory. |
| Port 8080 already in use | Stop your earlier local server before Step 4. The example client uses port 8080. |
| HTTP `401` / `403` | Use the matching local credential file and permitted role; do not disable authentication. |
| Browser shows JSON rather than a page | Expected: this prototype exposes a JSON API, not a dashboard. |

[Back to the four-section reading guide](../docs/README.md) · [Repository overview](../README.md)
