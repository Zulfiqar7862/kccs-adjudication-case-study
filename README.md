# KCCS adjudication case study

**Zulfiqar Ali Ahmed — Senior AI/backend engineering take-home**

A deterministic, tenant-scoped **evidence-eligibility and bitemporal reference-resolution kernel**. It makes unsafe reference selection and missing evidence explicit instead of inventing a pharmaceutical disposition. The production HLD/LLD includes an independent regulatory clock, human signing, retained historical basis, regional isolation and qualified deployment.

## Fresh-clone quickstart

Requires Python 3.11+ and GNU Make. On Debian/Ubuntu install `python3-venv` and `make` if absent. No model account, cloud credential or API key is needed.

```bash
git clone https://github.com/Zulfiqar7862/kccs-adjudication-case-study.git
cd kccs-adjudication-case-study
make setup
make test
```

The public clone contains **no private workbook**. Tests pass on hand-made synthetic fixtures; four private-workbook integration tests skip cleanly.

Then copy your own authorised workbook into `data/`:

```bash
cp /path/to/KCCS_Sentinel_Reference_Data_Pack.xlsx data/
make test
make run
make e2e
```

`make run` reads all workbook sheets without modifying them. It writes five **gitignored, local-only** files into `prototype/output/`: `adjudication_report.json`, `adjudication_summary.csv`, `case_audit_log.csv`, `evidence_gaps.csv`, and `run_manifest.json`. The manifest pins code/rules/no-model selection and input/output fingerprints. No regulator notification or email is sent.

Manual virtual-environment equivalent:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pip install --no-deps -e .
.venv/bin/python -m pytest
```

To run without private data:

```bash
.venv/bin/python -m adjudication.cli \
  --fixtures prototype/tests/fixtures --out prototype/output
```

## Measured aggregate results

| Check | Captured local result |
|---|---|
| Full suite with workbook | **49 passed**, **99.19%** combined statement/branch coverage |
| Entire suite with workbook physically absent | **45 passed, 4 skipped**, **95.30%** combined coverage |
| Workbook replay | **15 sheets, 420 events**, immutable input |
| Product references | 297 exact-source matches; 72 unverified alias candidates; 51 missing |
| Notification replay | 14 late; 14 within fixed historical window; 392 flagged not reportable in extract |
| Evidence result | All 420 need more evidence; zero proposed auto-closures or signed dispositions |
| Reproducibility | All five generated files byte-identical across clean reruns |

These are selected-pack counts, **not** population rates or clinical accuracy. The clock replays supplied flags and hours; it does not qualify jurisdictional calendars or independently decide reportability. Exact source equality is not canonical presentation approval.

Local Ruff, Bandit, runtime dependency audit and Gitleaks checks are described in [validation](docs/08-validation-and-test-strategy.md). The initial public commit passed all three hosted workflows: CI (Python 3.11/3.13), Security and Prototype fixtures. A fresh clone independently passed the quickstart above; pinned run links are in the validation document. Docker is not installed on the build box: image/compose configuration is provided but was not executed there.

## Commands

`make setup`, `make test`, `make test-unit`, `make test-integration`, `make run`, `make e2e`, `make lint`, `make docker-build`, `make docker-run`.

Docker build defaults to synthetic fixtures. Compose expects your local workbook, mounts it read-only, writes only local outputs and disables networking. Inspect your host's volume permissions before use. No source workbook is copied into the image.

## Design and working record

- [Executive summary](docs/00-executive-summary.md)
- [Where we land: requirements, sources, exclusions and rollout](docs/01-where-we-land.md)
- [System architecture / HLD](docs/02-system-architecture.md)
- [Data model / temporal LLD](docs/03-data-model.md)
- [Case lifecycle](docs/04-case-lifecycle.md)
- [Degradation and regulatory clock](docs/05-degradation-and-regulatory-clock.md)
- [Versioning and deployment](docs/06-versioning-and-deployment.md)
- [Honest working log](docs/07-working-log.md)
- [Validation and measured evidence](docs/08-validation-and-test-strategy.md)
- [Risks, complete sheet inventory and open questions](docs/09-risks-assumptions-and-open-questions.md)
- [Future roadmap](docs/10-future-roadmap.md)
- [Five Mermaid diagrams](diagrams/architecture.md), [prototype boundaries](prototype/README.md), [infrastructure contract](infrastructure/README.md)

## Confidentiality and scope

Fresh git history contains authored code, paraphrased analysis and synthetic fixtures only. Do not commit the source brief, private workbook, private PDF, customer-derived output, contacts, compensation details or credentials. `.gitignore` excludes those local artefacts; this is not a substitute for reviewing staged changes. The MIT license covers authored work, not rights to the supplied private dataset.

Only the local kernel, reference/audit stores and small in-memory workflow are implemented. Production adapters, durable scheduling, authority/e-signature validation, legal calendars, regulator filing, multiwriter exposure accounting and HA/DR remain qualified future work. An audit hash chain is not administrator-proof WORM, and a basis-hash guard is not a regulated signature.

Optional private report: install `Markdown` and `weasyprint` plus OS Pango libraries, then run `python scripts/generate_diagrams.py --report /path/outside/repo/REPORT.pdf`. Add `--renderer /path/to/mmdc` (Mermaid CLI) and `--puppeteer-config /path/to/config.json` for rendered SVG/PNG figures. Generated diagram files stay in `.local-evidence/`; PDF should remain outside public history. No submission archive is created.
