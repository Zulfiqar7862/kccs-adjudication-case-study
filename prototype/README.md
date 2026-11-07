# Working prototype

This is a local deterministic evidence kernel with explicit module boundaries, not a deployed clinical adjudicator. `ingestion` reads/validates all workbook sheets; `identity` returns tenant-scoped candidates; `temporal` owns fixed-hour replay and a two-axis SQLite reference store; `evidence` surfaces gaps; `rules` composes the dossier; `recommendations` provides guarded no-model task lists; `workflow` demonstrates waits/reopens; `audit` verifies a local hash chain; `reporting` writes five deterministic files.

From the repository root: `make setup`, `make test`, then supply the private workbook and `make run`. For public fixtures:

```bash
.venv/bin/python -m adjudication.cli --fixtures prototype/tests/fixtures --out prototype/output
```

From this directory, `../.venv/bin/python -m pytest` uses its own pytest configuration. Runtime dependencies are listed by the forwarding requirements file; install the package from the root for the console entry point. Never commit real output files. The assistant and document dependencies explicitly return unavailable/fallback, not invented source facts.
