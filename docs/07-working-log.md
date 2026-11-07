# Working log

## What was retained

The first implementation read the complete eight-page brief using layout-preserving extraction and every cell on all fifteen workbook tabs. It selected evidence eligibility rather than a full clinical adjudicator because the input includes indexes, not controlled document bodies, raw telemetry or batch occupancy history. That choice remains.

The earlier local repository mixed source attachments, full reading dumps and output evidence with code. It was not public-safe. This iteration starts in a new directory with new history, retains only paraphrased design analysis and aggregate results, replaces all public examples with manually made synthetic data, and ignores the authorised local workbook, outputs and evidence. No old git objects are copied. The requested modular tree is implemented as a single Python application, not a deployment-per-folder architecture.

## Assumptions corrected by actual checks

1. The narrative's simple anchor release looked suitable for a golden. Following its product/study links instead found a presentation mismatch and an unsuitable study type. Expected outputs therefore test evidence gaps, not a clinical release.
2. Effective-date lookup alone did not resolve SOP authority. Overlapping versions and non-monotonic revision dates required returning all candidates and leaving site scope unverified.
3. An unreadable study still carried allowance-like text in an adjacent field. Readability and study design must gate eligibility; a populated number is not permission.
4. Firmware matches, changed decisions and affected incident populations have different denominators. The prototype's conservative firmware flag does not reconstruct device/date applicability.
5. The README promises queue-time reconciliation, but independent arithmetic found two discrepancies. One review timestamp is also later than the declared extract date. Snapshot import time is a demonstration assumption, never reconstructed transaction history.
6. Initial notification code treated a missing flag as not-reportable and claimed calendar qualification for some fixed-hour windows. Failing assertions exposed both; missingness is explicit and all calendar qualification remains false.

## Refactor and tooling record

The first refactor run had one failing subprocess test: pytest's process-local import path was not inherited by a new Python process. The package is now installed editable in setup, and the explicit subprocess test also supplies the source path. That actual failure is retained locally; no successful run was invented.

Formatting first exposed packed statements and integration imports below marker declarations. Ruff formatting and import reordering corrected them before the final lint gate. The box initially lacked GNU Make. Debian's configured HTTP package mirror failed; a public HTTPS package was extracted locally to run the exact Makefile commands without changing project semantics. Docker availability is reported honestly in the validation record.

The workflow implementation is in-memory; its signature guard checks the presence of a reviewed basis, not a legally qualified signer. SQLite audit chains are persistent and verifiable but not a WORM security guarantee. These limits are explicit rather than disguised by component names.

## Alternatives discarded

- Full autonomous rule release from aggregate temperatures: rejected because missing evidence is the main risk.
- LLM/vector retrieval as authority: rejected; drafting may be an optional permissioned dependency, not the source of numeric limits.
- Global shared precedent artefacts: rejected because tenant-derived-data restrictions apply to indexes and prompts as well as rows.
- A microservice per requested module: rejected for a six-person team and modest case volume; independent timer resources remain a meaningful production boundary.
- Always-on regional GPUs as the inexpensive default: rejected after idle-month arithmetic exceeded the inference ceiling.
- Treating all historical human outcomes as golden truth: rejected because some written rationales conflate liability, reporting and product fitness.

## AI and effort honesty

Grok Bot performed the assisted extraction, refactor, test execution and drafting. No candidate-versus-assistant debate, clinical QA sign-off, factual customer reply or human working-hour total was fabricated. Raw provider-session export was unavailable; the original local evidence is retained privately, while this public log is a truthful summary rather than a complete raw transcript. Candidate review and ownership of the final judgement remain necessary. No application email or regulatory message was sent.
