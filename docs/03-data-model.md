# 3. Data model — LLD

## 2.3 LLD: data and temporal semantics



All business primary/foreign keys include `tenant_id`, and storage paths, cache keys, encryption contexts and message keys include `tenant_id` and `region_id`. PostgreSQL RLS is defence in depth; application claims come from verified identity, never an arbitrary client header. No unscoped vector search followed by post-filtering. the restrictive-derived-data tenant uses a separate tenant index/model artefact namespace, evaluation corpus and keys; no cross-tenant derived artefacts, even when a draft appears anonymised. Shared software can be reused; tenant-derived data cannot.

### Core records

* `case(tenant_id, case_id, aggregate_version, shipment_id, physical_excursion_id, alert_received_at, status)`; an original event is immutable. Multiple physical events can affect one batch; multiple alerts can refer to one physical event.
* `episode(tenant_id, episode_id, case_id, sequence, opened_at, reason, previous_decision_id)`: reopening adds an episode, not a new original clock.
* `evidence_blob(tenant_id, evidence_id, object_version, sha256, source_system, source_ref, observed_at, received_at, format, data_quality, retention_until)`; `evidence_edge` records dependencies/derivations.
* `product_version`: strength, dosage form, presentation, market, storage rules and original identifier fields; `alias_assertion`: source string, candidate canonical entity, entity kind, valid/recorded intervals, authority, proposed/approved/disputed/rejected status. Tenant-less pack aliases are proposals only.
* `facility`, `room`, `equipment`, `occupancy(tenant_id, pallet_id, batch_id, room_id, leg_id, valid_range, recorded_range, provenance)`; no inference that similar names mean equal GMP licences. Correct Memphis timezone requires steward approval (`03!F52:F56` says America/New_York); do not silently fix history.
* `controlled_document_version(tenant_id, doc_id, revision, valid_range, recorded_range, source_blob_id, language, approval)`. `scope_assertion` binds site/product/operation; `annexure_link` binds document versions. Handwritten changes require an approved exception, never OCR-only promotion.
* `stability_rule`: presentation-specific approved temperature envelope, permitted duration, cumulative/once-only semantics, forbidden freeze/light conditions, study version/page. Blank/no study is **unknown**, not zero tolerance or permission. MKT uses a QA-approved activation energy and the full irregularly sampled series; it cannot excuse freezing or missing samples.
* `batch_exposure(tenant_id, batch_id, physical_excursion_id, exposure_version, interval, quality, invalidates_id)` unique physical-event/version key; serialise updates per batch or use an optimistic batch version. Duplicate alerts never double-count exposure; late data creates a superseding calculation, not additive double counting.
* `decision(tenant_id, decision_id, episode_id, manifest_id, rationale, outcome, affected_pallet_ids, expiry_change, signed_at)`, `signature(signer, authority_version, decision_hash, authentication_context, meaning)`. Expiry change is a distinct structured human decision, not lost in a generic note/relabel outcome.
* `obligation(tenant_id, obligation_id, case_id, jurisdiction_id, policy_version, starts_at, due_at, status, confirmed_at)` and `filing_attempt(idempotency_key, payload_hash, attempted_at, channel, receipt_blob_id, status)`. Claims obligations have separate legal windows and their own owner.
* `release_manifest`: code/container digest, tenant rule overlay hash, reference snapshot, prompt, model ID/weights, tokenizer, decoding configuration, retrieval/index version, approved template/language, input/output hashes and QA qualification ID. No model is a valid versioned selection.

### Two questions, two axes

“Which SOP applied then, as we believed then?” is not “which SOP do we now believe applied then?”. All effective references use half-open intervals `[valid_from, valid_to)` and `[recorded_from, recorded_to)`. The source may contain overlapping valid intervals; ingestion **retains** them as a conflict instead of enforcing a constraint that silently drops a version. Approved governing bindings must be unique for a tenant/site/product/operation at both axes. Original facts and stewardship corrections are append-only audit events; a mutable temporal projection is rebuildable.

```sql
SELECT * FROM controlled_document_version
WHERE tenant_id = :tenant
  AND doc_id = :doc
  AND valid_from <= :excursion_instant
  AND (valid_to IS NULL OR :excursion_instant < valid_to)
  AND recorded_from <= :knowledge_cutoff
  AND (recorded_to IS NULL OR :knowledge_cutoff < recorded_to);
```

Zero rows means missing history; two rows means conflict. Do not use `ORDER BY revision DESC LIMIT 1`, and do not parse `supersedes_text` as a trusted relationship. `05!E115:E116` even has Rev05 effective before Rev04. A correction learned in October about a July SOP closes the old **recorded** interval in the projection and appends the corrected assertion; both July-at-August and July-at-November queries remain answerable. Episode manifests pin the exact version IDs and blob hashes; later queries do not replace their basis.

The workbook is a September 14 snapshot without transaction history. Its `last_updated`, revision effective dates and alias confirmation dates are not ingestion timestamps. Prototype import uses a declared synthetic snapshot time only; querying knowledge before that returns unknown history. No attempt is made to recreate the August 2025 inspector's missing documents. Production effective date-only metadata is interpreted using an approved issuing/site timezone; UTC midnight in the demo is a limitation. Cross-midnight boundary cases stay manual until scope/timezone is approved.

### Exposure and identity rules

Keep observed extrema unchanged. TT-2.14.3 under-reading “up to 1.8°C” gives an uncertainty interval `[observed, observed+1.8]` for affected observations, not a deterministic correction and never subtraction. For the anchor case the lower reading near freezing may be warmer in reality, but the interval does not establish that it was above 2°C. For a warm excursion, under-reading can make risk worse. Bulletin applicability dates/devices and per-sensor corrections need source evidence; the prototype conservatively flags every matching firmware string, including later dates, without claiming all are in the bulletin's original three-week cohort.

Temperature range, once-only/cumulative duration, identity, approved SOP and stability rule are independent preconditions; commercial liability is not one of the product-fitness arithmetic gates. Historical outcomes/triage are evaluation labels only and never features for eligibility. Product identification includes tenant, market, presentation, strength and packaging, not just molecule. The prototype exact source match is explicitly weaker than a verified canonical identity.



Implementation: `domain/models.py`, `domain/value_objects.py`, and `temporal/effective_dating.py`. The SQLite audit/reference stores are real local implementations, not production multitenant databases. Audit hash chains detect accidental tampering but are not protection against an administrator rewriting the entire chain; production needs WORM and externally anchored hashes.
