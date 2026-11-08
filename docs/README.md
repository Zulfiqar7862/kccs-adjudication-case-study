# Start here: reviewer reading guide

This guide follows the four requested submission sections. Read in the order below; each step explains what to look for and what you should understand before moving on. No installation is required for the written review.

If you are not an engineer, read [the whole thing in plain English](PLAIN_ENGLISH.md) first.

The project is a **human-controlled evidence and case-workflow prototype**, not a production regulatory platform. Diagrams and captions distinguish implemented behavior from proposed production controls. Source attachments and identifying records are intentionally absent from this public repository.

## Step 1 — Where You Land

Read:

1. [Executive summary](00-executive-summary.md): the recommendation and prototype boundary.
2. [Where we land](01-where-we-land.md): requirements traceability (ID, source, acceptance criterion, phase), incident-to-control mapping, first customer and the tempting alternatives, deliberate exclusions, and the assessment of each board target (denominators, two clocks, median versus tail).
3. [Data findings and assumptions](12-data-findings-and-assumptions.md): what the workbook actually contains, verified incident references, the twelve reviewer questions, and the contradictions-and-assumptions register with owners.
4. [Risks and open questions](09-risks-assumptions-and-open-questions.md): board counterarguments and unresolved policy questions.
5. [Rollout](10-future-roadmap.md): the bounded pilot, expansion waves to 34 tenants, acceptance gates.

**Checkpoint:** you should be able to explain why evidence completeness and accountable human review take priority over an automated-closure quota, why "closed without reaching a person" must mean non-actionable closure and never a product disposition, and why day 90 is a gated decision rather than a guarantee.

## Step 2 — The Design

Read these documents in sequence:

| Order | Document | Question it answers |
|---|---|---|
| 1 | [Architecture](02-system-architecture.md) | What runs locally, what is proposed, and why do the component boundaries exist? |
| 2 | [Data model](03-data-model.md) | How are tenant scope, provenance, revisions and “as at” queries represented? |
| 3 | [Lifecycle](04-case-lifecycle.md) | How do evidence waiting, manual review, approvals and reopening work? |
| 4 | [Degradation and clocks](05-degradation-and-regulatory-clock.md) | What happens during outages, and why does the regulatory clock continue? |
| 5 | [Versioning and deployment](06-versioning-and-deployment.md) | How are changes qualified, promoted and rolled back without erasing history? |
| 6 | [Detailed design (LLD)](13-detailed-design-lld.md) | Entities and keys, valid versus recorded time, interface contracts, the transition tables, reliability, tenant controls, version matrix, diagrams. |
| 7 | [Cost and sizing](14-cost-and-sizing.md) | What the tab-13 ceiling buys, by route and provider; idle cost; separate retention sizing. |
| 8 | [Operations runbook](15-operations-runbook.md) | How failure is detected at 3 a.m. six months later, and who does what. |

Each document contains its relevant inline diagrams. The [diagram index](../diagrams/README.md) is an alternative visual entry point.

**Checkpoint:** distinguish the prototype's single-snapshot SQLite implementation from the proposed bitemporal, regional production system. Neither a successful internal reminder nor a human-entered receipt proves regulator delivery.

## Step 3 — Working Prototype

1. If you hold the supplied workbook, run the full suite against it first: `SENTINEL_WORKBOOK=/absolute/path/to/pack.xlsx python scripts/check.py`. This is the brief's "execution against the provided workbook"; the [verification record](08-validation-and-test-strategy.md#verification-record) lists the expected aggregates.
2. Follow the [step-by-step working guide](17-step-by-step-working.md): fifteen commands with captured output, then how the kernel processes one alert. Inspect `artifacts/private/demo-cases.json` for the knowledge-cutoff and correction replays.
3. Follow the [hands-on walkthrough](../prototype/WALKTHROUGH.md) to install and run the fictional HTTP lifecycle demo.
4. Read [validation and long-term reliability](08-validation-and-test-strategy.md) to separate current checks from proposed qualification gates, and the [operations runbook](15-operations-runbook.md).
5. Without the pack, inspect `artifacts/public/` (generated from the [anonymized workbook](../data/README.md); structure preserved, outcomes not equivalent) and use the [prototype module map](../prototype/README.md) and [API contract](API.md) for a code review.

**Checkpoint:** demonstrate an assessment that abstains with named conflicts, the same alert assessed with an earlier `known_at` yielding a different hash, a correction producing a new assessment while the original package still verifies, a cross-tenant request answered as not found, rejected premature signing, independent approval, preserved history after reopening, and reminder retry. Do not interpret these structural checks as clinical validation.

## Step 4 — Working Log

1. [Working log](07-working-log.md): alternatives, discarded approaches, wrong assumptions and how they were detected, verification history, and the session record for the assessment kernel.
2. [AI review and corrections](11-ai-review-corrections.md): AI-use disclosure and an observed factual correction.

**Checkpoint:** identify what was changed because an assumption failed, not merely what was built. The authored log does not substitute for the AI session export the brief asks the candidate to keep.

## Finish — reproduce and assess

- [Review walkthrough](16-review-walkthrough.md): the 20-minute script, deep-dive preparation, five hard questions, change-response examples, the submission email draft and the candidate's own pre-send tasks.
- [Submission checklist](../SUBMISSION_CHECKLIST.md): every evaluator expectation mapped to a file, test or artifact, with status.
