"""Tenant-scoped, temporally explicit evidence assessment for one workbook alert.

An assessment turns a single ``01_Excursion_Events`` row into a structured,
reproducible statement of what evidence exists, what is missing, what
conflicts, and what a human must do. It never produces a disposition.

Two time axes are kept separate:

* ``as_at``   – valid time: the excursion start, used to pick applicable SOP
  revisions and contracts.
* ``known_at`` – knowledge time: facts recorded after this instant are hidden.
  The workbook is a single snapshot with no recorded-time history, so its rows
  are treated as known at the pack's extract date. The only facts with an
  independent recorded time are alias confirmations (``confirmed_on``),
  incident-log entries (``date``) and explicit correction overlays
  (``recorded_at``).
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from typing import Any

from sentinel import __version__
from sentinel.evidence.analysis import _field, _norm, _presentation, _table, _truthy, parse_time, sops_as_at

ASSESSMENT_VERSION = "assessment-v1"
POLICY_VERSION = "notification-policy-stub-v1"

# Event columns the assessment may read. Everything else on the event row is a
# historical outcome or reviewer artefact and is listed, not read.
ALLOWED_EVENT_FIELDS = (
    "event_id", "alert_ts_utc", "tenant_code", "shipment_ref", "leg_no", "source_system", "logger_id",
    "logger_vendor", "logger_fw", "product_ref_as_received", "origin_ref_as_received", "dest_ref_as_received",
    "lane_text", "carrier_ref_as_received", "mode", "excursion_start_utc", "excursion_end_utc", "duration_min",
    "min_temp_c", "max_temp_c", "mean_temp_c", "spec_text_as_received", "readings_in_window", "gateway_gap_min",
    "interpolated", "dock_door_open_flag", "prior_excursions_lane_90d", "consignment_value_usd",
)
# Provisional policy inputs: the window is a policy fact, but its provenance on the row is unverified.
PROVISIONAL_POLICY_FIELDS = ("regulator_reportable", "reg_window_hours")
HISTORICAL_OUTCOME_FIELDS = (
    "case_opened", "triage_outcome", "rules_engine_recommendation", "final_disposition", "reviewer_id",
    "review_minutes", "systems_opened", "reviewer_overrode", "days_to_disposition", "hours_to_notification",
    "reported_within_window", "reopened_later", "notes",
)
# Telemetry sources whose records carry no tenant tag at source (11_Systems_Inventory, SYS-03).
UNTAGGED_SOURCE_SYSTEMS = ("SYS-03",)
FIRMWARE_TOKEN = re.compile(r"\b[A-Z]{2}-\d+\.\d+\.\d+\b")
BULLETIN_TOKEN = re.compile(r"\b[A-Z]{2}-CB-\d+\b")
MAGNITUDE = re.compile(r"up to\s+([0-9]+(?:\.[0-9]+)?)\s*°?\s*C", re.IGNORECASE)


class AccessDenied(Exception):
    """Raised when a principal asks for an event outside its tenant."""


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def extract_date(tables: dict[str, Any]) -> datetime | None:
    """Return the pack extract date from the README tab when it is stated."""
    for row in _table(tables, "00_README"):
        cells = [str(v) for k, v in row.items() if k != "_row"]
        if any(_norm(c) == "extract date" for c in cells):
            for cell in cells:
                try:
                    return parse_time(cell)
                except (TypeError, ValueError):
                    continue
    return None


def apply_corrections(tables: dict[str, Any], corrections: list[dict[str, Any]], known_at: datetime) -> tuple[dict[str, Any], list[dict]]:
    """Overlay corrections recorded at or before ``known_at``; the input tables are not mutated."""
    applied: list[dict] = []
    patched: dict[str, Any] = {name: ([dict(r) for r in rows] if isinstance(rows, list) else rows) for name, rows in tables.items()}
    for correction in corrections:
        recorded = parse_time(correction["recorded_at"])
        if recorded > known_at:
            continue
        rows = patched.get(correction["sheet"], [])
        target = next((r for r in rows if r.get("_row") == correction["row"]), None)
        if target is None:
            raise ValueError(f"Correction targets unknown row {correction['sheet']}#{correction['row']}")
        target[correction["field"]] = correction["value"]
        applied.append({"id": correction.get("id") or canonical_hash(correction), "sheet": correction["sheet"],
                        "row": correction["row"], "field": correction["field"], "recorded_at": recorded.isoformat()})
    return patched, applied


def _ref(sheet: str, row: dict[str, Any]) -> str:
    return f"{sheet}#row={row.get('_row', '')}"


def _resolve_product(tables, event, tenant, known_at, out) -> list[dict]:
    products = _table(tables, "02_Product_Master")
    fields = ("brand_as_labelled", "internal_sku", "gtin", "legacy_code")
    received = _norm(_field(event, "product_ref_as_received"))
    entity = {"kind": "PRODUCT", "as_received": str(_field(event, "product_ref_as_received")), "status": "MISSING_REFERENCE",
              "candidates": [], "unverified_alias_candidates": [], "source_refs": []}
    if not received:
        out["missing_inputs"].append("Product reference is blank on the alert; the consignment note or TMS record must supply it.")
        out["entities"].append(entity)
        return []
    matches = [r for r in products if _norm(_field(r, "tenant_code")) == tenant
               and received in {_norm(_field(r, f)) for f in fields} - {""}]
    for row in matches:
        entity["candidates"].append({"internal_sku": _field(row, "internal_sku"), "brand_as_labelled": _field(row, "brand_as_labelled"),
                                     "stability_study_ref": _field(row, "stability_study_ref"), "source_ref": _ref("02_Product_Master", row)})
        entity["source_refs"].append(_ref("02_Product_Master", row))
    if len(matches) == 1:
        entity["status"] = "RESOLVED_EXACT_TENANT_SCOPED"
    elif len(matches) > 1:
        entity["status"] = "AMBIGUOUS"
        out["conflicts"].append(f"Product reference {received!r} matches {len(matches)} master rows in this tenant.")
    else:
        entity["status"] = "UNRESOLVED"
        # Alias observations are reviewer sightings, not a master: surface, never resolve.
        for alias in _table(tables, "07_Alias_Observations"):
            if _norm(_field(alias, "entity_kind")) != "product" or not _truthy(_field(alias, "same_real_world_thing")):
                continue
            pair = (_norm(_field(alias, "string_a")), _norm(_field(alias, "string_b")))
            if received not in pair:
                continue
            try:
                confirmed = parse_time(str(_field(alias, "confirmed_on")))
            except (TypeError, ValueError):
                confirmed = None
            if confirmed is None or confirmed > known_at:
                continue
            other = pair[1] if pair[0] == received else pair[0]
            in_tenant = [r for r in products if _norm(_field(r, "tenant_code")) == tenant and other in {_norm(_field(r, f)) for f in fields}]
            entity["unverified_alias_candidates"].append({"alias": other, "confirmed_on": confirmed.date().isoformat(),
                                                          "confirmed_by": _field(alias, "confirmed_by"),
                                                          "same_tenant_master_rows": [_ref("02_Product_Master", r) for r in in_tenant],
                                                          "source_ref": _ref("07_Alias_Observations", alias)})
        out["required_human_actions"].append("Confirm product identity from the consignment note or tenant ERP; alias observations are not authoritative.")
        out["missing_inputs"].append(f"No exact tenant-scoped product master match for {received!r}.")
    out["entities"].append(entity)
    return matches


def _resolve_facility(tables, code: str, role: str, out) -> None:
    facilities = _table(tables, "03_Facility_Registry")
    wanted = _norm(code)
    entity = {"kind": "FACILITY", "role": role, "as_received": code, "status": "MISSING_REFERENCE", "source_records": [], "source_refs": []}
    if wanted:
        matches = [r for r in facilities if wanted in {_norm(_field(r, "code_in_source")), _norm(_field(r, "record_id")), _norm(_field(r, "name_in_source"))}]
        for row in matches:
            entity["source_records"].append({"system": _field(row, "source_system"), "record_id": _field(row, "record_id"),
                                             "timezone_in_source": _field(row, "timezone_in_source"), "cold_rooms": _field(row, "cold_rooms")})
            entity["source_refs"].append(_ref("03_Facility_Registry", row))
        if not matches:
            entity["status"] = "UNRESOLVED"
            out["missing_inputs"].append(f"{role.title()} facility {code!r} is not in any facility source record.")
        else:
            zones = {_norm(_field(r, "timezone_in_source")) for r in matches} - {""}
            entity["status"] = "RESOLVED_MULTIPLE_SOURCE_RECORDS" if len(matches) > 1 else "RESOLVED"
            if len(zones) > 1:
                entity["status"] = "CONFLICTING_SOURCE_RECORDS"
                out["conflicts"].append(f"{role.title()} facility {code!r} has conflicting timezones across source records: {sorted(zones)}.")
            entity["timezone_trust"] = "UNTRUSTED: registry timezone is known wrong for two sites (00_README); local-time semantics need site confirmation."
    out["entities"].append(entity)


def _resolve_carrier(tables, event, when: datetime | None, out) -> None:
    contracts = _table(tables, "04_Carrier_Contracts")
    received = _norm(_field(event, "carrier_ref_as_received"))
    entity = {"kind": "CARRIER_CONTRACT", "as_received": str(_field(event, "carrier_ref_as_received")), "status": "MISSING_REFERENCE",
              "candidates": [], "source_refs": []}
    if received:
        matches = []
        for row in contracts:
            names = {_norm(n) for n in str(_field(row, "names_seen_on_documents")).split("|")} | {_norm(_field(row, "counterparty_legal_entity")), _norm(_field(row, "parent_of"))}
            if received in names - {""}:
                matches.append(row)
        if when is not None:
            effective = []
            for row in matches:
                try:
                    start = parse_time(str(_field(row, "effective_from")))
                    end_text = str(_field(row, "effective_to")).strip()
                    end = parse_time(end_text) if end_text else None
                except (TypeError, ValueError):
                    continue
                if start <= when and (end is None or when < end + timedelta(days=1)):
                    effective.append(row)
            matches = effective
        for row in matches:
            entity["candidates"].append({"contract_id": _field(row, "contract_id"), "legal_entity": _field(row, "counterparty_legal_entity"),
                                         "parent_of": _field(row, "parent_of"), "claim_window_days": _field(row, "claim_window_days"),
                                         "liability_cap": _field(row, "liability_cap"), "source_ref": _ref("04_Carrier_Contracts", row)})
            entity["source_refs"].append(_ref("04_Carrier_Contracts", row))
        legal_entities = {_norm(_field(r, "counterparty_legal_entity")) for r in matches}
        if not matches:
            entity["status"] = "UNRESOLVED"
            out["missing_inputs"].append(f"No carrier contract effective at the excursion names {received!r}; claim track cannot start.")
        elif len(legal_entities) > 1:
            entity["status"] = "AMBIGUOUS_PARENT_OR_SUBSIDIARY"
            out["conflicts"].append(f"Carrier name {received!r} matches contracts with {len(legal_entities)} distinct legal entities; parent versus subsidiary must be settled from the consignment note.")
        else:
            entity["status"] = "RESOLVED"
    entity["note"] = "Carrier liability and claims are a separate financial track; they never gate the product disposition or the regulatory clock."
    out["entities"].append(entity)


def _sop_evidence(tables, tenant, when: datetime | None, out) -> list[dict]:
    section = {"valid_at": when.isoformat() if when else None, "candidates": [], "rejected": [], "conflicts": []}
    if when is None:
        out["missing_inputs"].append("Excursion start time is missing or invalid; applicable SOP revisions cannot be selected.")
        out["evidence"]["sop"] = section
        return []
    candidates = sops_as_at(tables, tenant, when)
    by_doc: dict[str, list[dict]] = {}
    for row in candidates:
        by_doc.setdefault(_norm(_field(row, "doc_id")), []).append(row)
        item = {"doc_id": _field(row, "doc_id"), "revision": _field(row, "revision"), "title": _field(row, "title"),
                "effective_from": _field(row, "effective_from"), "effective_to": _field(row, "effective_to"),
                "applies_to": _field(row, "applies_to_facilities_text"), "format": _field(row, "format"),
                "language": _field(row, "language"), "source_ref": _ref("05_SOP_Index", row), "flags": []}
        for bound in ("effective_from", "effective_to"):
            text = str(_field(row, bound)).strip()
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text) and text == when.date().isoformat():
                item["flags"].append(f"{bound} is date-only and equals the excursion date; the boundary convention and its timezone are undefined in the index.")
        if "site-specific" in _norm(item["applies_to"]):
            item["flags"].append("Site-specific annexure governs acceptance limits; annexure not supplied.")
        if "scan" in _norm(item["format"]):
            item["flags"].append("Scanned document; limits must be read from the controlled copy, not the index.")
        section["candidates"].append(item)
    for doc_id, rows in by_doc.items():
        if len(rows) > 1:
            revisions = sorted(str(_field(r, "revision")) for r in rows)
            section["conflicts"].append({"doc_id": doc_id, "revisions": revisions, "reason": "Effective windows overlap at the excursion start; supersedes_text is free text and does not settle precedence."})
            out["conflicts"].append(f"SOP {doc_id} has overlapping revisions {revisions} in force at the excursion start.")
            out["required_human_actions"].append(f"Document control must state which revision of {doc_id} governed on {when.date().isoformat()}.")
    if not candidates:
        out["missing_inputs"].append("No same-tenant SOP index row is effective at the excursion start.")
    if any(f for c in section["candidates"] for f in c["flags"] if "annexure" in f):
        out["missing_inputs"].append("Site-specific SOP annexure(s) are not supplied.")
    out["missing_inputs"].append("Controlled SOP documents themselves are not in the pack; the index is metadata, not procedure evidence.")
    out["evidence"]["sop"] = section
    return candidates


def _stability_evidence(tables, tenant, products: list[dict], out) -> None:
    rows = _table(tables, "06_Stability_Index")
    section = {"candidates": [], "rejected": []}
    refs = {_norm(_field(p, "stability_study_ref")) for p in products} - {""}
    if products and not refs:
        out["missing_inputs"].append("Matched product master row carries no stability study reference.")
    product_presentations = set().union(*(_presentation(_field(p, "brand_as_labelled")) for p in products)) if products else set()
    for ref in sorted(refs):
        same_tenant = [r for r in rows if _norm(_field(r, "study_ref")) == ref and _norm(_field(r, "tenant_code")) == tenant]
        elsewhere = [r for r in rows if _norm(_field(r, "study_ref")) == ref and _norm(_field(r, "tenant_code")) != tenant]
        if not same_tenant:
            reason = ("Reference resolves only under another tenant's ownership; not usable." if elsewhere
                      else "Not in the stability index; the index covers ~60% of the repository, so absence is not evidence that no study exists.")
            section["rejected"].append({"study_ref": ref.upper(), "reason": reason})
            out["missing_inputs"].append(f"Stability study {ref.upper()} is not available to this tenant from the index: {reason}")
            out["required_human_actions"].append(f"Locate study {ref.upper()} in the stability repository (SYS-06) and register it with ownership confirmed.")
            continue
        for row in same_tenant:
            item = {"study_ref": _field(row, "study_ref"), "product_text_as_written": _field(row, "product_text_as_written"),
                    "study_type": _field(row, "study_type"), "readable": _field(row, "readable"),
                    "permitted_excursion_text": _field(row, "permitted_excursion_text"), "file_path_text": _field(row, "file_path_text"),
                    "ownership_basis": "tenant_code column (file path is where it was found, not who owns it)",
                    "source_ref": _ref("06_Stability_Index", row), "usable": True, "flags": []}
            # The index writes "<product> — <presentation>"; the part after the dash names the presentation studied.
            written = str(_field(row, "product_text_as_written"))
            study_presentations = _presentation(written.split("—")[-1] if "—" in written else written)
            if product_presentations and study_presentations and not (study_presentations & product_presentations):
                item["usable"] = False
                item["flags"].append(f"Presentation mismatch: product is {sorted(product_presentations)}, study is {sorted(study_presentations)}.")
                out["conflicts"].append(f"Product master points at study {item['study_ref']} for a different presentation ({sorted(study_presentations)} vs {sorted(product_presentations)}).")
            if not _truthy(_field(row, "readable")):
                item["usable"] = False
                item["flags"].append(f"Readability {_field(row, 'readable')!r}: the study is real and cited but its outcome cannot be read from the index.")
                out["missing_inputs"].append(f"Stability study {item['study_ref']} is unreadable or only partially readable; a legible controlled copy is required.")
            if not str(_field(row, "permitted_excursion_text")).strip():
                item["usable"] = False
                item["flags"].append(f"{_field(row, 'study_type')} study with no permitted-excursion statement; it does not answer how long product may sit out of range.")
                out["missing_inputs"].append(f"Study {item['study_ref']} does not establish an excursion limit.")
            section["candidates"].append(item)
    out["missing_inputs"].append("Full stability reports are not in the pack; an index row cannot verify findings or applicability.")
    out["evidence"]["stability"] = section


def _telemetry_evidence(tables, event, known_at: datetime, out) -> None:
    section = {"basis": "Aggregate statistics from the alert row (min/max/mean, duration, reading count); the raw temperature series is not in the pack.",
               "logger_fw": str(_field(event, "logger_fw")), "source_system": str(_field(event, "source_system")), "flags": [], "bulletins": []}
    out["missing_inputs"].append("Raw temperature series is not supplied; only aggregates are available.")
    fw = _norm(_field(event, "logger_fw"))
    for incident in _table(tables, "14_Incident_Log"):
        text = " ".join(str(v) for k, v in incident.items() if k != "_row")
        builds = {b.casefold() for b in FIRMWARE_TOKEN.findall(text)}
        if not builds or "bulletin" not in text.casefold():
            continue
        try:
            recorded = parse_time(str(_field(incident, "date")))
        except (TypeError, ValueError):
            continue
        bulletin = next(iter(BULLETIN_TOKEN.findall(text)), str(_field(incident, "ref")))
        if fw in builds:
            if recorded <= known_at:
                magnitude = MAGNITUDE.search(text)
                bound = f"up to {magnitude.group(1)} °C" if magnitude else "an unstated bound"
                section["bulletins"].append({"bulletin": bulletin, "incident_ref": _field(incident, "ref"), "recorded_at": recorded.isoformat(),
                                             "effect": f"Readings may under-report by {bound}; the per-device magnitude and direction are not known from the bulletin.",
                                             "source_ref": _ref("14_Incident_Log", incident)})
                out["conflicts"].append(f"Logger firmware {section['logger_fw']} is subject to {bulletin}; recorded temperatures cannot be relied on and no fixed correction may be applied.")
                out["required_human_actions"].append(f"Obtain the device-specific calibration result under {bulletin} before using any temperature from logger {_field(event, 'logger_id')}.")
            else:
                section["bulletins"].append({"bulletin": bulletin, "recorded_at": recorded.isoformat(), "status": "NOT_KNOWN_AT_CUTOFF",
                                             "note": "Hidden from this assessment because it was recorded after known_at."})
    if not section["bulletins"]:
        section["flags"].append("Firmware and calibration status must be verified against vendor records; none are in the pack.")
    gap = str(_field(event, "gateway_gap_min")).strip()
    try:
        if float(gap) > 0:
            section["flags"].append(f"Gateway gap of {gap} min inside the window; readings around the gap are incomplete.")
    except ValueError:
        section["flags"].append("Gateway gap value is not numeric.")
    if _truthy(_field(event, "interpolated")):
        section["flags"].append("Series contains interpolated readings; measured versus interpolated points must be separated from the raw export.")
    try:
        if float(str(_field(event, "readings_in_window"))) <= 0:
            section["flags"].append("Reading count is non-positive.")
    except ValueError:
        section["flags"].append("Reading count is missing or non-numeric.")
    if str(_field(event, "source_system")).upper() in UNTAGGED_SOURCE_SYSTEMS:
        section["flags"].append("Source is facility BMS telemetry with no tenant tag; tenant attribution relies on the TMS room-to-consignment mapping and must be confirmed before this record is treated as this tenant's.")
        out["conflicts"].append("Tenant attribution is inferred, not recorded at source (BMS feed); quarantine for attribution before any tenant-scoped evidence is relied on.")
    out["evidence"]["telemetry"] = section
    out["missing_inputs"].append("No batch identity or lifetime exposure history is supplied; cumulative exposure cannot be computed.")


def _notification(tables, event, tenant, out) -> None:
    constraints = next((r for r in _table(tables, "12_Tenant_Constraints") if _norm(_field(r, "tenant_code")) == tenant), None)
    try:
        start = parse_time(str(_field(event, "alert_ts_utc")))
    except (TypeError, ValueError):
        start = None
    obligation = {"clock_starts_at": start.isoformat() if start else None, "clock_basis": "alert_ts_utc (receipt at Sentinel), not excursion start and not disposition",
                  "policy_version": POLICY_VERSION, "window": None, "due_at": None, "calendar_semantics": None, "status": "OPEN_UNFILED",
                  "signatory_policy": _field(constraints, "who_signs_a_disposition") if constraints else "",
                  "regulator_output_language": _field(constraints, "output_language") if constraints else "",
                  "note": "The prototype records the obligation and reminders only; it never files with a regulator and a reminder is not a receipt."}
    reportable = str(_field(event, "regulator_reportable")).strip().upper()
    window = str(_field(event, "reg_window_hours")).strip()
    if reportable == "N":
        obligation["status"] = "NOT_REPORTABLE_PER_RECORD"
        obligation["window"] = "Record marks the event not reportable; this is a provisional input and the tenant policy must confirm it."
    elif start and window:
        try:
            hours = float(window)
            obligation["window"] = f"{window} h (provisional; taken from the record, pending an approved tenant/jurisdiction policy)"
            obligation["due_at"] = (start + timedelta(hours=hours)).isoformat()
            obligation["calendar_semantics"] = "Fixed hours in UTC. Business-day or calendar-day windows need an explicit calendar and timezone policy that the pack does not contain."
        except ValueError:
            obligation["window"] = "Unparseable window on the record"
    else:
        obligation["window"] = "No window recorded; reportability unknown"
        obligation["status"] = "URGENT_POLICY_REVIEW"
        out["required_human_actions"].append("Regulatory affairs must confirm reportability and window from the approved policy; unknown is never 'not required'.")
    out["notification"] = obligation


def assess(tables: dict[str, Any], event_id: str, *, principal_tenant: str | None = None,
           known_at: str | datetime | None = None, corrections: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Assess one event. Raises ``AccessDenied`` when the principal's tenant does not own it."""
    event = next((e for e in _table(tables, "01_Excursion_Events") if _norm(_field(e, "event_id")) == _norm(event_id)), None)
    tenant = _norm(_field(event, "tenant_code")) if event else ""
    if event is None or (principal_tenant is not None and _norm(principal_tenant) != tenant):
        # Same answer for "not yours" and "does not exist" so existence does not leak across tenants.
        raise AccessDenied(f"Event {event_id!r} is not available to tenant {principal_tenant!r}")
    extracted = extract_date(tables)
    cutoff = parse_time(known_at) if known_at is not None else (extracted or parse_time(tables.get("_observed_at") or datetime.now(timezone.utc)))
    tables, applied = apply_corrections(tables, corrections or [], cutoff)
    event = next(e for e in _table(tables, "01_Excursion_Events") if _norm(_field(e, "event_id")) == _norm(event_id))
    try:
        when: datetime | None = parse_time(str(_field(event, "excursion_start_utc")))
    except (TypeError, ValueError):
        when = None

    out: dict[str, Any] = {
        "assessment_version": ASSESSMENT_VERSION, "event_id": str(_field(event, "event_id")), "tenant_code": tenant.upper(),
        "source_refs": [_ref("01_Excursion_Events", event)],
        "time_semantics": {"as_at": when.isoformat() if when else None, "as_at_basis": "excursion_start_utc (valid time)",
                           "known_at": cutoff.isoformat(), "known_at_basis": "workbook rows are treated as known at the pack extract date; alias confirmations, incident entries and corrections carry their own recorded time",
                           "extract_date": extracted.isoformat() if extracted else None, "interval_convention": "half-open [from, to); date-only bounds are flagged on the boundary day"},
        "inputs": {"event_fields_read": [f for f in ALLOWED_EVENT_FIELDS if f in event], "provisional_policy_fields": [f for f in PROVISIONAL_POLICY_FIELDS if f in event],
                   "historical_fields_excluded": [f for f in HISTORICAL_OUTCOME_FIELDS if f in event], "corrections_applied": applied},
        "entities": [], "evidence": {}, "conflicts": [], "missing_inputs": [], "required_human_actions": [], "notification": None,
    }
    products = _resolve_product(tables, event, tenant, cutoff, out)
    _resolve_facility(tables, str(_field(event, "origin_ref_as_received")), "origin", out)
    _resolve_facility(tables, str(_field(event, "dest_ref_as_received")), "destination", out)
    _resolve_carrier(tables, event, when, out)
    _sop_evidence(tables, tenant, when, out)
    _stability_evidence(tables, tenant, products, out)
    _telemetry_evidence(tables, event, cutoff, out)
    _notification(tables, event, tenant, out)
    for entity in out["entities"]:
        out["source_refs"].extend(entity.get("source_refs", []))
    out["source_refs"] = sorted(set(out["source_refs"]))
    out["missing_inputs"] = list(dict.fromkeys(out["missing_inputs"]))
    out["required_human_actions"] = list(dict.fromkeys(out["required_human_actions"] + [
        "A named, authorised human decides the disposition from verified source documents; this assessment is a reviewer aid."]))
    out["conclusion"] = {
        "disposition": "ABSTAIN",
        "readiness": "BLOCKED_BY_CONFLICTS" if out["conflicts"] else ("INCOMPLETE_EVIDENCE" if out["missing_inputs"] else "EVIDENCE_ASSEMBLED"),
        "statement": "No disposition is proposed. The assessment lists verified candidates, rejected evidence with reasons, open conflicts and the inputs a reviewer must obtain.",
    }
    out["manifest"] = {"code_version": __version__, "assessment_version": ASSESSMENT_VERSION, "policy_version": POLICY_VERSION,
                       "workbook_sha256": tables.get("_source_hash"), "python": sys.version.split()[0],
                       "corrections_sha256": canonical_hash(corrections or [])}
    out["assessment_sha256"] = canonical_hash(out)
    return out


def package(assessment: dict[str, Any]) -> dict[str, Any]:
    """Wrap an assessment as an evidence package with per-section digests."""
    sections = {name: canonical_hash(assessment[name]) for name in ("entities", "evidence", "conflicts", "missing_inputs", "notification", "manifest")}
    return {"package_version": "evidence-package-v1", "event_id": assessment["event_id"], "tenant_code": assessment["tenant_code"],
            "assessment": assessment, "section_sha256": sections, "package_sha256": canonical_hash({"assessment": assessment["assessment_sha256"], "sections": sections})}


def verify_package(bundle: dict[str, Any]) -> bool:
    assessment = bundle["assessment"]
    body = {k: v for k, v in assessment.items() if k != "assessment_sha256"}
    if canonical_hash(body) != assessment.get("assessment_sha256"):
        return False
    sections = {name: canonical_hash(assessment[name]) for name in bundle["section_sha256"]}
    return sections == bundle["section_sha256"] and bundle["package_sha256"] == canonical_hash({"assessment": assessment["assessment_sha256"], "sections": sections})
