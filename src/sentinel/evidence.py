"""Fail-closed evidence candidate analysis for Sentinel excursion cases."""

from __future__ import annotations

from datetime import date, datetime, time, timezone
from typing import Any

RULES_VERSION = "evidence-v1"


def parse_time(value: str | date | datetime) -> datetime:
    """Parse workbook or ISO date/time text as an aware UTC datetime."""
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, date):
        parsed = datetime.combine(value, time.min)
    elif isinstance(value, str):
        text = value.strip()
        if not text:
            raise ValueError("Time value is blank")
        if text.endswith(("Z", "z")):
            text = text[:-1] + "+00:00"
        parsed = None
        try:
            parsed = datetime.fromisoformat(text)
        except ValueError:
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
                try:
                    parsed = datetime.strptime(text, fmt)
                    break
                except ValueError:
                    pass
        if parsed is None:
            raise ValueError(f"Invalid time value: {value!r}")
    else:
        raise TypeError("Time value must be a string, date, or datetime")
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _norm(value: Any) -> str:
    return str(value).strip().casefold() if value is not None else ""


def _field(row: dict[str, Any], *names: str) -> Any:
    normalized = {_norm(key): value for key, value in row.items()}
    for name in names:
        key = _norm(name)
        if key in normalized and normalized[key] is not None and str(normalized[key]).strip():
            return normalized[key]
    return ""


def _table(tables: dict[str, Any], *names: str) -> list[dict[str, Any]]:
    indexed = {_norm(name).replace(" ", "_"): rows for name, rows in tables.items()}
    for name in names:
        key = _norm(name).replace(" ", "_")
        if key in indexed and isinstance(indexed[key], list):
            return [row for row in indexed[key] if isinstance(row, dict)]
    return []


def _valid_start(value: Any) -> datetime | None:
    if value is None or not str(value).strip():
        return None
    try:
        return parse_time(str(value))
    except (TypeError, ValueError):
        return None


def _effective(row: dict[str, Any], when: datetime) -> bool:
    start = _valid_start(_field(row, "effective_from"))
    end_raw = _field(row, "effective_to")
    end = _valid_start(end_raw) if str(end_raw).strip() else None
    if start is None or (str(end_raw).strip() and end is None):
        return False
    return start <= when and (end is None or when < end)


def sops_as_at(
    tables: dict[str, Any], tenant: str, valid_at: str | date | datetime, known_at: str | date | datetime | None = None
) -> list[dict[str, Any]]:
    """Return same-tenant SOP index rows valid at a time and visible by snapshot time."""
    if known_at is not None and (not tables.get("_observed_at") or parse_time(known_at) < parse_time(tables["_observed_at"])):
        return []
    when = parse_time(valid_at)
    wanted_tenant = _norm(tenant)
    return [
        row
        for row in _table(tables, "05_SOP_Index", "SOP_Index", "sops")
        if _norm(_field(row, "tenant_code")) == wanted_tenant and _effective(row, when)
    ]


def _same_tenant(row: dict[str, Any], tenant: str) -> bool:
    return bool(tenant) and _norm(_field(row, "tenant_code")) == _norm(tenant)


def _presentation(text: Any) -> set[str]:
    value = _norm(text)
    groups = {
        "syringe": ("syringe", "pfs", "pre-filled", "prefilled"),
        "vial": ("vial",),
        "pen": ("pen",),
        "cartridge": ("cartridge",),
        "ampoule": ("ampoule", "ampule"),
        "bottle": ("bottle",),
        "tablet": ("tablet",),
        "capsule": ("capsule",),
    }
    return {presentation for presentation, terms in groups.items() if any(term in value for term in terms)}


def _truthy(value: Any) -> bool:
    return _norm(value) in {"y", "yes", "true", "1", "t"}


def _number(value: Any) -> float | None:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def analyze(tables: dict[str, Any], event: dict[str, Any]) -> dict[str, Any]:
    """Return candidate source rows and blockers, never an adjudication."""
    blockers: list[str] = []

    def block(message: str) -> None:
        if message not in blockers:
            blockers.append(message)

    tenant = str(_field(event, "tenant_code") or "")
    identifier_fields = ("brand_as_labelled", "internal_sku", "gtin", "legacy_code")
    identifiers = {_norm(_field(event, name)) for name in (
        "product_ref_as_received", "product_ref", "brand_as_labelled", "internal_sku", "gtin", "legacy_code"
    )}
    identifiers.discard("")

    products = _table(tables, "02_Product_Master", "Product_Master", "products")
    product_candidates = [
        dict(row) for row in products
        if _same_tenant(row, tenant)
        and identifiers.intersection({_norm(_field(row, field)) for field in identifier_fields} - {""})
    ]
    if not identifiers:
        block("Product identifier is missing from the event.")
    elif not product_candidates:
        block("No exact tenant-scoped product identifier match was found.")
    elif len(product_candidates) > 1:
        block("Product identifier is ambiguous across multiple tenant-scoped master rows.")
    block("Product master is a historical snapshot without bitemporal validity; it cannot establish the product record as of the excursion.")

    excursion_start = _field(event, "excursion_start_utc", "excursion_start")
    when: datetime | None = None
    try:
        when = parse_time(str(excursion_start))
    except (TypeError, ValueError):
        block("Excursion start time is missing or invalid; applicable SOPs cannot be selected.")

    sop_candidates = sops_as_at(tables, tenant, when) if tenant and when else []
    if not sop_candidates:
        block("No same-tenant SOP index row is valid at the excursion start.")
    docs: dict[str, int] = {}
    for row in sop_candidates:
        doc_id = _norm(_field(row, "doc_id"))
        if doc_id:
            docs[doc_id] = docs.get(doc_id, 0) + 1
    for doc_id, count in docs.items():
        if count > 1:
            block(f"Overlapping SOP revisions are indexed for document {doc_id} at the excursion start.")
    if any("site-specific" in _norm(_field(row, "applies_to_facilities_text")) for row in sop_candidates):
        block("Applicable site-specific SOP annex or facility evidence is not supplied.")

    study_refs = {_norm(_field(row, "stability_study_ref")) for row in product_candidates}
    study_refs.discard("")
    stability_rows = _table(tables, "06_Stability_Index", "Stability_Index", "stability")
    stability_candidates = [
        dict(row) for row in stability_rows
        if _same_tenant(row, tenant) and _norm(_field(row, "study_ref")) in study_refs
    ]
    if not study_refs:
        block("A stability study reference is missing from the matched product master row.")
    elif not stability_candidates:
        block("No same-tenant stability index row matches the product study reference exactly.")
    for row in stability_candidates:
        readable = _field(row, "readable")
        if not _truthy(readable):
            block(f"Stability source {str(_field(row, 'study_ref'))} is marked unreadable or has no readability confirmation.")
        product_names = {_norm(_field(product, "brand_as_labelled")) for product in product_candidates}
        product_names.discard("")
        product_presentations = set().union(*(_presentation(name) for name in product_names)) if product_names else set()
        study_presentations = _presentation(_field(row, "product_text_as_written"))
        unexpected_presentations = study_presentations - product_presentations
        if product_presentations and study_presentations and unexpected_presentations:
            unexpected = ", ".join(sorted(unexpected_presentations))
            block(
                f"Stability index has unexpected or conflicting presentation tag(s) {unexpected} "
                f"relative to the product master for study {str(_field(row, 'study_ref'))}."
            )
    block("Full stability report source documents are not supplied; an index row does not verify study findings or applicability.")
    block("Full source SOP documents and any applicable annexes are not supplied; index metadata is not authoritative procedure evidence.")

    firmware = _field(event, "logger_fw", "firmware")
    if _norm(firmware):
        block("Logger firmware and calibration records require source verification before telemetry can be relied upon.")

    gap = _number(_field(event, "gateway_gap_min", "telemetry_gap_min"))
    if gap is not None and gap > 0:
        block("Telemetry contains a gateway gap; complete raw logger and gateway records are required.")
    if _truthy(_field(event, "interpolated", "telemetry_interpolated")):
        block("Telemetry includes interpolated readings; original readings must be verified.")
    readings = _number(_field(event, "readings_in_window"))
    if readings is None or readings <= 0:
        block("Telemetry reading count is missing or non-positive.")

    batch_exposure = _field(event, "batch_exposure_record", "cumulative_batch_exposure", "batch_exposure_ref")
    if not str(batch_exposure).strip():
        block("No cumulative exposure record linked to the affected batch is supplied.")

    # The workbook supplies indexes and historical case outcomes, not primary evidence.
    block("Required primary source documents and records are not available in the supplied workbook; candidate rows are not verification.")

    source_refs: list[str] = []
    event_id = _field(event, "event_id")
    if str(event_id).strip():
        source_refs.append(f"event:{str(event_id).strip()}")
    for row in product_candidates:
        value = _field(row, "internal_sku", "gtin", "legacy_code", "brand_as_labelled")
        source_refs.append(f"product:{str(value).strip()}#row={row.get('_row', '')}")
    for row in sop_candidates:
        value = _field(row, "doc_id")
        source_refs.append(f"sop:{str(value).strip()}:{str(_field(row, 'revision')).strip()}#row={row.get('_row', '')}")
    for row in stability_candidates:
        value = _field(row, "study_ref")
        source_refs.append(f"stability:{str(value).strip()}#row={row.get('_row', '')}")

    return {
        "status": "WAITING_EVIDENCE",
        "blockers": blockers,
        "product_candidates": product_candidates,
        "sop_candidates": [dict(row) for row in sop_candidates],
        "stability_candidates": stability_candidates,
        "source_refs": source_refs,
        "rules_version": RULES_VERSION,
    }
