"""Generate a small, fully synthetic Sentinel workbook for demos and tests."""

from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo
from xml.etree import ElementTree as ET

SAMPLE_TENANTS = ("DEMO-ALPHA", "DEMO-BETA")
SAMPLE_EVENT_COUNT = 12

MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
OFFICE_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PACKAGE_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CONTENT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
XML_NS = "http://www.w3.org/XML/1998/namespace"

ET.register_namespace("", MAIN_NS)
ET.register_namespace("r", OFFICE_REL_NS)

SHEET_HEADERS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("00_README", ("field", "value")),
    (
        "01_Excursion_Events",
        (
            "event_id", "alert_ts_utc", "tenant_code", "shipment_ref", "leg_no", "source_system",
            "logger_id", "logger_vendor", "logger_fw", "product_ref_as_received", "origin_ref_as_received",
            "dest_ref_as_received", "lane_text", "carrier_ref_as_received", "mode", "excursion_start_utc",
            "excursion_end_utc", "duration_min", "min_temp_c", "max_temp_c", "mean_temp_c",
            "spec_text_as_received", "readings_in_window", "gateway_gap_min", "interpolated",
            "dock_door_open_flag", "prior_excursions_lane_90d", "consignment_value_usd", "case_opened",
            "triage_outcome", "rules_engine_recommendation", "final_disposition", "reviewer_id",
            "review_minutes", "systems_opened", "reviewer_overrode", "days_to_disposition",
            "regulator_reportable", "reg_window_hours", "hours_to_notification", "reported_within_window",
            "reopened_later", "notes",
        ),
    ),
    (
        "02_Product_Master",
        (
            "erp_source", "tenant_code", "brand_as_labelled", "generic_inn", "internal_sku", "gtin",
            "legacy_code", "storage_spec_text", "mkt_tolerance_text", "permitted_excursion_text",
            "stability_study_ref", "light_sensitive", "last_updated",
        ),
    ),
    (
        "03_Facility_Registry",
        (
            "source_system", "record_id", "name_in_source", "code_in_source", "country", "timezone_in_source",
            "cold_rooms", "gmp_licence_ref", "bms_room_tags", "record_created", "active",
        ),
    ),
    (
        "04_Carrier_Contracts",
        (
            "contract_id", "counterparty_legal_entity", "names_seen_on_documents", "parent_of", "effective_from",
            "effective_to", "governing_law", "cold_chain_clause", "liability_summary", "liability_cap",
            "claim_window_days", "amendment_docs",
        ),
    ),
    (
        "05_SOP_Index",
        (
            "doc_id", "tenant_code", "title", "revision", "effective_from", "effective_to", "supersedes_text",
            "applies_to_facilities_text", "format", "pages", "language", "acceptance_limits_location",
        ),
    ),
    (
        "06_Stability_Index",
        (
            "study_ref", "product_text_as_written", "tenant_code", "study_type", "temps_tested_text",
            "duration_tested", "outcome_text", "permitted_excursion_text", "file_path_text", "pages",
            "indexed_by", "readable",
        ),
    ),
    (
        "07_Alias_Observations",
        (
            "entity_kind", "string_a", "string_b", "same_real_world_thing", "times_seen_a", "times_seen_b",
            "confirmed_by", "confirmed_on", "comment",
        ),
    ),
    (
        "08_Reviewer_Queue_Log",
        (
            "log_id", "case_ref", "reviewer_id", "reviewer_region", "reviewer_utc_offset", "local_start",
            "local_end", "active_minutes", "systems_opened", "systems_list", "action", "queue_wait_hours",
            "interrupted_count", "shift",
        ),
    ),
    ("09_Override_Reasons", ("case_ref", "reviewer_id", "engine_said", "reviewer_decided", "verbatim_reason")),
    (
        "10_Reviewer_Questions",
        ("#", "question_as_asked", "where_the_answer_lives_today", "typical_minutes", "how_often_needed"),
    ),
    (
        "11_Systems_Inventory",
        (
            "system_id", "system", "what_it_holds", "access_method", "freshness", "rate_limit",
            "ordering_and_backfill", "measured_availability", "known_problems",
        ),
    ),
    (
        "12_Tenant_Constraints",
        (
            "tenant_code", "tenant_name", "country", "region", "shipments_per_month", "data_residency_position",
            "third_party_model_apis", "who_signs_a_disposition", "output_language", "sop_ownership", "other",
        ),
    ),
    ("13_Volume_And_Cost", ("metric", "value", "unit", "notes")),
    ("14_Incident_Log", ("ref", "date", "title", "severity", "what_happened", "consequence")),
)


def _event_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    reportable_windows = (24, 48, 24, 24, 48, 24, 72, 24, 48, 24, 48, 72)
    for index in range(1, SAMPLE_EVENT_COUNT + 1):
        tenant = SAMPLE_TENANTS[0] if index <= 6 else SAMPLE_TENANTS[1]
        day = (index - 1) * 2 + 1
        reportable = index not in (4, 10)
        row = {
            "event_id": f"DEMO-EVT-{index:03d}",
            "alert_ts_utc": f"2026-01-{day:02d} 08:00",
            "tenant_code": tenant,
            "shipment_ref": f"DEMO-SHIP-{index:03d}",
            "leg_no": "01",
            "source_system": "DEMO-MONITOR",
            "logger_id": f"DEMO-LOGGER-{index:03d}",
            "logger_vendor": "Demo Instruments",
            "logger_fw": "DEMO-FW-1",
            "product_ref_as_received": "Demo Serum syringe",
            "origin_ref_as_received": "DEMO-ORIGIN-01",
            "dest_ref_as_received": "DEMO-DEST-01",
            "lane_text": "Demo lane, ambient-to-cold transfer",
            "carrier_ref_as_received": "DEMO-CARRIER-01",
            "mode": "road",
            "excursion_start_utc": f"2026-01-{day:02d} 06:00",
            "excursion_end_utc": f"2026-01-{day:02d} 07:00",
            "duration_min": "60",
            "min_temp_c": "2.1",
            "max_temp_c": "9.4",
            "mean_temp_c": "5.7",
            "spec_text_as_received": "Demo storage range: 2-8 C",
            "readings_in_window": "12",
            "gateway_gap_min": "0",
            "interpolated": "N",
            "dock_door_open_flag": "N",
            "prior_excursions_lane_90d": "0",
            "consignment_value_usd": "100.00",
            "case_opened": "Y",
            "triage_outcome": "Pending evidence review",
            "rules_engine_recommendation": "Review required",
            "final_disposition": "",
            "reviewer_id": "",
            "review_minutes": "",
            "systems_opened": "",
            "reviewer_overrode": "N",
            "days_to_disposition": "",
            "regulator_reportable": "Y" if reportable else "N",
            "reg_window_hours": str(reportable_windows[index - 1]) if reportable else "",
            "hours_to_notification": "",
            "reported_within_window": "",
            "reopened_later": "N",
            "notes": "Synthetic training record; not a real shipment or disposition.",
        }
        if index in (2, 8):
            row["gateway_gap_min"] = "15"
        if index == 3:
            row["interpolated"] = "Y"
        if index == 5:
            row["product_ref_as_received"] = ""
        if index == 9:
            row["readings_in_window"] = "0"
        rows.append(row)
    return rows


def _workbook_rows() -> dict[str, list[dict[str, str]]]:
    events = _event_rows()
    products = [
        {
            "erp_source": "DEMO-ERP",
            "tenant_code": tenant,
            "brand_as_labelled": "Demo Serum syringe",
            "generic_inn": "Demo compound",
            "internal_sku": "00001234",
            "gtin": "00000000000101",
            "legacy_code": "0007-DEMO",
            "storage_spec_text": "2-8 C",
            "mkt_tolerance_text": "Synthetic example only",
            "permitted_excursion_text": "Requires case-specific review",
            "stability_study_ref": "DEMO-STUDY-1",
            "light_sensitive": "N",
            "last_updated": "2026-01-01",
        }
        for tenant in SAMPLE_TENANTS
    ]
    stability = [
        {
            "study_ref": "DEMO-STUDY-1",
            "product_text_as_written": "Demo Serum vial" if tenant == SAMPLE_TENANTS[1] else "Demo Serum syringe",
            "tenant_code": tenant,
            "study_type": "Synthetic summary",
            "temps_tested_text": "2-8 C",
            "duration_tested": "24 hours",
            "outcome_text": "Index only; verification required",
            "permitted_excursion_text": "Not established by this fixture",
            "file_path_text": "",
            "pages": "",
            "indexed_by": "DEMO-INDEXER",
            "readable": "N",
        }
        for tenant in SAMPLE_TENANTS
    ]
    sops = [
        {
            "doc_id": f"DEMO-SOP-{tenant.removeprefix('DEMO-')}",
            "tenant_code": tenant,
            "title": "Demo excursion triage procedure",
            "revision": "1",
            "effective_from": "2025-01-01",
            "effective_to": "",
            "supersedes_text": "",
            "applies_to_facilities_text": "All demo facilities",
            "format": "Synthetic index row",
            "pages": "1",
            "language": "English",
            "acceptance_limits_location": "Not supplied",
        }
        for tenant in SAMPLE_TENANTS
    ]
    constraints = [
        {
            "tenant_code": SAMPLE_TENANTS[0],
            "tenant_name": "Demo Alpha",
            "country": "ZZ",
            "region": "Demo Region A",
            "shipments_per_month": "20",
            "data_residency_position": "Synthetic fixture",
            "third_party_model_apis": "N",
            "who_signs_a_disposition": "Named individual signer",
            "output_language": "English",
            "sop_ownership": "Demo Alpha",
            "other": "Synthetic tenant policy.",
        },
        {
            "tenant_code": SAMPLE_TENANTS[1],
            "tenant_name": "Demo Beta",
            "country": "ZZ",
            "region": "Demo Region B",
            "shipments_per_month": "20",
            "data_residency_position": "Synthetic fixture",
            "third_party_model_apis": "N",
            "who_signs_a_disposition": "Site QA + Corporate QA (dual)",
            "output_language": "English",
            "sop_ownership": "Demo Beta",
            "other": "Synthetic tenant policy.",
        },
    ]
    records: dict[str, list[dict[str, str]]] = {
        "00_README": [
            {"field": "Purpose", "value": "Synthetic demo fixture; all records are fictional."},
            {"field": "Date range", "value": "2026-01"},
        ],
        "01_Excursion_Events": events,
        "02_Product_Master": products,
        "03_Facility_Registry": [
            {
                "source_system": "DEMO-FACILITY-SYSTEM",
                "record_id": "DEMO-FAC-01",
                "name_in_source": "Demo Facility",
                "code_in_source": "0001",
                "country": "ZZ",
                "timezone_in_source": "UTC",
                "cold_rooms": "1",
                "gmp_licence_ref": "DEMO-LICENCE-01",
                "bms_room_tags": "DEMO-ROOM-01",
                "record_created": "2026-01-01",
                "active": "Y",
            }
        ],
        "04_Carrier_Contracts": [
            {
                "contract_id": "DEMO-CONTRACT-01",
                "counterparty_legal_entity": "Demo Carrier Ltd",
                "names_seen_on_documents": "Demo Carrier",
                "parent_of": "",
                "effective_from": "2025-01-01",
                "effective_to": "",
                "governing_law": "Demo jurisdiction",
                "cold_chain_clause": "Synthetic clause; not legal advice",
                "liability_summary": "Not applicable to real parties",
                "liability_cap": "0",
                "claim_window_days": "30",
                "amendment_docs": "",
            }
        ],
        "05_SOP_Index": sops,
        "06_Stability_Index": stability,
        "07_Alias_Observations": [
            {
                "entity_kind": "product",
                "string_a": "Demo Serum syringe",
                "string_b": "Demo Serum",
                "same_real_world_thing": "Unknown",
                "times_seen_a": "1",
                "times_seen_b": "1",
                "confirmed_by": "",
                "confirmed_on": "",
                "comment": "Synthetic observation; not an identity assertion.",
            }
        ],
        "08_Reviewer_Queue_Log": [
            {
                "log_id": "DEMO-QUEUE-01",
                "case_ref": "DEMO-EVT-001",
                "reviewer_id": "DEMO-REVIEWER-01",
                "reviewer_region": "Demo Region A",
                "reviewer_utc_offset": "+00:00",
                "local_start": "2026-01-01 08:00",
                "local_end": "2026-01-01 08:05",
                "active_minutes": "5",
                "systems_opened": "1",
                "systems_list": "DEMO-MONITOR",
                "action": "Synthetic queue entry",
                "queue_wait_hours": "0",
                "interrupted_count": "0",
                "shift": "Demo shift",
            }
        ],
        "09_Override_Reasons": [
            {
                "case_ref": "DEMO-EVT-002",
                "reviewer_id": "DEMO-REVIEWER-01",
                "engine_said": "Review required",
                "reviewer_decided": "Pending",
                "verbatim_reason": "Synthetic example; no real adjudication.",
            }
        ],
        "10_Reviewer_Questions": [
            {
                "#": "1",
                "question_as_asked": "Which evidence is missing?",
                "where_the_answer_lives_today": "Demo evidence index",
                "typical_minutes": "5",
                "how_often_needed": "Synthetic example",
            }
        ],
        "11_Systems_Inventory": [
            {
                "system_id": "DEMO-SYSTEM-01",
                "system": "Demo monitoring system",
                "what_it_holds": "Synthetic logger observations",
                "access_method": "Local fixture",
                "freshness": "Static",
                "rate_limit": "Not applicable",
                "ordering_and_backfill": "Not applicable",
                "measured_availability": "Not measured",
                "known_problems": "Synthetic gaps may be present.",
            }
        ],
        "12_Tenant_Constraints": constraints,
        "13_Volume_And_Cost": [
            {"metric": "Synthetic fixture count", "value": "12", "unit": "events", "notes": "Not real operating volume."}
        ],
        "14_Incident_Log": [
            {
                "ref": "DEMO-INC-01",
                "date": "2026-01-01",
                "title": "Synthetic telemetry gap",
                "severity": "Demo",
                "what_happened": "A sample event includes a telemetry gap.",
                "consequence": "Evidence remains pending review.",
            }
        ],
    }
    return records


def _column_name(number: int) -> str:
    name = ""
    while number:
        number, remainder = divmod(number - 1, 26)
        name = chr(65 + remainder) + name
    return name


def _worksheet_xml(headers: tuple[str, ...], rows: list[dict[str, str]]) -> bytes:
    worksheet = ET.Element(f"{{{MAIN_NS}}}worksheet")
    sheet_data = ET.SubElement(worksheet, f"{{{MAIN_NS}}}sheetData")
    for row_number in range(1, len(rows) + 2):
        row_element = ET.SubElement(sheet_data, f"{{{MAIN_NS}}}row", {"r": str(row_number)})
        for column_number, header in enumerate(headers, start=1):
            value = header if row_number == 1 else rows[row_number - 2].get(header, "")
            cell = ET.SubElement(
                row_element,
                f"{{{MAIN_NS}}}c",
                {"r": f"{_column_name(column_number)}{row_number}", "t": "inlineStr"},
            )
            inline = ET.SubElement(cell, f"{{{MAIN_NS}}}is")
            text = ET.SubElement(inline, f"{{{MAIN_NS}}}t")
            text.text = str(value)
            if text.text and (text.text[0].isspace() or text.text[-1].isspace()):
                text.set(f"{{{XML_NS}}}space", "preserve")
    return ET.tostring(worksheet, encoding="utf-8", xml_declaration=True)


def _workbook_parts() -> dict[str, bytes]:
    root_rels = ET.Element(f"{{{PACKAGE_REL_NS}}}Relationships")
    ET.SubElement(
        root_rels,
        f"{{{PACKAGE_REL_NS}}}Relationship",
        {
            "Id": "rId1",
            "Type": f"{OFFICE_REL_NS}/officeDocument",
            "Target": "xl/workbook.xml",
        },
    )

    workbook = ET.Element(f"{{{MAIN_NS}}}workbook")
    sheets = ET.SubElement(workbook, f"{{{MAIN_NS}}}sheets")
    for index, (name, _) in enumerate(SHEET_HEADERS, start=1):
        ET.SubElement(
            sheets,
            f"{{{MAIN_NS}}}sheet",
            {"name": name, "sheetId": str(index), f"{{{OFFICE_REL_NS}}}id": f"rId{index}"},
        )

    workbook_rels = ET.Element(f"{{{PACKAGE_REL_NS}}}Relationships")
    for index in range(1, len(SHEET_HEADERS) + 1):
        ET.SubElement(
            workbook_rels,
            f"{{{PACKAGE_REL_NS}}}Relationship",
            {
                "Id": f"rId{index}",
                "Type": f"{OFFICE_REL_NS}/worksheet",
                "Target": f"worksheets/sheet{index}.xml",
            },
        )

    content_types = ET.Element(f"{{{CONTENT_NS}}}Types")
    ET.SubElement(
        content_types,
        f"{{{CONTENT_NS}}}Default",
        {"Extension": "rels", "ContentType": "application/vnd.openxmlformats-package.relationships+xml"},
    )
    ET.SubElement(content_types, f"{{{CONTENT_NS}}}Default", {"Extension": "xml", "ContentType": "application/xml"})
    ET.SubElement(
        content_types,
        f"{{{CONTENT_NS}}}Override",
        {
            "PartName": "/xl/workbook.xml",
            "ContentType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml",
        },
    )
    for index in range(1, len(SHEET_HEADERS) + 1):
        ET.SubElement(
            content_types,
            f"{{{CONTENT_NS}}}Override",
            {
                "PartName": f"/xl/worksheets/sheet{index}.xml",
                "ContentType": "application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml",
            },
        )

    parts = {
        "[Content_Types].xml": ET.tostring(content_types, encoding="utf-8", xml_declaration=True),
        "_rels/.rels": ET.tostring(root_rels, encoding="utf-8", xml_declaration=True),
        "xl/workbook.xml": ET.tostring(workbook, encoding="utf-8", xml_declaration=True),
        "xl/_rels/workbook.xml.rels": ET.tostring(workbook_rels, encoding="utf-8", xml_declaration=True),
    }
    records = _workbook_rows()
    for index, (name, headers) in enumerate(SHEET_HEADERS, start=1):
        parts[f"xl/worksheets/sheet{index}.xml"] = _worksheet_xml(headers, records[name])
    return parts


def create_workbook(path: str | Path) -> Path:
    """Write and return a deterministic XLSX containing only fictional demo records."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(destination, "w", compression=ZIP_DEFLATED) as archive:
        for name, contents in _workbook_parts().items():
            info = ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            archive.writestr(info, contents)
    return destination
