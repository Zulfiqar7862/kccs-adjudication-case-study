# Local API and data contract

The server is a local development adapter, not a hardened public service. It rejects non-loopback hosts. All routes except `/health` require `Authorization: Bearer <token>`; the token maps to tenant, actor and role. Request bodies cannot change that identity. No bearer token is logged by the request handler.

## Reads

| Method / route | Result |
|---|---|
| GET `/health` | Process health only, not database readiness |
| GET `/cases` | Credential tenant's case IDs, states, revisions and optimistic versions |
| GET `/cases/{id}` | Current case and evidence packet; foreign/unknown case is 404 |
| GET `/cases/{id}/audit` | Source row, revision packets, audit chain and manifest hash |
| GET `/notifications` | Tenant obligations, deadlines, status and human-attested receipts |
| GET `/sops?valid_at=2026-01-10&known_at=2026-02-01` | SOP index candidates at valid time and import knowledge cutoff |

`known_at` before the actual local import timestamp returns no known rows. The import timestamp is not reconstructed historical system knowledge. SOP applicability uses excursion time; notification windows use alert time. Candidate index rows do not establish site applicability or replace controlled source documents.

## Mutations

Require `Content-Type: application/json`, an object body, an integer `expected_version`, and a unique `Idempotency-Key` header. Maximum body size is 256 KiB; chunked requests are unsupported. Exact request replay returns its original result. Reusing a key with another request or acting on a stale version returns 409. A denied/invalid mutation does not advance the case version or append audit history.

| POST `/cases/{id}/...` | Role | Body in addition to `expected_version` |
|---|---|---|
| `evidence` | reviewer | `kind`, `source_ref`, `content` |
| `review` | reviewer | `resolutions` mapping every blocker string to existing evidence ID list; `note` |
| `sign` | signer, or site_qa/corporate_qa for dual policy | `disposition`, `rationale` |
| `reopen` | reviewer | `reason` |
| `notify` | regulatory | `receipt`, `sent_at` |

Evidence kinds are `SOP`, `STABILITY`, `TELEMETRY`, `IDENTITY`, `BATCH`, `CONTRACT`, `OTHER`. The first six are required for review. An explicit human review attests authenticity/applicability; the service does not semantically verify supplied text. Adding evidence invalidates review and signatures. Only disposed cases may reopen, and disposed evidence cannot be edited without reopening.

Dispositions: `RELEASE`, `RELEASE_WITH_NOTE`, `QUARANTINE`, `REWORK`, `RETURN`, `DESTROY`. The reviewer cannot sign their own packet. The whole word `dual` in the imported tenant policy activates the two-role development policy; otherwise a signer is required. Dual approvals need distinct actors/roles and matching dispositions. This text-based adapter is not a production authority roster.

A `notify` request records an external filing **attestation**, not an actual filing. `sent_at` must be between alert time and current time. Existing receipts cannot be silently overwritten. A receipt suppresses later pending internal reminders. Delivery already in flight may still occur; receivers must deduplicate stable keys. No command pauses or resets the legal clock.

Example attachment (all values fictional):

```json
{
  "expected_version": 1,
  "kind": "IDENTITY",
  "source_ref": "demo-stub://identity",
  "content": "FICTIONAL TEST STUB: not authoritative product evidence"
}
```

Errors: 400 malformed input, 401 invalid/missing bearer, 403 role or separation-of-duty violation, 404 absent/foreign resource, 409 version/state/idempotency conflict, 413 excessive body, 415 wrong content type, 422 invalid business command. Error responses are JSON objects with an `error` field. Read the case again after a conflict; do not guess a new version.

## Workbook contract

Inputs are local XLSX files, not HTTP uploads. At minimum provide the following tabular sheets with a header row. The reader preserves strings and original Excel row number as `_row`. It also retains other sheets for source provenance.

| Sheet | Fields used |
|---|---|
| `01_Excursion_Events` | `event_id`, `tenant_code`, `alert_ts_utc`, `excursion_start_utc`, `product_ref_as_received`, `logger_fw`, `gateway_gap_min`, `interpolated`, `readings_in_window`, `regulator_reportable`, `reg_window_hours` |
| `02_Product_Master` | `tenant_code`, `brand_as_labelled`, `internal_sku`, `gtin`, `legacy_code`, `stability_study_ref` |
| `05_SOP_Index` | `tenant_code`, `doc_id`, `revision`, `effective_from`, `effective_to`, `applies_to_facilities_text` |
| `06_Stability_Index` | `tenant_code`, `study_ref`, `product_text_as_written`, `readable` |
| `12_Tenant_Constraints` | `tenant_code`, `who_signs_a_disposition` |

The fictional generator is an executable format example, not a replacement for authorized source data. Source outcomes/recommendations may be retained as raw provenance but never affect evidence readiness. Blank/unknown identities, incomplete indexes, missing batch exposure and unverified source records block readiness. Invalid or missing regulatory windows create `POLICY_REQUIRED`; the service does not invent a window. Explicit `regulator_reportable=N` is replayed from the input, not independently qualified.

Use one immutable snapshot per database. Exact file hash replays are safe; any different subsequent file is rejected atomically. Import knowledge time is captured at execution. Store authorized source bytes separately; the database retains parsed values and the file digest, not an archival copy of original bytes.
