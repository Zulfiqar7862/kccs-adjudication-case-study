import json
import secrets
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from sentinel.http import MAX_BODY, make_server
from sentinel.sample import create_workbook
from sentinel.service import Engine


class HttpTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        engine = Engine(root / "http.sqlite")
        engine.ingest(create_workbook(root / "synthetic.xlsx"))
        self.engine = engine
        self.events = engine.tables()["01_Excursion_Events"]
        self.tenant = self.events[0]["tenant_code"]
        self.case_id = self.events[0]["event_id"]
        self.token = secrets.token_urlsafe(32)
        credentials = {self.token: {"tenant": self.tenant, "actor": "http-test", "role": "reviewer"}}
        self.server = make_server(engine, credentials)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop_server)
        self.base = f"http://127.0.0.1:{self.server.server_port}"

    def stop_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)

    def request(self, method, route, body=None, token=None, key="http-test-key"):
        data = json.dumps(body).encode() if body is not None else None
        headers = {}
        if token is not None:
            headers["Authorization"] = f"Bearer {token}"
        if body is not None:
            headers["Content-Type"] = "application/json"
            headers["Idempotency-Key"] = key
        req = Request(self.base + route, method=method, data=data, headers=headers)
        try:
            with urlopen(req, timeout=10) as response:
                return response.status, response.headers, json.load(response)
        except HTTPError as error:
            with error:
                return error.code, error.headers, json.load(error)

    def test_health_auth_tenant_scope_and_headers(self):
        status, headers, body = self.request("GET", "/health")
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "ok")
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertEqual(headers["X-Content-Type-Options"], "nosniff")

        status, _, _ = self.request("GET", "/cases")
        self.assertEqual(status, 401)
        status, _, cases = self.request("GET", "/cases", token=self.token)
        self.assertEqual(status, 200)
        self.assertTrue(cases)

        foreign = next(row for row in self.events if row["tenant_code"] != self.tenant)
        status, _, _ = self.request("GET", f"/cases/{foreign['event_id']}", token=self.token)
        self.assertEqual(status, 404)

    def test_snapshot_sop_audit_and_idempotent_command_routes(self):
        observed = self.engine.tables()["_observed_at"]
        from sentinel.evidence import parse_time
        from datetime import timedelta
        known_at = (parse_time(observed) - timedelta(seconds=1)).isoformat()
        status, _, rows = self.request(
            "GET", "/sops?" + urlencode({"valid_at": "2099-01-01", "known_at": known_at}), token=self.token,
        )
        self.assertEqual(status, 200)
        self.assertEqual(rows, [])
        status, _, bundle = self.request("GET", f"/cases/{self.case_id}/audit", token=self.token)
        self.assertEqual(status, 200)
        self.assertIn("manifest_hash", bundle)

        case = self.engine.get_case(self.tenant, self.case_id)
        command = {"expected_version": case["version"], "kind": "SOP",
                   "source_ref": "synthetic://http", "content": "TEST STUB only"}
        path = f"/cases/{self.case_id}/evidence"
        first = self.request("POST", path, body=command, token=self.token, key="stable-http-key")
        replay = self.request("POST", path, body=command, token=self.token, key="stable-http-key")
        self.assertEqual(first[0], 200)
        self.assertEqual(replay[0], 200)
        self.assertEqual(first[2], replay[2])

    def test_full_payload_limit_returns_413(self):
        body = b" " * (MAX_BODY + 1)
        req = Request(self.base + f"/cases/{self.case_id}/evidence", method="POST", data=body,
                      headers={"Authorization": f"Bearer {self.token}",
                               "Content-Type": "application/json", "Idempotency-Key": "large-payload"})
        with self.assertRaises(HTTPError) as error:
            urlopen(req, timeout=10)
        with error.exception as response:
            self.assertEqual(response.code, 413)
            self.assertIn("too large", json.load(response)["error"])

    def test_server_rejects_non_loopback_binding(self):
        with self.assertRaises(ValueError):
            make_server(self.engine, {}, host="0.0.0.0")


if __name__ == "__main__":
    unittest.main()
