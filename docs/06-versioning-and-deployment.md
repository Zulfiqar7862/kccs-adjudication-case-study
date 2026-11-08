# Versioning and deployment

## Qualification, deployment and rollback

Version code, schema, adapter mapping, governed aliases, approved rule/policy/calendar bundles, OCR/parser, optional retrieval index, embedding/model/provider and prompt independently. A case pins the complete release manifest. Do not let “latest” modify signed history or active adjudication without an explicit reevaluation event.

Pipeline: review → secret/dependency/static checks → unit/API/tenant-isolation/concurrency tests → all-workbook structural replay → QA-curated retrospective clinical benchmark with independently verified evidence → migration/backup/restore and disaster/alert-storm rehearsal → QA/security approval → shadow deployment for one tenant/site → controlled canary → signed tenant promotion. The production cohort must include language, handwritten-annex, wrong-presentation, missing-source, dual-signature, storm, late-data and correction cases. Freeze acceptance thresholds and false-closure cost before evaluating. The public and opt-in private tests are the first stage, not a substitute for qualification.

Use expand/backfill/contract database migrations with compatible readers; record schema versions and validate backfill counts/hashes. Stop promotion on evidence drift, tenant leakage, unknown deadline, increased false-safe closures or budget violations. Roll back code/config to a qualified manifest; never erase audit/case events. If a new version already generated decisions, identify affected packets and open controlled review rather than pretending rollback undid their legal consequences.

To meet the board's retrospective-review condition, before go-live and every change, record each benchmark case's historical outcome, the candidate system's closure or advisory result, every disagreement and its evidence-based explanation. Have accountable QA adjudicate disagreements against independently verified evidence rather than treating past decisions as ground truth. Report false-safe closures separately from disagreement rates. The current prototype supplies evidence candidates and workflow checks, not an autonomous disposition; its structural workbook replay does not satisfy this clinical qualification gate.

Optional AI comes later and may draft only cited summaries, never invent a missing stability limit or bypass a signer. Enforce tenant provider/residency permission before retrieval or inference, tenant-exclusive derived indexes where required, source-level citations, structured output validation and adversarial document-instruction tests. Budget each tenant/case before calls, cache only authorized artifacts, track quiet-period cost, and reject unqualified fallback. Vendor deprecation notice starts a qualification plan; expired qualification disables that feature while the non-model workflow continues.

## Current implementation boundary

The production pipeline and controls in this proposal are not implemented. The local prototype is run and checked using the commands in [Contributing](CONTRIBUTING.md) and [validation](08-validation-and-test-strategy.md). An optional Docker Compose path runs the isolated fictional demo and is tested in hosted CI; it is not a production deployment capability.
