import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

from sentinel.evidence import analyze, parse_time, sops_as_at
from sentinel.sample import create_workbook
from sentinel.service import Engine


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        source = create_workbook(Path(self.temp.name) / "synthetic.xlsx")
        self.engine = Engine(Path(self.temp.name) / "evidence.sqlite")
        self.engine.ingest(source)
        self.tables = self.engine.tables()

    def test_parse_time_normalizes_offsets_and_rejects_invalid_input(self):
        utc = parse_time("2030-01-02T03:00:00+03:00")
        self.assertEqual(utc.isoformat(), "2030-01-02T00:00:00+00:00")
        with self.assertRaises(ValueError):
            parse_time("not-a-time")

    def test_snapshot_known_time_and_sop_candidates_are_tenant_scoped(self):
        observed = parse_time(self.tables["_observed_at"])
        event = self.tables["01_Excursion_Events"][0]
        tenant = event["tenant_code"]
        earlier = (observed - timedelta(seconds=1)).isoformat()
        self.assertEqual(sops_as_at(self.tables, tenant, "2099-01-01", known_at=earlier), [])

        rows = sops_as_at(self.tables, tenant, "2099-01-01", known_at=observed.isoformat())
        self.assertTrue(all(row.get("tenant_code") == tenant for row in rows))

    def test_analysis_candidates_never_cross_tenant_or_decide_disposition(self):
        for event in self.tables["01_Excursion_Events"]:
            result = analyze(self.tables, event)
            self.assertNotIn("disposition", result)
            for candidates in result.values():
                if isinstance(candidates, list):
                    for candidate in candidates:
                        if isinstance(candidate, dict) and "tenant_code" in candidate:
                            self.assertEqual(candidate["tenant_code"], event["tenant_code"])


if __name__ == "__main__":
    unittest.main()
