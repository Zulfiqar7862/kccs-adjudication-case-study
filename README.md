# Sentinel adjudication

A structured, runnable **local evidence and adjudication workflow** with a JSON API, durable SQLite cases, human review/approval gates, independent notification clocks, and verifiable audit exports.

**Public code and anonymized case-study documentation.** The included demo data is fictional. No confidential brief, source workbook, source-derived reports or real customer identifiers are included. The application never autonomously releases or destroys product, never calls a model, and never files with a regulator.

## 1. Clone and run

Requires **Python 3.11 or newer** and Git. No Docker, database service, model account, or API key is needed. Installation adds one small runtime dependency, `defusedxml`, for safe XML parsing; setuptools is the build backend.

```sh
git clone https://github.com/Zulfiqar7862/kccs-adjudication-case-study.git
cd kccs-adjudication-case-study
python3 -m venv .venv
```

Activate the environment:

```sh
# macOS / Linux
source .venv/bin/activate

# Windows PowerShell (run this instead)
.venv\Scripts\Activate.ps1
```

On Windows, use `py -3` instead of `python3` to create the environment. If activation is restricted, invoke `.venv\Scripts\python.exe` directly in the commands below.

```sh
python -m pip install -e .
python scripts/check.py
python -m sentinel demo
```

`check.py` compiles the source, runs the automated suite and runs the real HTTP end-to-end demo. It exits nonzero on failure. Private-workbook tests explicitly skip unless you opt in; public functionality does not require a private file. `demo` creates a temporary fictional workbook/database, starts a loopback server, exercises the lifecycle and stops it. It prints `"result": "PASS"` after verifying:

1. A premature disposition is rejected.
2. Six kinds of fictional source evidence are recorded.
3. A reviewer explicitly resolves all blockers.
4. Two independent approvers must agree before the dual-policy case is disposed.
5. Reopening preserves the earlier signed revision and starts a fresh review.
6. Audit hashes verify; failed internal reminders retry without fabricating regulatory receipts.

The demo checks workflow mechanics—not clinical validity. Missing real evidence always remains a blocker until an authorized human records and attests its resolution.

## 2. Start the API for local development

```sh
python -m sentinel sample
python -m sentinel import artifacts/sample.xlsx
python -m sentinel credentials --tenant DEMO-ALPHA --tenant DEMO-BETA
python -m sentinel serve
```

Open `http://127.0.0.1:8080/health` or, from another activated terminal, run:

```sh
python scripts/api_example.py --tenant DEMO-ALPHA
```

The API is JSON-only; there is no dashboard. The server deliberately binds only to loopback. Ctrl-C stops it. Data persists in `artifacts/sentinel.db`; restarting does not clear cases. The credential command creates random, private local tokens and refuses to overwrite an existing file. Do not commit or share that file. Static identities are a **development stub**, not production SSO or qualified electronic signatures.

To choose another database, put the option before the command:

```sh
python -m sentinel --db artifacts/another.db import artifacts/sample.xlsx
python -m sentinel --db artifacts/another.db serve --port 8081
```

An exact workbook replay is idempotent. A different second workbook is rejected: use a new database for a different snapshot. Multi-snapshot reconciliation is deliberately outside this version rather than silently overwriting history.

## 3. Work with your authorized private workbook

Keep it outside this public repository, or in the ignored `data/` directory. The expected sheet/column contract is in [the API and data guide](docs/API.md). The importer reads XLSX directly with standard-library ZIP handling and hardened XML parsing, including shared strings, inline strings, sparse cells and workbook relationships.

```sh
python -m sentinel --db artifacts/private.db import /absolute/path/to/your-workbook.xlsx
python -m sentinel --db artifacts/private.db report --output artifacts/private-report.json
```

Opt into private integration tests:

```sh
# macOS / Linux
SENTINEL_WORKBOOK=/absolute/path/to/your-workbook.xlsx python -m unittest discover -s tests -v
```

```powershell
# Windows PowerShell
$env:SENTINEL_WORKBOOK = 'C:\private\your-workbook.xlsx'
python -m unittest discover -s tests -v
Remove-Item Env:SENTINEL_WORKBOOK
```

An unset variable produces explicit skips. A configured missing/invalid file fails, rather than silently skipping. The private checks replay the supplied events and test tenant separation, fail-closed evidence and audit integrity; historical dispositions are **not** clinical ground truth. The full report and export may contain private source-derived data: keep them local. Public CI does not receive this environment variable or workbook.

## 4. Project structure

```text
src/sentinel/
  workbook.py       XLSX reader and source hashes
  evidence.py       Tenant-scoped candidates, temporal lookup and blockers
  service.py        Transactional cases, approvals, clocks, outbox and audit
  http.py           Authenticated loopback JSON API
  sample.py         Deterministic, wholly fictional workbook generator
  demo.py           Running-HTTP lifecycle walkthrough
  __main__.py       CLI / installed `sentinel` command
scripts/
  check.py          Portable local and CI acceptance command
  api_example.py    Example authenticated API client
tests/             Unit, workflow, HTTP, CLI and opt-in private checks
docs/              API, architecture, development, testing and security guides
data/              Instructions only; private inputs are ignored
.github/workflows/  Cross-platform checks and security scanning
```

This replaces the previous `prototype/` layout with one installable package and one test entry point. Docker, Terraform and Kubernetes scaffolding are not included: this local implementation does not need them, and unverified production scaffolding would imply capabilities it does not provide.

## 5. Common commands

| Command | Purpose |
|---|---|
| `python scripts/check.py` | Compile, test and run the HTTP demo |
| `python -m unittest discover -s tests -v` | Run all tests; private integration is opt-in |
| `python -m sentinel demo` | Isolated end-to-end fictional walkthrough |
| `python -m sentinel sample` | Write ignored `artifacts/sample.xlsx` |
| `python -m sentinel report` | Print aggregate state/blocker/clock summary |
| `python -m sentinel report --output artifacts/report.json` | Write full local report, including case packets |
| `python -m sentinel tick --tenant DEMO-BETA --fail` | Inject an internal reminder outage |
| `python -m sentinel tick --tenant DEMO-BETA` | Retry pending internal reminders; no regulator calls |
| `python -m sentinel export --tenant TENANT --case CASE --output artifacts/audit.json` | Export an authorized local case and all revisions |
| `python -m sentinel verify artifacts/audit.json` | Verify manifest, audit chain and artifact hashes |

The CLI has trusted administrative access to its local database. Tenant access controls apply at the authenticated HTTP boundary. Consult [API](docs/API.md), [architecture](docs/ARCHITECTURE.md), [contributing](docs/CONTRIBUTING.md), [testing](docs/TESTING.md), and [security](docs/SECURITY.md).

## Case-study submission — four requested sections

1. **Where we land:** [recommendation](docs/RECOMMENDATION.md), with requirements mapped to source sections/rows, exclusions, a phased pilot, assumptions and board-level counterarguments.
2. **The design:** [implemented architecture](docs/ARCHITECTURE.md), [production HLD/LLD](docs/PRODUCTION_DESIGN.md), and [API/data contract](docs/API.md). Diagrams cover component and state boundaries; the production design covers bitemporal data, failure handling and deployment qualification.
3. **Working prototype:** this package implements the durable evidence/lifecycle/clock core. Public CI uses fictional fixtures; the explicit private-workbook integration path above executes against the authorized supplied workbook. Missing source systems remain documented stubs, not fabricated successful integrations.
4. **Working log:** [development decisions, mistakes and discarded approaches](docs/WORKING_LOG.md).

The written submission is anonymized. Source section/sheet/row references let an evaluator with the original pack trace decisions; original source files, customer-identifying details and case-level outputs are not published. Public and private verification claims are kept separate in [testing](docs/TESTING.md).

## Supported boundary

**Implemented:** real HTTP requests, durable transactions, exact import replay, tenant-scoped reads/mutations, optimistic concurrency, idempotency, evidence review, independent single/dual approvals, reopening, independent alert-based deadlines, explicit reminder retries, human-attested filing receipts, local audit export/verification, synthetic and authorized-workbook execution.

**Not implemented:** live source-system connectors, validated clinical rules, authoritative document interpretation, named-signatory licensing/SSO, qualified signatures, regulator delivery, continuously supervised deadline scheduling, legal holiday calendars, distributed availability or seven-year immutable retention. No “production-ready” or “everything integrated” claim is made. Those require external systems, approvals and evidence that are not in this repository.

Audit hashes detect accidental alteration relative to a trusted copy; they do not stop an administrator from rewriting data and recomputing hashes. An internal reminder is never treated as a regulator receipt. Case disposition and notification clocks remain independent, including during outages and reopening.
