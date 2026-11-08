# Start here: reviewer reading guide

This guide follows the four requested submission sections. Read in the order below; each step explains what to look for and what you should understand before moving on. No installation is required for the written review.

The project is a **human-controlled evidence and case-workflow prototype**, not a production regulatory platform. Diagrams and captions distinguish implemented behavior from proposed production controls. Source attachments and identifying records are intentionally absent from this public repository.

## Step 1 — Where You Land

Read:

1. [Executive summary](00-executive-summary.md): the recommendation and prototype boundary.
2. [Where we land](01-where-we-land.md): requirements mapped to brief/pack references, the critical component, deliberate exclusions and the anonymized first-customer choice.
3. [Risks and open questions](09-risks-assumptions-and-open-questions.md): board counterarguments, assumptions and unresolved policy questions.
4. [Rollout](10-future-roadmap.md): the bounded pilot, timeline rationale and acceptance gates.

**Checkpoint:** you should be able to explain why evidence completeness and accountable human review take priority over an automated-closure quota, and why day 90 is a gated decision rather than a guarantee.

## Step 2 — The Design

Read these documents in sequence:

| Order | Document | Question it answers |
|---|---|---|
| 1 | [Architecture](02-system-architecture.md) | What runs locally, what is proposed, and why do the component boundaries exist? |
| 2 | [Data model](03-data-model.md) | How are tenant scope, provenance, revisions and “as at” queries represented? |
| 3 | [Lifecycle](04-case-lifecycle.md) | How do evidence waiting, manual review, approvals and reopening work? |
| 4 | [Degradation and clocks](05-degradation-and-regulatory-clock.md) | What happens during outages, and why does the regulatory clock continue? |
| 5 | [Versioning and deployment](06-versioning-and-deployment.md) | How are changes qualified, promoted and rolled back without erasing history? |

Each document contains its relevant inline diagrams. The [diagram index](../diagrams/README.md) is an alternative visual entry point.

**Checkpoint:** distinguish the prototype's single-snapshot SQLite implementation from the proposed bitemporal, regional production system. Neither a successful internal reminder nor a human-entered receipt proves regulator delivery.

## Step 3 — Working Prototype

1. If you hold the supplied workbook, run the full suite against it first: `SENTINEL_WORKBOOK=/absolute/path/to/pack.xlsx python scripts/check.py`. This is the brief's "execution against the provided workbook"; the [verification record](08-validation-and-test-strategy.md#verification-record--2026-11-08) lists the expected aggregates.
2. Follow the [hands-on walkthrough](../prototype/WALKTHROUGH.md) to install and run the fictional HTTP lifecycle demo.
3. Read [validation and long-term reliability](08-validation-and-test-strategy.md) to separate current checks from proposed qualification gates.
4. Inspect and run the [bundled anonymized evaluation workbook](../data/README.md). It preserves structure, not clinical outcomes. The workbook must be provided locally; public CI uses fictional fixtures and the reviewed anonymized workbook.
5. For a code review, use the walkthrough's source-reading order, the [prototype module map](../prototype/README.md) and the [API contract](API.md).

**Checkpoint:** demonstrate rejected premature signing, evidence review, independent approval, preserved history after reopening, and reminder retry. Do not interpret these structural checks as clinical validation.

## Step 4 — Working Log

1. [Working log](07-working-log.md): alternatives, discarded approaches, observed implementation mistakes, corrections and verification history.
2. [AI review and corrections](11-ai-review-corrections.md): AI-use disclosure and an observed factual correction.

**Checkpoint:** identify what was changed because an assumption failed, not merely what was built. Complete original AI sessions are not included; the authored log does not substitute for that separate submission item.

## Finish — reproduce and assess

- Can you run the demo and explain its expected rejection as well as its successful transitions?
- Can you trace a recommendation back to the brief or workbook without needing private records in GitHub?
- Are implemented features, stubs and future production work clearly separated?
- Have you reviewed the known limitations and the outstanding AI-session archive item?

Return to the [repository overview](../README.md), or begin the [hands-on walkthrough](../prototype/WALKTHROUGH.md).
