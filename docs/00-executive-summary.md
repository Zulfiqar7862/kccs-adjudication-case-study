# Executive summary

Sentinel is an evidence-first case workflow prototype. It assembles tenant-scoped evidence candidates and blockers for accountable human review; it does not adjudicate, recommend a disposition, or validate source documents. The recommendation is to proceed only toward a bounded, human-controlled EU pilot with explicit readiness gates—not to treat a 90-day milestone as production approval.

## What exists today

The local Python/SQLite implementation imports a single XLSX snapshot, analyzes evidence indexes, manages case revisions and review/signatures, enforces optimistic versions and idempotency, exports/verifies hash-chained audit history, and tracks notification obligations with an internal reminder/outbox stub. It includes a CLI and loopback-only HTTP adapter. Exact-file replay is safe; a different workbook snapshot is rejected. Public examples use synthetic data; private workbook checks are opt-in.

## What is proposed, not implemented

Regional production cells, production identity/TLS, source and filing integrations, a PostgreSQL ledger, immutable object retention, full bitemporal evidence, independently operated deadline processing, qualified signatures, verified receipts, multi-snapshot reconciliation, and disaster recovery all require separate implementation and qualification. A recorded receipt is a human attestation; a reminder is not an external filing. Hash chaining is not WORM retention, legal non-repudiation, or proof of factual correctness.

## Decision and next step

Keep disposition with an authorized human. Define the pilot boundary, source ownership, residency, policies, signatories, clocks, baselines, retention, and stop rules before any live records. Run shadow comparisons and reconcile exceptions before a QA/security/governance/operations go/no-go. Expand tenant by tenant only after independent review. See [where we land](01-where-we-land.md), [rollout](10-future-roadmap.md), and [open risks](09-risks-assumptions-and-open-questions.md).

## Evidence and verification limits

The source pack's volumes, rates, and modeled costs are inputs, not validated forecasts, population estimates, or outcome labels. The written submission preserves anonymized references to brief sections and workbook sheets/rows; source files and identifying values are not reproduced. Existing test results are described in the [validation strategy](08-validation-and-test-strategy.md); they validate workflow mechanics, not clinical correctness or production readiness.

## Implemented prototype boundary


The supported implementation is a local prototype: SQLite, static locally generated bearer identities, and loopback HTTP. It does not include production identity management, TLS termination, external notification or filing integrations, verified receipt ingestion, durable distributed storage, or validated document interpretation. Deploying it outside its intended local environment requires those controls to be designed and implemented separately; the prototype is not a substitute for them.

Sentinel is a local, evidence-first case workflow prototype. It analyzes imported indexes and records workflow actions; it does not make an adjudication or independently validate source documents.
