"""Unit tests for the assessment kernel on small, clearly fictional tables."""
import json
import unittest

from sentinel.evidence.assessment import AccessDenied, apply_corrections, assess, package, verify_package
from sentinel.evidence.analysis import parse_time


def tables(**overrides):
    """Fictional snapshot with one alert per interesting shape. Rows carry `_row` like the workbook reader."""
    base = {
        "00_README": [{"Pack": "Extract date", "_col_2": "2026-09-14", "_row": 6}],
        "01_Excursion_Events": [
            {"event_id": "FX-1", "alert_ts_utc": "2026-05-02 10:00", "excursion_start_utc": "2026-05-02 09:30", "tenant_code": "T-ONE",
             "product_ref_as_received": "SKU-SHARED-1", "origin_ref_as_received": "SITE-A", "dest_ref_as_received": "SITE-B",
             "carrier_ref_as_received": "ACME", "source_system": "SYS-01", "logger_id": "LG-1", "logger_fw": "TT-9.9.9",
             "gateway_gap_min": "0", "interpolated": "N", "readings_in_window": "12", "regulator_reportable": "Y", "reg_window_hours": "72",
             "final_disposition": "RELEASE", "reviewer_overrode": "N", "_row": 2},
            {"event_id": "FX-2", "alert_ts_utc": "2026-05-02 10:00", "excursion_start_utc": "2026-05-02 09:30", "tenant_code": "T-TWO",
             "product_ref_as_received": "SKU-SHARED-1", "origin_ref_as_received": "SITE-A", "dest_ref_as_received": "",
             "carrier_ref_as_received": "ACME", "source_system": "SYS-03", "logger_id": "LG-2", "logger_fw": "TT-1.0.0",
             "gateway_gap_min": "0", "interpolated": "N", "readings_in_window": "12", "regulator_reportable": "N", "reg_window_hours": "", "_row": 3},
            {"event_id": "FX-3", "alert_ts_utc": "2026-06-01 00:10", "excursion_start_utc": "2026-06-01 00:00", "tenant_code": "T-ONE",
             "product_ref_as_received": "Brandname Pen", "origin_ref_as_received": "SITE-Z", "dest_ref_as_received": "",
             "carrier_ref_as_received": "ACME", "source_system": "SYS-01", "logger_id": "LG-3", "logger_fw": "TT-9.9.9",
             "gateway_gap_min": "0", "interpolated": "N", "readings_in_window": "12", "regulator_reportable": "", "reg_window_hours": "", "_row": 4},
        ],
        "02_Product_Master": [
            {"tenant_code": "T-ONE", "brand_as_labelled": "Alpha 10mg PFS", "internal_sku": "SKU-SHARED-1", "gtin": "", "legacy_code": "",
             "stability_study_ref": "STB-1", "_row": 2},
            {"tenant_code": "T-TWO", "brand_as_labelled": "Beta 10mg vial", "internal_sku": "SKU-SHARED-1", "gtin": "", "legacy_code": "",
             "stability_study_ref": "STB-2", "_row": 3},
            {"tenant_code": "T-ONE", "brand_as_labelled": "Brand Pen 3mL", "internal_sku": "SKU-PEN", "gtin": "", "legacy_code": "",
             "stability_study_ref": "", "_row": 4},
        ],
        "03_Facility_Registry": [
            {"source_system": "SYS-04", "record_id": "R-1", "name_in_source": "Site A", "code_in_source": "SITE-A", "timezone_in_source": "Europe/Amsterdam", "cold_rooms": "2", "_row": 2},
            {"source_system": "SYS-07", "record_id": "R-2", "name_in_source": "Site A", "code_in_source": "SITE-A", "timezone_in_source": "Asia/Kolkata", "cold_rooms": "2", "_row": 3},
            {"source_system": "SYS-04", "record_id": "R-3", "name_in_source": "Site B", "code_in_source": "SITE-B", "timezone_in_source": "Europe/Berlin", "cold_rooms": "1", "_row": 4},
        ],
        "04_Carrier_Contracts": [
            {"contract_id": "C-1", "counterparty_legal_entity": "Acme Logistics Ltd", "names_seen_on_documents": "ACME | Acme Logistics", "parent_of": "",
             "effective_from": "2025-01-01", "effective_to": "", "claim_window_days": "30", "liability_cap": "USD 1", "_row": 2},
            {"contract_id": "C-2", "counterparty_legal_entity": "Acme Logistics GmbH", "names_seen_on_documents": "ACME | Acme DE", "parent_of": "",
             "effective_from": "2025-01-01", "effective_to": "", "claim_window_days": "21", "liability_cap": "None", "_row": 3},
        ],
        "05_SOP_Index": [
            {"doc_id": "SOP-ONE-1", "tenant_code": "T-ONE", "title": "Excursions", "revision": "Rev 01", "effective_from": "2025-01-01", "effective_to": "2026-06-01",
             "applies_to_facilities_text": "All sites", "format": "Native PDF", "language": "en", "_row": 2},
            {"doc_id": "SOP-ONE-1", "tenant_code": "T-ONE", "title": "Excursions", "revision": "Rev 02", "effective_from": "2026-05-01", "effective_to": "",
             "applies_to_facilities_text": "Site-specific — see Annexure 1", "format": "Scanned PDF", "language": "en", "_row": 3},
            {"doc_id": "SOP-ONE-2", "tenant_code": "T-ONE", "title": "Other", "revision": "Rev 01", "effective_from": "2026-06-01", "effective_to": "",
             "applies_to_facilities_text": "All sites", "format": "Native PDF", "language": "en", "_row": 4},
            {"doc_id": "SOP-TWO-1", "tenant_code": "T-TWO", "title": "Excursions", "revision": "Rev 01", "effective_from": "2025-01-01", "effective_to": "",
             "applies_to_facilities_text": "All sites", "format": "Native PDF", "language": "en", "_row": 5},
        ],
        "06_Stability_Index": [
            {"study_ref": "STB-1", "product_text_as_written": "Alpha 10mg PFS — vial", "tenant_code": "T-ONE", "study_type": "Excursion",
             "permitted_excursion_text": "24 h at 25 °C", "file_path_text": "/stability/T-ONE/STB-1.pdf", "readable": "Y", "_row": 2},
            {"study_ref": "STB-2", "product_text_as_written": "Beta 10mg vial — vial", "tenant_code": "T-ONE", "study_type": "Long-term",
             "permitted_excursion_text": "", "file_path_text": "/stability/T-TWO/STB-2.pdf", "readable": "N — scan of scan", "_row": 3},
        ],
        "07_Alias_Observations": [
            {"entity_kind": "PRODUCT", "string_a": "Brandname Pen", "string_b": "SKU-PEN", "same_real_world_thing": "Y", "confirmed_by": "QA-1", "confirmed_on": "2026-03-01", "_row": 2},
            {"entity_kind": "PRODUCT", "string_a": "Brandname Pen", "string_b": "SKU-SHARED-1", "same_real_world_thing": "Y", "confirmed_by": "QA-1", "confirmed_on": "2026-09-30", "_row": 3},
        ],
        "12_Tenant_Constraints": [
            {"tenant_code": "T-ONE", "who_signs_a_disposition": "QA Head", "output_language": "English", "_row": 2},
            {"tenant_code": "T-TWO", "who_signs_a_disposition": "Site QA + Corporate QA (dual)", "output_language": "Portuguese (pt-BR)", "_row": 3},
        ],
        "14_Incident_Log": [
            {"ref": "INC-X", "date": "2026-04-11", "title": "Calibration bulletin", "severity": "P2",
             "what_happened": "Vendor issued calibration bulletin TT-CB-999: firmware build TT-9.9.9 under-reported by up to 1.8 °C.", "consequence": "", "_row": 2},
        ],
        "_observed_at": "2026-11-01T00:00:00+00:00", "_source_hash": "fixture",
    }
    base.update(overrides)
    return base


def entity(result, kind, role=None):
    return next(e for e in result["entities"] if e["kind"] == kind and (role is None or e.get("role") == role))


class AssessmentTests(unittest.TestCase):
    def test_same_identifier_under_two_tenants_resolves_only_within_tenant(self):
        one = assess(tables(), "FX-1", principal_tenant="T-ONE")
        two = assess(tables(), "FX-2", principal_tenant="T-TWO")
        self.assertEqual(entity(one, "PRODUCT")["candidates"][0]["source_ref"], "02_Product_Master#row=2")
        self.assertEqual(entity(two, "PRODUCT")["candidates"][0]["source_ref"], "02_Product_Master#row=3")

    def test_cross_tenant_access_is_indistinguishable_from_missing(self):
        with self.assertRaises(AccessDenied) as wrong:
            assess(tables(), "FX-1", principal_tenant="T-TWO")
        with self.assertRaises(AccessDenied) as absent:
            assess(tables(), "FX-404", principal_tenant="T-TWO")
        self.assertEqual(type(wrong.exception), type(absent.exception))

    def test_misleading_file_path_does_not_transfer_ownership(self):
        # STB-2 sits in a T-TWO folder but is owned by T-ONE; T-TWO's product cites it and must not get it.
        two = assess(tables(), "FX-2")
        self.assertEqual(two["evidence"]["stability"]["candidates"], [])
        self.assertIn("another tenant", two["evidence"]["stability"]["rejected"][0]["reason"])

    def test_wrong_presentation_is_a_conflict_not_a_match(self):
        one = assess(tables(), "FX-1")
        self.assertTrue(any("Presentation mismatch" in f for c in one["evidence"]["stability"]["candidates"] for f in c["flags"]))
        self.assertFalse(one["evidence"]["stability"]["candidates"][0]["usable"])
        self.assertEqual(one["conclusion"]["readiness"], "BLOCKED_BY_CONFLICTS")

    def test_missing_and_unreadable_stability_evidence(self):
        unreadable = tables()
        unreadable["06_Stability_Index"][1]["tenant_code"] = "T-TWO"
        two = assess(unreadable, "FX-2")
        flags = two["evidence"]["stability"]["candidates"][0]["flags"]
        self.assertTrue(any("Readability" in f for f in flags))
        self.assertTrue(any("does not answer" in f for f in flags))
        absent = tables()
        absent["06_Stability_Index"] = []
        self.assertIn("absence is not evidence", assess(absent, "FX-1")["evidence"]["stability"]["rejected"][0]["reason"])

    def test_overlapping_sop_revisions_are_a_conflict(self):
        one = assess(tables(), "FX-1")
        self.assertEqual(one["evidence"]["sop"]["conflicts"][0]["revisions"], ["Rev 01", "Rev 02"])
        self.assertTrue(any("Document control must state" in a for a in one["required_human_actions"]))

    def test_policy_interval_boundaries_are_half_open_and_flagged(self):
        three = assess(tables(), "FX-3")  # excursion 2026-06-01: Rev 01 ends that day (excluded), SOP-ONE-2 starts that day
        docs = {(c["doc_id"], c["revision"]) for c in three["evidence"]["sop"]["candidates"]}
        self.assertNotIn(("SOP-ONE-1", "Rev 01"), docs)
        self.assertIn(("SOP-ONE-2", "Rev 01"), docs)
        starts_today = next(c for c in three["evidence"]["sop"]["candidates"] if c["doc_id"] == "SOP-ONE-2")
        self.assertTrue(any("date-only" in f for f in starts_today["flags"]))

    def test_site_specific_scope_requires_annexure(self):
        one = assess(tables(), "FX-1")
        self.assertIn("Site-specific SOP annexure(s) are not supplied.", one["missing_inputs"])

    def test_missing_product_reference(self):
        blank = tables()
        blank["01_Excursion_Events"][0]["product_ref_as_received"] = ""
        self.assertEqual(entity(assess(blank, "FX-1"), "PRODUCT")["status"], "MISSING_REFERENCE")

    def test_alias_observations_are_surfaced_but_never_resolve(self):
        three = assess(tables(), "FX-3")
        product = entity(three, "PRODUCT")
        self.assertEqual(product["status"], "UNRESOLVED")
        aliases = {a["alias"] for a in product["unverified_alias_candidates"]}
        self.assertEqual(aliases, {"sku-pen"})  # the second alias was confirmed after the extract-date cutoff
        self.assertEqual(three["evidence"]["stability"]["candidates"], [])

    def test_historical_replay_hides_facts_recorded_after_known_at(self):
        before = assess(tables(), "FX-1", known_at="2026-04-10T00:00:00+00:00")
        after = assess(tables(), "FX-1", known_at="2026-04-11T00:00:00+00:00")
        self.assertEqual(before["evidence"]["telemetry"]["bulletins"][0]["status"], "NOT_KNOWN_AT_CUTOFF")
        self.assertTrue(any("TT-CB-999" in c for c in after["conflicts"]))
        self.assertNotEqual(before["assessment_sha256"], after["assessment_sha256"])

    def test_repeated_execution_is_deterministic(self):
        self.assertEqual(assess(tables(), "FX-1")["assessment_sha256"], assess(tables(), "FX-1")["assessment_sha256"])

    def test_correction_yields_new_assessment_and_leaves_original_intact(self):
        source = tables()
        original = package(assess(source, "FX-1"))
        frozen = json.dumps(original, sort_keys=True)
        correction = [{"id": "c1", "recorded_at": "2026-10-01T00:00:00+00:00", "sheet": "06_Stability_Index", "row": 2,
                       "field": "product_text_as_written", "value": "Alpha 10mg PFS — pre-filled syringe"}]
        hidden = assess(source, "FX-1", corrections=correction)  # known_at defaults to extract date, before the correction
        self.assertEqual(hidden["inputs"]["corrections_applied"], [])
        applied = assess(source, "FX-1", known_at="2026-10-02T00:00:00+00:00", corrections=correction)
        self.assertEqual(applied["inputs"]["corrections_applied"][0]["id"], "c1")
        self.assertFalse(any("Presentation mismatch" in f for c in applied["evidence"]["stability"]["candidates"] for f in c["flags"]))
        self.assertNotEqual(applied["assessment_sha256"], original["assessment"]["assessment_sha256"])
        self.assertEqual(json.dumps(original, sort_keys=True), frozen)
        self.assertTrue(verify_package(original))
        self.assertEqual(source["06_Stability_Index"][0]["product_text_as_written"], "Alpha 10mg PFS — vial")
        with self.assertRaises(ValueError):
            apply_corrections(source, [dict(correction[0], row=999)], parse_time("2026-12-01"))

    def test_affected_firmware_is_flagged_without_a_fixed_correction(self):
        one = assess(tables(), "FX-1")
        effect = one["evidence"]["telemetry"]["bulletins"][0]["effect"]
        self.assertIn("up to 1.8 °C", effect)
        self.assertIn("not known", effect)
        self.assertTrue(any("no fixed correction" in c for c in one["conflicts"]))

    def test_conflicting_facility_records_fail_safely(self):
        one = assess(tables(), "FX-1")
        self.assertEqual(entity(one, "FACILITY", "origin")["status"], "CONFLICTING_SOURCE_RECORDS")
        self.assertTrue(any("conflicting timezones" in c for c in one["conflicts"]))

    def test_parent_and_subsidiary_contracts_are_ambiguous(self):
        self.assertEqual(entity(assess(tables(), "FX-1"), "CARRIER_CONTRACT")["status"], "AMBIGUOUS_PARENT_OR_SUBSIDIARY")

    def test_untagged_bms_source_is_quarantined_for_attribution(self):
        self.assertTrue(any("quarantine for attribution" in c for c in assess(tables(), "FX-2")["conflicts"]))

    def test_historical_outcomes_are_listed_but_never_read(self):
        source = tables()
        baseline = assess(source, "FX-1")
        self.assertIn("final_disposition", baseline["inputs"]["historical_fields_excluded"])
        source["01_Excursion_Events"][0]["final_disposition"] = "DESTROY"
        source["01_Excursion_Events"][0]["reviewer_overrode"] = "Y"
        self.assertEqual(assess(source, "FX-1")["assessment_sha256"], baseline["assessment_sha256"])
        self.assertEqual(baseline["conclusion"]["disposition"], "ABSTAIN")

    def test_notification_clock_starts_at_alert_receipt(self):
        one = assess(tables(), "FX-1")
        self.assertEqual(one["notification"]["clock_starts_at"], "2026-05-02T10:00:00+00:00")
        self.assertEqual(one["notification"]["due_at"], "2026-05-05T10:00:00+00:00")
        unknown = assess(tables(), "FX-3")
        self.assertEqual(unknown["notification"]["status"], "URGENT_POLICY_REVIEW")
        self.assertEqual(assess(tables(), "FX-2")["notification"]["regulator_output_language"], "Portuguese (pt-BR)")

    def test_package_verification_detects_tampering(self):
        bundle = package(assess(tables(), "FX-1"))
        self.assertTrue(verify_package(bundle))
        bundle["assessment"]["conflicts"] = []
        self.assertFalse(verify_package(bundle))


if __name__ == "__main__":
    unittest.main()
