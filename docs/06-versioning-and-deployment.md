# 6. Versioning and deployment

## 2.6 Interfaces and deployment



Production contracts (not HTTP endpoints implemented in the CLI):

```text
POST /v1/alerts              Idempotency-Key + source envelope → 202 only after durable receipt
POST /v1/cases/{id}/compile  expected_version, valid_at, knowledge_cutoff → dossier + manifest
GET  /v1/cases/{id}/basis?decision_id=... → immutable authorised export job
POST /v1/cases/{id}/tasks/{task}/complete → evidence version, expected_version
POST /v1/cases/{id}/sign     frozen_decision_hash, authority_version, reauth → signature record
POST /v1/cases/{id}/reopen   reason, affected_manifest, expected_version → new episode
POST /v1/obligations/{id}/receipt receipt hash, verified channel → CONFIRMED after verification
```

Return 409 for version conflict, 422 for invalid/missing facts, 403 for scope/authority mismatch, 503 for non-durable intake. A compile result can succeed while returning `NEEDS_EVIDENCE`; missing evidence is a domain result, not a hidden exception. Include request/correlation IDs, tenant-scoped redacted audit logs and immutable actor attribution. Page/row evidence IDs are resolved server-side; an arbitrary client URL cannot cause document exfiltration or SSRF. Export jobs are encrypted, short-lived and auditable; expiry does not delete the seven-year original.



Version the public API with additive changes within v1 and new major versions for breaking contracts; event envelopes carry schema version and consumers handle unknown fields. Database migrations are expand/backfill/dual-read/contract with rollback-compatible releases; no destructive migration in the same release as a behaviour change. Rule packages are immutable base + declarative tenant overlays, with a rule trace listing each predicate and source fact. Reference corrections create new recorded-time versions. Model prompts, weights/provider IDs and decoding/tokenizer configs are pinned. Retirement dates generate qualification work at least a quarter ahead where notice permits; keep a qualified no-model fallback. The June incident shows why an unqualified replacement is not a rollback.

Pipeline: PR → lint/type/dependency/secret scan → unit/property/data-contract/golden/isolation suite → deterministic pack replay + candidate-vs-baseline difference artefact → QA review of every clinically material disagreement and random unchanged cases → signed qualification manifest → immutable container digest/SBOM → regional staging replay → shadow one tenant → canary one cohort → monitored promotion. Behavioural changes require the quality lead's gate every time, including document-rule corrections, retrieval changes and translated templates. Infrastructure-only changes still get regression/security validation. No production model change is promoted just because its output mix resembles the old one.

Metrics by tenant/cohort/rule version: evidence-gap rate; incorrect entity merges; false closures from independent audit; unsafe/missing citations; retrieved foreign-tenant count (must be zero); evidence-ready-to-sign latency; queue age/occupancy failures; deadline slack distribution, overdue count and receipt failures; source freshness/watermark lag; model retirement notice; cost/case and cost/day at zero traffic. INC-2411 changed destroy share from 11% to 19%: alert on conditional outcome-mix drift with sample sizes, but also inspect semantic disagreement. A normal-looking ratio is not proof of safety.


## Repository implementation

The CLI emits engine, policy, API, no-model selection, source fingerprint and output hashes in `run_manifest.json`. Runtime dependencies are pinned; CI installs declared development tools. CI has no private data or model credentials. The Docker image uses an explicit COPY allowlist, a non-root user and synthetic fixtures by default; compose mounts local workbook read-only with network disabled. Production IaC is deliberately not supplied as if qualification had happened. See [deployment pipeline](../diagrams/deployment-pipeline.md).
