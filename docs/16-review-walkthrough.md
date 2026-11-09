# Review walkthrough, deep-dive preparation and change response

Speaker notes for the 90-minute conversation (brief §9: 20 minutes of walkthrough, two deep dives chosen by the reviewers, then an unseen change). Every claim below points at a file, a test or a command. Real-data commands need the supplied workbook (`<pack>` = its path, also exported as `SENTINEL_WORKBOOK`); outputs go to `artifacts/private/`, which is gitignored. Only tenant codes and event IDs appear here, never names from the brief or the pack.

Related documents: [data findings and assumptions](12-data-findings-and-assumptions.md) (doc 12), [detailed design / LLD](13-detailed-design-lld.md) (doc 13), [cost and sizing](14-cost-and-sizing.md) (doc 14), [operations runbook](15-operations-runbook.md) (doc 15). Docs 12, 13 and 15 were written in parallel with this one; check their section names before quoting them.

---

## 1. 20-minute walkthrough

| Minutes | Segment | Say / show |
|---|---|---|
| 0–2 | The problem | Evidence assembly, not prediction. The brief's own example (EXC-107133) took 1 h 50 min of assembly for a decision that did not change; the signed record was `RELEASE_WITH_NOTE` and reconstruction four weeks later took 1.5 days. I do not try to predict a disposition. I make the basis of one reconstructible and I keep the clock honest. |
| 2–4 | Four concepts that the board paper blurs | (1) **Non-actionable closure** of an alert, which automation may do. (2) **Product disposition** (release, quarantine, destroy…), which is always a named human. (3) **Regulatory notification**, which starts at alert time on its own clock, independent of (1) and (2). (4) **Carrier claim**, which depends on the disposition and on later corrections (April: 9 invoices withdrawn). Most design errors come from letting one of these drive another. See [doc 01](01-where-we-land.md), [doc 05](05-degradation-and-regulatory-clock.md). |
| 4–6 | The decision | A bounded, human-controlled, single-tenant EU pilot with explicit gates, not "live at day 90". No automated disposition, no cross-tenant precedent retrieval, no LLM in the decision path. First tenant and reasoning: [doc 01 "Why this tenant first"](01-where-we-land.md), rollout in [doc 10](10-future-roadmap.md). |
| 6–9 | The critical component | The thing that keeps me up at night is the **temporal, tenant-scoped evidence assessment**: given one alert, say exactly what evidence exists, what is missing, what conflicts, as known at a stated time, and **abstain** whenever required evidence is absent or ambiguous. A wrong "looks fine" here becomes a signed release of product that should not have been released, and it is silent. Missing evidence must never read as favourable; that is the invariant the code and tests protect (`prototype/src/sentinel/evidence/assessment.py`; `prototype/tests/unit/test_assessment.py`). The lifecycle/clock kernel around it is real but conventional. |
| 9–15 | Live demo | Sequence in 1.1 below (about 6 minutes; rehearse it, do not improvise). |
| 15–17 | The design in three diagrams | Open [doc 02](02-system-architecture.md) (regional components and tenant boundary), [doc 04](04-case-lifecycle.md) (state flow, waiting, reopening), [doc 05](05-degradation-and-regulatory-clock.md) (independent clock and degraded modes). Doc 13 holds the pinned-down LLD behind them. Spend one sentence each on the boundary reasoning: the clock is separate because the February chiller storm showed queue health must not decide filing; tenant keys are on every row because Cl.22 for T-MERIDIAN forbids shared derived artefacts. |
| 17–19 | Rollout, gates, what I did not build | Gates in [doc 10](10-future-roadmap.md). Not built, on purpose: live connectors, document interpretation or OCR of scanned annexures, regulator delivery, a model call, production identity or signatures, legal calendars, WORM retention. Each is named in [doc 09 "Explicit exclusions"](09-risks-assumptions-and-open-questions.md) with the reason. Board items I think are wrong or unqualified (the 70% closure target as stated, nine months for all 34 tenants, "no late notifications" as an absolute) are argued in [doc 09](09-risks-assumptions-and-open-questions.md). |
| 19–20 | Honesty statement | See 1.2. |

### 1.1 Live demo sequence

Setup (once, before the session):

```sh
python scripts/check.py
python -m sentinel --db prototype/output/private.db import <pack>
python scripts/select_demo_cases.py --db prototype/output/private.db --output-dir artifacts/private
```

`check.py` should report 55 tests passing (2 are skipped unless `SENTINEL_WORKBOOK` is set; with it, all 55 run).

1. **Whole-pack posture (30 s).** Show `artifacts/private/assessment-summary.json`, produced by
   `python -m sentinel --db prototype/output/private.db assess-all --compare-history --output artifacts/private/assessment-summary.json`.
   Point at: 420 events, **ABSTAIN 420**, BLOCKED_BY_CONFLICTS 234, INCOMPLETE_EVIDENCE 186; conflict kinds (SYS-03 tenant attribution 96, firmware TT-2.14.3 under bulletin TT-CB-114 91, SOP overlaps, product→study presentation mismatch 23). Say plainly: this is the pack, not a bug (Q1 below).
2. **EXC-110336 (T-VIRENT), current view.**
   `python -m sentinel --db prototype/output/private.db assess --tenant T-VIRENT --event EXC-110336 --output artifacts/private/x.json`
   Point at: the firmware bulletin conflict, the sop-vir-9115 Rev 04/05 overlap, `known_at`, the package hash, and the list of event fields that were *listed but not read* (historical outcomes).
3. **EXC-110336 with `known_at`.**
   `python -m sentinel --db prototype/output/private.db assess --tenant T-VIRENT --event EXC-110336 --known-at 2026-01-01T00:00:00+00:00 --output artifacts/private/x-replay.json`
   Point at: the bulletin is hidden because it was recorded after that instant, and the package hash differs. This is the "what did we know then" answer the March inspector asked for.
4. **verify-assessment.**
   `python -m sentinel --db prototype/output/private.db verify-assessment artifacts/private/x.json`
   Then edit one character in a copy and run it again to show it fails. State the limit: a hash shows alteration against a trusted copy, not that the content is correct.
5. **EXC-110336 (T-VIRENT) with the correction.** Its product master row (`02` row 16) cites a vial study (STB-4417) for a syringe product; EXC-112135 (T-KAVERI, STB-7388) is the same defect on another tenant. Run `assess` without and then with `--corrections artifacts/private/demo-correction.json` (overlay recorded 2026-09-20; it is a demonstration fixture, not a QA action). Point at: a *new* assessment with a new hash, while the original package still verifies. This is the shape of the April calibration problem (Section 4b).
6. **Cross-tenant access.**
   `python -m sentinel --db prototype/output/private.db assess --tenant T-VIRENT --event EXC-110287`
   (EXC-110287 belongs to T-KAVERI.) Expect a not-found error, indistinguishable from a nonexistent event. The HTTP API gives the same 404 for foreign cases ([docs/API.md](API.md)); unit tests are `test_cross_tenant_access_is_indistinguishable_from_missing` and `test_same_identifier_under_two_tenants_resolves_only_within_tenant`.
7. **Lifecycle (optional, 60 s).** `python -m sentinel demo` on fictional data: premature signing is rejected, independent approval, reopening keeps history, reminder retry.

Fallback if the workbook will not load on the day: use `data/anonymized-evaluation.xlsx` and the pre-generated `artifacts/public/` summaries (same commands, replaced keys, synthetic dates). Say so out loud.

Other demo cases, if asked: EXC-112198 (T-AURA, blank product reference), EXC-111008 (SYS-03 untagged, quarantined for attribution), EXC-112583 (unreadable study), EXC-111064 (unresolved product, unverified alias hint that is shown but never resolves), EXC-110287 (T-KAVERI, 360 h window recorded on the row), EXC-111519 (study absent from the index).

### 1.2 Closing honesty statement (say it near-verbatim)

"What you have seen is a prototype of the part I distrust most, running on a single hand-assembled snapshot. It is not production, and it has not been clinically validated: the 420 abstentions mean the pack cannot support an automated judgement, and I did not tune anything to change that. The notification clock is a stub with a provisional policy; a reminder is not a regulator receipt. 118 events have a historical disposition alongside open conflicts. Those are candidates for re-review, not proof that anyone erred. AI was used heavily for the thinking, the design and the build, and the working log records where it was wrong. Time spent is in the covering note."

---

## 2. Deep-dive preparation: the two parts I am least comfortable with

### (i) Temporal semantics with one snapshot and no recorded-time history

**What the prototype does.** Two axes: `as_at` (valid time, the excursion start, picks the SOP revision and contract) and `known_at` (knowledge cutoff, hides facts recorded later). SOP selection uses date-only effective ranges, half-open at the boundary and flagged (`test_policy_interval_boundaries_are_half_open_and_flagged`). Replay and corrections are tested (`test_historical_replay_hides_facts_recorded_after_known_at`, `test_correction_yields_new_assessment_and_leaves_original_intact`, `test_repeated_execution_is_deterministic`).

**What is faked by assumption.** The workbook has no recorded-time column. Rows are treated as known at the pack's extract date. Only three kinds of fact carry their own recorded time: alias confirmations (`confirmed_on`), incident-log entries (`date`) and explicit correction overlays (`recorded_at`). So `known_at` replay is **real for those three and vacuous for everything else**. Product master has no validity dates at all, so the prototype cannot tell whether a stability-study reference was current on the excursion date. It can only say what the snapshot shows.

**What production adds** ([doc 03](03-data-model.md), [doc 13](13-detailed-design-lld.md)): every evidence row is bitemporal (`valid_from/valid_to`, `recorded_at`), append-only, with supersession instead of update. Ingestion stamps `recorded_at` on arrival and keeps source version identifiers. A retrospective correction is a new row with a later `recorded_at`, never an edit. The selection query is `valid_at(as_at) AND recorded_at <= known_at`.

**Talking points.**
- I separated the axes in the interface now so that the stored package shape does not change when real history arrives.
- A replay on this pack proves the mechanism and the hash behaviour; it does not prove any historical conclusion.
- The package records what it could not know (the listed-not-read fields and the snapshot assumption) rather than implying completeness.

**Weakest point.** Anyone can say: "your `known_at` for 90% of the evidence is the extract date, so a replay to January 2026 shows the same SOPs as today." That is correct. I cannot show that SOP indexes are complete, or that a document was in force on a given date, from this data. The date-only SOP ranges also cannot say which revision applies on the changeover day beyond the half-open convention and a flag, and T-KAVERI's site limits sit in paper annexures the index does not describe. The honest answer is that production correctness depends on QA-owned document registration, which I specify but did not build.

### (ii) The notification clock with calendars and regulator receipts

**What the prototype does.** Obligations are derived from the alert, with the clock starting at alert receipt (`test_notification_clock_starts_at_alert_receipt`), and are independent of the case lifecycle, so reopening or a slow review changes nothing. A reminder outbox with retries exists; a receipt is human-attested. The policy is `notification-policy-stub-v1`. Windows come from the supplied rows (for example 360 h on the EXC-110287 row; 72 h on the T-AURA and T-NORDIA rows) and are provisional.

**What is stubbed.** Legal calendars (business days, holidays, time zones), the definition of "detection" that starts the clock, reportability rules per regulator, the filing channel, and receipt ingestion. Unknown windows are treated as urgent manual review, never as exempt. Outbox delivery is internal; nothing contacts a regulator.

**What production adds** ([doc 05](05-degradation-and-regulatory-clock.md), [doc 13](13-detailed-design-lld.md), [doc 15](15-operations-runbook.md)): a versioned `policy_bundle` per jurisdiction with `valid_from`, calendar tables per regulator, a deadline computed once and stored with its policy version, a clock service that is separate from the review queue and from the alert-storm path (priority lane for obligations, shed load on the false-alert path first), deadline-approaching escalation, and receipts ingested from the regulator channel with a human attestation as fallback.

**Talking points.**
- The February failure was queue contention, so the design goal is isolation: obligations never wait behind alert triage.
- "No late notifications" is a goal with controls, not a guarantee: a regulator outage or a wrong policy can still make a filing late. What the design adds is early warning and a recorded reason.
- Policy changes are versioned and replayed before activation (Section 4a).

**Weakest point.** I cannot defend the legal content. "Next business day" and "five days" depend on calendars and on when detection legally occurs. I have taken alert receipt as the start, which may be earlier or later than a regulator's reading, and I have no regulator receipt format. A reviewer could also ask what happens when the alert timestamp itself is wrong (logger clock drift, gateway gap). My answer is to keep the raw timestamp, flag the gap, and start from the earlier of the plausible times, but that is a position, not tested behaviour.

---

## 3. Five likely difficult reviewer questions

### Q1. "Every one of the 420 assessments abstains. Is that useful?"

It is the correct output for this data, and the more useful result is the *reason* each case abstains. Across the 420 events: 234 are blocked by at least one conflict and 186 have incomplete evidence. The pack lacks the SOP bodies, the stability documents and the calibration bulletins, and its product master has no validity dates, so no event could responsibly support an automated judgement ([doc 07 "Assumptions that turned out wrong"](07-working-log.md), [doc 12](12-data-findings-and-assumptions.md)). What the pass produced is a reviewer-ready list of specific blockers: 96 untagged SYS-03 records needing attribution, 91 events on firmware TT-2.14.3 under bulletin TT-CB-114, SOP overlaps (sop-vir-9115 35 events), 23 product→study presentation mismatches. Each is something a human currently finds by hand in the 1 h 50 min. It also keeps the stricter invariant: `test_every_public_event_abstains_and_hashes_deterministically` and `test_supplied_pack_exhibits_documented_failure_modes`. If an assessment *had* produced "clear to release" for even a handful of rows, I would suspect the code first. The 118 rows where a historical disposition sits next to open conflicts are re-review candidates, not errors, since the historical outcomes are listed but never read (`test_historical_outcomes_are_listed_but_never_read`). What I cannot claim is that the kernel would pass a case once evidence is complete; that needs the retrospective evaluation against known outcomes that the brief requires before go-live.

### Q2. "Why not fix the 70% automated closure first? It is the business ask."

Because the closure number is worth little compared with what goes wrong after it, and I could not defend a change to it with this data. The brief gives about 78% closure of non-actionable alerts and an 82% non-actionable share, so the rules engine already closes about 64% of all alerts ([doc 09](09-risks-assumptions-and-open-questions.md)). The step from 64% to 70% is about 680 more alerts a month, whereas the destroy loss ($19.4M, perhaps a third salvageable), the inspection finding and the 14 late filings are all evidence and clock failures on the roughly 2,000 cases that need adjudication. Closure is also where the November incident came from: a change in one place altered 34 customers' outcomes without a retrospective gate. The pack has no ground truth for non-actionable status: the historical dispositions are reviewer outputs, and some are in the 118 conflicted candidates. Raising closure first would mean tuning a 2,400-rule engine against unlabelled history. My position: closure stays with the existing engine at the pilot tenant, and any increase is a versioned `policy_bundle` change that passes replay with explained differences before activation ([doc 06](06-versioning-and-deployment.md)). 70% is a target to qualify per tenant, not a go-live number. The cost of this position is that I am not delivering the board's second commitment on schedule, and I say so.

### Q3. "Your as-at query assumes the SOP index is complete and date-only. What happens on the boundary day, and with T-KAVERI's paper annexures?"

It does not assume completeness; it refuses to infer it. Boundary: effective ranges are half-open, and an excursion on a day where one revision ends and the next begins is flagged, not silently assigned (`test_policy_interval_boundaries_are_half_open_and_flagged`). Overlapping revisions are a conflict, not "pick the latest" (`test_overlapping_sop_revisions_are_a_conflict`; in the pack 35 events on sop-vir-9115 Rev 04/05, 16 on sop-kav-5329, 13 on sop-kav-9392). Because the index is date-only, I cannot tell hours-level changeover, so the flag sends it to a human. Site-specific limits in an annexure are required evidence: a site-scoped SOP with no registered annexure is a blocker (`test_site_specific_scope_requires_annexure`). A scanned annexure with handwritten amendments is *registered as a document* in production with a QA-attested transcription of the amended limits; the prototype does no OCR and does not read it. If the index itself is wrong or incomplete, no code of mine detects it; that is why an index entry is evidence of existence, not of applicability, and why the pilot gate includes QA reconciliation of the index for the pilot tenant before go-live ([doc 10](10-future-roadmap.md), [doc 12](12-data-findings-and-assumptions.md)). The residual risk is a missing revision that does not appear anywhere. I record it in [doc 09](09-risks-assumptions-and-open-questions.md).

### Q4. "How does Cl.22 survive a shared embedding index or a shared model fine-tune?"

It does not survive either, so neither exists in the design. Cl.22 (T-MERIDIAN) forbids models, indexes or derived artefacts built on its data being used for another customer. The pilot has no embeddings and no fine-tuning at all: the kernel is deterministic code over tenant-keyed rows. In the production design every table, index, export and outbox item is keyed by tenant, and any retrieval index is *per tenant* with a tenant-specific key, so there is nothing shared to leak and no pooled vocabulary ([doc 14 §4](14-cost-and-sizing.md), [doc 02](02-system-architecture.md)). Precedent retrieval across tenants is a non-goal, which also answers the near-miss where similar-case lookup almost exposed one customer to a competitor. No provider-side training: zero-retention terms are a procurement gate, and a route without them is excluded on cost sheet grounds ([doc 14 §3](14-cost-and-sizing.md)). Evidence: `test_same_identifier_under_two_tenants_resolves_only_within_tenant`, `test_misleading_file_path_does_not_transfer_ownership`, and the 404-for-foreign-case behaviour in `prototype/tests/integration/test_http.py`. Gaps I should name: the prototype enforces isolation in application code on one SQLite file, not by separate storage; production needs per-tenant encryption keys and a cross-tenant leak test in CI. Also, a tenant's *aggregate* statistics shaping a shared rule default is a derived artefact, so threshold tuning is per tenant.

### Q5. "You rejected an LLM in the decision path. What does the USD 3,000 buy, and what happens on a 30-day sunset?"

Short answer: the ceiling buys bounded assistive work, not judgement, and the design does not need it. Doc 14 prices the routes: the per-unit ceilings sum to USD 2,939/month (reviewed-case drafting 2,255; screening 684), with USD 61 of margin, and the realistic spend of the candidate routes is a small fraction of that ([doc 14 §2–3](14-cost-and-sizing.md)). A model, if used, drafts a summary of the already-assembled evidence package for the reviewer and cites package items; it cannot add facts the package lacks, and a citation that does not resolve to a package item is rejected. The decision, the closure, the clock and the signature stay deterministic or human. A 30-day sunset therefore changes nothing a reviewer or regulator depends on. A model is pinned per case revision; a replacement runs only after a qualification replay on the pilot tenant's history shows explained differences; until then the draft step is omitted and the screen shows "no draft" (degraded mode, [doc 05](05-degradation-and-regulatory-clock.md), [doc 06](06-versioning-and-deployment.md)). June's failure was a silent swap; here a swap cannot be silent. Self-hosting is dominated on cost: one always-on instance costs more than the whole envelope. I should concede that I have not measured draft quality or reviewer overrule rates; the model path is design only and the prototype calls no model.

---

## 4. Change-response example

### 4a. A regulator shortens a market's window from 72 h to 48 h from a date

1. **New artefact.** `policy_bundle` version N+1 for that jurisdiction with `valid_from = <effective date>`, the new window, and the regulatory source reference. Old versions stay. A bundle is data, not a deploy, but it goes through the same release gates as code ([doc 06](06-versioning-and-deployment.md)).
2. **Which obligations use it.** An obligation is computed once at alert time and stores the `policy_version` it used. Alerts received on or after `valid_from` get 48 h. Existing obligations keep 72 h. The prototype's equivalent is `POLICY_VERSION = "notification-policy-stub-v1"` and the tested start-at-alert behaviour.
3. **If the regulation is retroactive.** Record a *policy correction* (with `recorded_at`) that generates new obligation revisions for open obligations in scope. Originals are retained and linked; the superseding revision carries the tighter deadline and an immediate escalation if it is already past. Nothing is edited in place.
4. **Replay report before activation.** Run the new bundle over open and last-N-months cases and report: obligations whose deadline moves, which are already at risk, and which tenants are affected. Same mechanism as the retrospective evaluation; the output is a diff list with reasons.
5. **Approval.** QA signs the bundle and the replay report; activation is a recorded event; rollback is reactivating version N, which does not change obligations already created under N+1.
6. **Other effects.** Reminder cadence derives from the stored deadline, so schedules update with the revisions; the clock service's alerting thresholds use the same stored deadline. Disposition, case state and carrier claims are not touched.

What I would ask in the room: effective date semantics (alert time vs detection vs receipt), whether in-flight filings are affected, and whether a grace period exists. Those are policy inputs, not engineering.

### 4b. A second calibration bulletin affects firmware TT-2.15.0

1. **Record.** A `calibration_bulletin` evidence row with its own `recorded_at`, the affected firmware/logger range and the correction (or "no correction available", which is a blocker, as in `test_affected_firmware_is_flagged_without_a_fixed_correction`). Existing reading data is not modified.
2. **Find affected cases.** A dependency index from logger → readings → assessments → cases and from bulletins to firmware. A query over the index finds every case whose evidence used a logger on TT-2.15.0. In April this was 214 cases found by hand.
3. **Re-assess.** For each affected case, create a *new assessment revision* with `known_at = now`. The prior revision remains and still verifies; the hash differs. Signed dispositions are untouched: they are legal statements by a named person about what they knew then.
4. **Human work.** Impact-review tasks open for each case whose new revision differs materially; reviewers sign a "reaffirm" or open a reopening. Reopened cases keep their history and the original package.
5. **Carrier claims.** Where a reopened outcome invalidates an invoice, a withdrawal request is queued through the outbox with an idempotency key and a tenant scope. It is only sent after human approval of the changed disposition. This treats the claim as a consequence of the decision, not as part of it.
6. **Regulatory follow-up.** Assessed separately per case: a changed outcome does not itself reopen or refile a notification. A reviewer decides whether a follow-up is required and the obligation system records the decision.
7. **Control.** The replay report goes to QA before bulk revisions run; revision creation is batched and rate-limited so it cannot starve the obligation lane.

**What the prototype shows today.** The shape, not the dependency index or the tasks. EXC-110336 with and without `--known-at 2026-01-01T00:00:00+00:00` shows the bulletin appearing or disappearing from the knowledge view, with a different hash. EXC-110336 with `--corrections artifacts/private/demo-correction.json` shows a correction recorded 2026-09-20 yielding a new assessment while the original package still verifies. Not built: the logger→case dependency index, impact-review tasks, outbox withdrawal of invoices, and the follow-up assessment. They are specified in [doc 13](13-detailed-design-lld.md).

---

## 5. Submission email draft

> **To:** the address in §10 of the brief (Sangeeta in copy if applicable)
> **Subject:** Sentinel adjudication case study: submission from Zulfiqar
>
> Hello,
>
> My submission is a public repository: `<REPOSITORY LINK: https://github.com/Zulfiqar7862/kccs-adjudication-case-study, confirm before sending>`.
>
> To run it (Python 3.11+, from a fresh clone):
> ```sh
> python -m pip install -r requirements.txt
> python scripts/check.py
> python -m sentinel demo
> ```
> `check.py` reports 54 passing tests (2 more run against the supplied workbook when `SENTINEL_WORKBOOK` is set).
>
> Where the four deliverables are:
> - **A, where I land:** `docs/00-executive-summary.md`, `docs/01-where-we-land.md`, `docs/09-risks-assumptions-and-open-questions.md`, `docs/10-future-roadmap.md`, `docs/12-data-findings-and-assumptions.md`.
> - **B, design (HLD/LLD):** `docs/02` to `docs/06`, `docs/13-detailed-design-lld.md`, `docs/14-cost-and-sizing.md`, `docs/15-operations-runbook.md`.
> - **C, prototype:** the evidence-assessment kernel in `prototype/src/sentinel/evidence/assessment.py`, its tests, and `prototype/WALKTHROUGH.md`; validation in `docs/08-validation-and-test-strategy.md`.
> - **D, working log:** `docs/07-working-log.md` and `docs/11-ai-review-corrections.md`.
> - Reviewer guide: `docs/README.md`, `docs/16-review-walkthrough.md`, `SUBMISSION_CHECKLIST.md`.
>
> Things you should know:
> - It is a prototype of the hardest component: not production, no live integrations, no regulator delivery, no clinical validation. Over the supplied 420 events it abstains on all of them, deliberately, and lists the blockers.
> - I used AI assistance heavily for analysis, design and code. The working log records what was kept, discarded and corrected. `<state whether the original session transcripts are attached or where they are>`.
> - The supplied workbook is not committed. To run against it: `SENTINEL_WORKBOOK=<path> python scripts/check.py`. A reduced anonymized workbook (`data/anonymized-evaluation.xlsx`) is included for the mechanics.
> - `<privacy statement on tenant codes; see the candidate task list>`
>
> Time spent: ___ hours (to be completed by the candidate).
>
> Regards,
> Zulfiqar

---

## 6. Candidate review tasks before sending

Zulfiqar must do these personally; none can be delegated to the tooling that wrote the documents.

- [ ] Read docs 00–16 end to end. Be able to explain every number you cite (64%, 2,939, 420/234/186, 118) without opening the file.
- [ ] Run `python scripts/check.py` from a fresh clone and virtualenv, and `python -m sentinel demo`. Run once with `SENTINEL_WORKBOOK` set and confirm 55 tests pass with none skipped.
- [ ] Run every command in 1.1 with the real workbook; compare the output with the points listed. Rehearse the demo twice, timed.
- [ ] Decide the privacy stance for tenant codes (they are pseudonymous codes from the pack, but the pack is confidential): keep, replace with generic labels, or ask in writing. Check `docs/` and `data/anonymized-evaluation.xlsx` for any customer or person name. Confirm `artifacts/private/` and the supplied workbook are not tracked.
- [ ] Verify the repository is public and readable, the link in the email works in a private window, and the licence/readme state is as you intend.
- [ ] Fill in the repository link and **time spent** honestly. The brief suggests 10–14 hours; report the real figure and, if over, say what took the time.
- [ ] Export the AI session transcripts (brief §8 D: "keep the sessions") and decide how they are delivered (attached archive or private link). The authored log does not replace them.
- [ ] Check the working log for anything you would not defend: especially any "wrong assumption" you do not actually remember being wrong, and any disagreement with the AI that you cannot reconstruct. Edit it to match what happened.
- [ ] Decide which two deep-dive topics you will own (Section 2) and do a fifteen-minute dry run of each aloud. Also prepare one unseen-change practice run.
- [ ] Send to the address given in §10 of the brief, with Sangeeta in copy if that is the arrangement you have.
