from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from sentinel.ingestion import workbook
from sentinel.fixtures.sample import SAMPLE_EVENT_COUNT, SAMPLE_TENANTS, create_workbook


class SampleWorkbookTests(unittest.TestCase):
    def test_generates_valid_synthetic_workbook(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = create_workbook(Path(directory) / "sample.xlsx")
            self.assertEqual(path, Path(directory) / "sample.xlsx")

            with ZipFile(path) as archive:
                self.assertIsNone(archive.testzip())
                self.assertIn("xl/_rels/workbook.xml.rels", archive.namelist())
                self.assertEqual(len([name for name in archive.namelist() if name.startswith("xl/worksheets/")]), 15)

            tables = workbook.load(path)
            events = tables["01_Excursion_Events"]
            self.assertEqual(len(events), SAMPLE_EVENT_COUNT)
            self.assertEqual({row["tenant_code"] for row in events}, set(SAMPLE_TENANTS))
            self.assertEqual(events[0]["_row"], 2)
            self.assertEqual(events[0]["leg_no"], "01")
            self.assertEqual(events[0]["alert_ts_utc"], "2026-01-01 08:00")
            self.assertEqual(len(tables), 15)
            self.assertEqual(len(tables["12_Tenant_Constraints"]), 2)
            self.assertEqual(tables["02_Product_Master"][0]["internal_sku"], "00001234")

    def test_generated_file_hash_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = create_workbook(Path(directory) / "first.xlsx")
            second = create_workbook(Path(directory) / "second.xlsx")
            self.assertEqual(hashlib.sha256(first.read_bytes()).digest(), hashlib.sha256(second.read_bytes()).digest())


if __name__ == "__main__":
    unittest.main()
