import os
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

from sentinel.evidence.analysis import parse_time, sops_as_at
from sentinel.workflow.service import Engine, verify_export


class ConfiguredWorkbookTests(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("SENTINEL_WORKBOOK"), "SENTINEL_WORKBOOK is not configured")
    def test_configured_workbook_is_imported_without_decisions_or_tenant_leaks(self):
        source = Path(os.environ["SENTINEL_WORKBOOK"])
        self.assertTrue(source.is_file(), "Configured SENTINEL_WORKBOOK path does not exist")
        with tempfile.TemporaryDirectory() as directory:
            engine = Engine(Path(directory) / "private-workbook.sqlite")
            imported = engine.ingest(source)
            tables = engine.tables()
            events = tables["01_Excursion_Events"]
            self.assertTrue(imported["created"] == len(events),
                            "Imported event count did not match the configured workbook")
            replay = engine.ingest(source)
            self.assertTrue(replay.get("replayed"), "Exact workbook replay was not identified")
            self.assertTrue(replay.get("created") == 0, "Exact workbook replay created additional cases")

            by_tenant = {}
            for event in events:
                tenant = event["tenant_code"]
                case_id = event["event_id"]
                by_tenant.setdefault(tenant, set()).add(case_id)
                case = engine.get_case(tenant, case_id)
                self.assertEqual(case["state"], "WAITING_EVIDENCE")
                self.assertTrue(case["packet"].get("disposition") is None,
                                "Imported case unexpectedly contains a disposition")
                analysis = case["packet"]["analysis"]
                self.assertTrue(analysis.get("blockers"),
                                "Imported case is missing evidence blockers")
                for rows in analysis.values():
                    if isinstance(rows, list):
                        for candidate in rows:
                            if isinstance(candidate, dict) and "tenant_code" in candidate:
                                self.assertTrue(candidate["tenant_code"] == tenant,
                                                "Analysis contains a cross-tenant candidate")
                self.assertTrue(verify_export(engine.export(tenant, case_id)),
                                "Imported case export failed integrity verification")

            for tenant, expected_ids in by_tenant.items():
                actual_ids = {case["id"] for case in engine.list_cases(tenant)}
                self.assertTrue(actual_ids == expected_ids,
                                "Tenant case list does not match imported event identities")

            observed = parse_time(tables["_observed_at"])
            self.assertEqual(
                sops_as_at(tables, next(iter(by_tenant)), "2099-01-01",
                           known_at=(observed - timedelta(seconds=1)).isoformat()),
                [],
            )
