import re
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sentinel.fixtures.sample import create_workbook
from sentinel.workflow.service import DomainError, Engine, verify_export


def principal(tenant, actor, role):
    return {"tenant": tenant, "actor": actor, "role": role}


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.source = create_workbook(root / "synthetic.xlsx")
        self.database = root / "cases.sqlite"
        self.clock_value = datetime(2035, 1, 1, tzinfo=timezone.utc)
        self.engine = Engine(self.database, clock=lambda: self.clock_value)
        self.engine.ingest(self.source)
        self.events = self.engine.tables()["01_Excursion_Events"]
        self.constraints = self.engine.tables()["12_Tenant_Constraints"]
        self.sequence = 0

    def command(self, tenant, case_id, role, action, body):
        self.sequence += 1
        current = self.engine.get_case(tenant, case_id)
        return self.engine.command(
            principal(tenant, f"test-{role}", role), case_id, action, body,
            f"workflow-{self.sequence}", current["version"],
        )

    def selected_case(self, dual=None):
        constraints = {row["tenant_code"]: row["who_signs_a_disposition"] for row in self.constraints}
        eligible = [row for row in self.events if dual is None or
                    (re.search(r"\bdual\b", constraints[row["tenant_code"]], re.IGNORECASE) is not None) == dual]
        event = eligible[0]
        return event["tenant_code"], event["event_id"]

    def test_import_replay_scope_idempotency_and_persistence(self):
        tenant, case_id = self.selected_case()
        before = self.engine.get_case(tenant, case_id)
        self.engine.ingest(self.source)
        after = self.engine.get_case(tenant, case_id)
        self.assertEqual(before, after)
        self.assertEqual(after["state"], "WAITING_EVIDENCE")
        other_tenant = next(row["tenant_code"] for row in self.events if row["tenant_code"] != tenant)
        with self.assertRaises(DomainError) as missing:
            self.engine.get_case(other_tenant, case_id)
        self.assertEqual(missing.exception.status, 404)

        body = {"kind": "SOP", "source_ref": "synthetic://sop", "content": "TEST STUB only"}
        actor = principal(tenant, "reviewer-a", "reviewer")
        first = self.engine.command(actor, case_id, "evidence", body, "replay-key", before["version"])
        replay = self.engine.command(actor, case_id, "evidence", body, "replay-key", before["version"])
        self.assertEqual(first, replay)
        with self.assertRaises(DomainError) as reused:
            self.engine.command(actor, case_id, "evidence", {**body, "content": "different"},
                                "replay-key", before["version"])
        self.assertEqual(reused.exception.status, 409)

        reopened = Engine(self.database, clock=lambda: self.clock_value)
        self.assertEqual(reopened.get_case(tenant, case_id), self.engine.get_case(tenant, case_id))

    def test_concurrent_commands_allow_only_one_version_winner(self):
        tenant, case_id = self.selected_case()
        version = self.engine.get_case(tenant, case_id)["version"]
        barrier = threading.Barrier(2)

        def submit(n):
            barrier.wait()
            try:
                return self.engine.command(
                    principal(tenant, f"reviewer-{n}", "reviewer"), case_id, "evidence",
                    {"kind": "SOP", "source_ref": f"synthetic://{n}", "content": "TEST STUB only"},
                    f"concurrent-{n}", version,
                )
            except DomainError as error:
                return error.status

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(submit, (1, 2)))
        self.assertEqual(sum(isinstance(result, dict) for result in results), 1)
        self.assertEqual(results.count(409), 1)

    def test_invalid_command_rolls_back_packet_and_audit(self):
        tenant, case_id = self.selected_case()
        before = self.engine.get_case(tenant, case_id)
        audit_before = self.engine.export(tenant, case_id)["audit"]
        with self.assertRaises(DomainError):
            self.command(tenant, case_id, "reviewer", "evidence", {"kind": "UNKNOWN"})
        self.assertEqual(before, self.engine.get_case(tenant, case_id))
        self.assertEqual(audit_before, self.engine.export(tenant, case_id)["audit"])

    def test_dual_review_sign_reopen_and_audit_integrity(self):
        tenant, case_id = self.selected_case(dual=True)
        packet = self.engine.get_case(tenant, case_id)["packet"]
        for kind in ("SOP", "STABILITY", "TELEMETRY", "IDENTITY", "BATCH", "CONTRACT"):
            self.command(tenant, case_id, "reviewer", "evidence", {
                "kind": kind, "source_ref": f"synthetic://{kind.casefold()}",
                "content": f"TEST STUB only: {kind}",
            })
        reviewed = self.engine.get_case(tenant, case_id)
        references = [item["id"] for item in reviewed["packet"]["artifacts"]]
        self.command(tenant, case_id, "reviewer", "review", {
            "resolutions": {blocker: references for blocker in packet["analysis"]["blockers"]},
            "note": "Synthetic workflow test; no adjudication asserted.",
        })
        self.command(tenant, case_id, "site_qa", "sign", {
            "disposition": "QUARANTINE", "rationale": "Synthetic first approval",
        })
        self.assertEqual(self.engine.get_case(tenant, case_id)["state"], "READY_FOR_REVIEW")
        final = self.command(tenant, case_id, "corporate_qa", "sign", {
            "disposition": "QUARANTINE", "rationale": "Synthetic independent approval",
        })
        self.assertEqual(final["state"], "DISPOSED")

        previous = self.engine.export(tenant, case_id)
        self.assertTrue(verify_export(previous))
        tampered = dict(previous)
        tampered["manifest_hash"] = "invalid-test-hash"
        self.assertFalse(verify_export(tampered))
        self.command(tenant, case_id, "reviewer", "reopen", {"reason": "Synthetic test reopening"})
        current = self.engine.export(tenant, case_id)
        self.assertTrue(verify_export(current))
        self.assertEqual(len(current["revisions"]), len(previous["revisions"]) + 1)
        self.assertEqual(current["revisions"][:-1], previous["revisions"])
        self.assertEqual(self.engine.get_case(tenant, case_id)["state"], "WAITING_EVIDENCE")

    def test_second_distinct_snapshot_is_rejected(self):
        altered = Path(self.temp.name) / "different-snapshot.xlsx"
        altered.write_bytes(Path(self.source).read_bytes() + b"\n")
        with self.assertRaises(DomainError) as rejected:
            self.engine.ingest(altered)
        self.assertEqual(rejected.exception.status, 409)

    def test_single_signer_policy_and_role_enforcement(self):
        tenant, case_id = self.selected_case(dual=False)
        packet = self.engine.get_case(tenant, case_id)["packet"]
        for kind in ("SOP", "STABILITY", "TELEMETRY", "IDENTITY", "BATCH", "CONTRACT"):
            self.command(tenant, case_id, "reviewer", "evidence", {
                "kind": kind, "source_ref": f"synthetic://{kind.casefold()}",
                "content": f"TEST STUB only: {kind}",
            })
        artifacts = self.engine.get_case(tenant, case_id)["packet"]["artifacts"]
        references = [item["id"] for item in artifacts]
        self.command(tenant, case_id, "reviewer", "review", {
            "resolutions": {blocker: references for blocker in packet["analysis"]["blockers"]},
            "note": "Synthetic single-signer policy test.",
        })
        with self.assertRaises(DomainError) as forbidden:
            self.command(tenant, case_id, "site_qa", "sign", {
                "disposition": "QUARANTINE", "rationale": "Role not allowed by synthetic policy",
            })
        self.assertEqual(forbidden.exception.status, 403)
        result = self.command(tenant, case_id, "signer", "sign", {
            "disposition": "QUARANTINE", "rationale": "Synthetic authorized signer",
        })
        self.assertEqual(result["state"], "DISPOSED")
        self.assertEqual(len(self.engine.get_case(tenant, case_id)["packet"]["signatures"]), 1)

    def test_new_evidence_invalidates_completed_review_and_signature(self):
        tenant, case_id = self.selected_case(dual=True)
        packet = self.engine.get_case(tenant, case_id)["packet"]
        for kind in ("SOP", "STABILITY", "TELEMETRY", "IDENTITY", "BATCH", "CONTRACT"):
            self.command(tenant, case_id, "reviewer", "evidence", {
                "kind": kind, "source_ref": f"synthetic://{kind.casefold()}",
                "content": f"TEST STUB only: {kind}",
            })
        references = [item["id"] for item in self.engine.get_case(tenant, case_id)["packet"]["artifacts"]]
        self.command(tenant, case_id, "reviewer", "review", {
            "resolutions": {blocker: references for blocker in packet["analysis"]["blockers"]},
            "note": "Synthetic review invalidation test.",
        })
        self.command(tenant, case_id, "site_qa", "sign", {
            "disposition": "QUARANTINE", "rationale": "Synthetic first approval",
        })
        current = self.engine.get_case(tenant, case_id)
        self.assertEqual(current["state"], "READY_FOR_REVIEW")
        self.assertTrue(current["packet"]["review"])
        self.assertTrue(current["packet"]["signatures"])
        updated = self.command(tenant, case_id, "reviewer", "evidence", {
            "kind": "SOP", "source_ref": "synthetic://new-evidence", "content": "TEST STUB only: update",
        })
        self.assertEqual(updated["state"], "WAITING_EVIDENCE")
        packet_after_update = self.engine.get_case(tenant, case_id)["packet"]
        self.assertIsNone(packet_after_update["review"])
        self.assertEqual(packet_after_update["signatures"], [])

    def test_reminder_retry_never_creates_receipt_and_deadline_is_data_derived(self):
        tenants = {row["tenant_code"] for row in self.events}
        notices = [(tenant, item) for tenant in tenants for item in self.engine.notifications(tenant)]
        self.assertTrue(notices)
        boundaries = [datetime.fromisoformat(item["deadline"] or item["alert_at"]) for _, item in notices]
        self.clock_value = max(boundaries) + timedelta(days=2)
        for tenant, item in notices:
            if item["deadline"] is not None:
                self.assertGreater(datetime.fromisoformat(item["deadline"]),
                                   datetime.fromisoformat(item["alert_at"]))
                self.assertEqual(item["status"], "OVERDUE")
            else:
                self.assertEqual(item["status"], "POLICY_REQUIRED")
        tenant = notices[0][0]
        failed = self.engine.tick(tenant, lambda key, payload: (_ for _ in ()).throw(ConnectionError("test outage")))
        self.assertTrue(failed)
        self.assertTrue(all(not row["delivered"] for row in failed))
        retried = self.engine.tick(tenant, lambda key, payload: None)
        self.assertTrue(retried)
        self.assertTrue(all(row["delivered"] for row in retried))
        self.assertTrue(all(item["receipt"] is None for item in self.engine.notifications(tenant)))

    def test_regulatory_receipt_records_a_human_attestation(self):
        tenants = {row["tenant_code"] for row in self.events}
        notices = [(tenant, item) for tenant in tenants for item in self.engine.notifications(tenant)
                   if item["receipt"] is None]
        self.assertTrue(notices)
        tenant, notice = notices[0]
        event = next(row for row in self.events if row["event_id"] == notice["case_id"])
        self.clock_value = datetime(2040, 1, 1, tzinfo=timezone.utc)
        sent_at = datetime.fromisoformat(event["alert_ts_utc"]) + timedelta(minutes=1)
        self.command(tenant, notice["case_id"], "regulatory", "notify", {
            "receipt": "Synthetic test attestation", "sent_at": sent_at.isoformat(),
        })
        updated = next(item for item in self.engine.notifications(tenant)
                       if item["case_id"] == notice["case_id"])
        self.assertIsNotNone(updated["receipt"])
        self.assertEqual(datetime.fromisoformat(updated["receipt"]["sent_at"]), sent_at.replace(tzinfo=timezone.utc))
        if updated["deadline"] is None:
            self.assertEqual(updated["status"], "POLICY_REQUIRED")
        else:
            deadline = datetime.fromisoformat(updated["deadline"])
            self.assertEqual(updated["status"], "NOTIFIED_ON_TIME" if sent_at.replace(tzinfo=timezone.utc) <= deadline
                             else "NOTIFIED_LATE")

    def test_recorded_receipt_suppresses_internal_reminders(self):
        tenants = {row["tenant_code"] for row in self.events}
        notices = [(tenant, item) for tenant in tenants for item in self.engine.notifications(tenant)
                   if item["receipt"] is None]
        tenant, notice = notices[0]
        event = next(row for row in self.events if row["event_id"] == notice["case_id"])
        self.clock_value = datetime(2040, 1, 1, tzinfo=timezone.utc)
        sent_at = datetime.fromisoformat(event["alert_ts_utc"])
        self.command(tenant, notice["case_id"], "regulatory", "notify", {
            "receipt": "Synthetic attestation before reminder", "sent_at": sent_at.isoformat(),
        })
        delivered = self.engine.tick(tenant, lambda key, payload: None)
        self.assertNotIn(notice["case_id"], {row["id"] for row in delivered})
        saved = next(item for item in self.engine.notifications(tenant) if item["case_id"] == notice["case_id"])
        self.assertIsNotNone(saved["receipt"])



if __name__ == "__main__":
    unittest.main()
