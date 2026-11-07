"""Local append-only SQLite event ledger with a verifiable hash chain (not WORM security)."""

import hashlib
import json
import sqlite3


class EventStore:
    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path)
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS events (seq INTEGER PRIMARY KEY, tenant TEXT, case_id TEXT, body TEXT, previous_hash TEXT, hash TEXT)"
        )

    @staticmethod
    def digest(tenant, case_id, body, previous):
        payload = json.dumps([tenant, case_id, body, previous], separators=(",", ":"))
        return hashlib.sha256(payload.encode()).hexdigest()

    def append(self, tenant, case_id, body):
        encoded = json.dumps(body, sort_keys=True, default=str)
        with self.db:
            # BEGIN IMMEDIATE serialises the previous-hash read with the insert.
            self.db.execute("BEGIN IMMEDIATE")
            last = self.db.execute("SELECT hash FROM events ORDER BY seq DESC LIMIT 1").fetchone()
            previous = last[0] if last else "0" * 64
            digest = self.digest(tenant, case_id, encoded, previous)
            self.db.execute(
                "INSERT INTO events(tenant,case_id,body,previous_hash,hash) VALUES(?,?,?,?,?)",
                (tenant, case_id, encoded, previous, digest),
            )
        return digest

    def all(self):
        return [
            dict(zip(("seq", "tenant", "case_id", "body", "previous_hash", "hash"), row))
            for row in self.db.execute("SELECT * FROM events ORDER BY seq")
        ]

    def verify(self):
        previous = "0" * 64
        for row in self.all():
            if row["previous_hash"] != previous or row["hash"] != self.digest(
                row["tenant"], row["case_id"], row["body"], previous
            ):
                return False
            previous = row["hash"]
        return True

    def close(self):
        self.db.close()
