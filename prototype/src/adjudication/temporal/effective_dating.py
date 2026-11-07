"""SQLite bitemporal reference store. Half-open UTC valid and recorded intervals."""

import json
import sqlite3
from datetime import datetime, timezone


def instant(value):
    t = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if t.tzinfo is None:
        t = t.replace(tzinfo=timezone.utc)
    return t.astimezone(timezone.utc).isoformat(timespec="seconds")


class TemporalStore:
    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("""CREATE TABLE IF NOT EXISTS reference_version (
            id INTEGER PRIMARY KEY, tenant TEXT NOT NULL, ref_key TEXT NOT NULL,
            valid_from TEXT NOT NULL, valid_to TEXT, recorded_from TEXT NOT NULL,
            recorded_to TEXT, payload TEXT NOT NULL)""")
        self.db.execute(
            "CREATE INDEX IF NOT EXISTS lookup ON reference_version(tenant,ref_key,valid_from,recorded_from)"
        )

    def put(self, tenant, key, valid_from, valid_to, recorded_from, payload):
        vf, vt, tx = instant(valid_from), instant(valid_to) if valid_to else None, instant(recorded_from)
        if not tenant or not key or (vt and vt <= vf):
            raise ValueError("Nonempty identity and positive valid interval required")
        with self.db:
            self.db.execute(
                "INSERT INTO reference_version(tenant,ref_key,valid_from,valid_to,recorded_from,payload) VALUES(?,?,?,?,?,?)",
                (tenant, key, vf, vt, tx, json.dumps(payload, sort_keys=True)),
            )

    def correct(self, tenant, key, recorded_at, valid_from, valid_to, payload):
        vf, vt, tx = instant(valid_from), instant(valid_to) if valid_to else None, instant(recorded_at)
        if vt and vt <= vf:
            raise ValueError("Positive valid interval required")
        with self.db:
            current = self.db.execute(
                "SELECT * FROM reference_version WHERE tenant=? AND ref_key=? AND valid_from=? AND valid_to IS ? AND recorded_to IS NULL",
                (tenant, key, vf, vt),
            ).fetchall()
            if len(current) != 1 or tx <= current[0]["recorded_from"]:
                raise ValueError("Correction requires one current interval and later transaction time")
            self.db.execute("UPDATE reference_version SET recorded_to=? WHERE id=?", (tx, current[0]["id"]))
            self.db.execute(
                "INSERT INTO reference_version(tenant,ref_key,valid_from,valid_to,recorded_from,payload) VALUES(?,?,?,?,?,?)",
                (tenant, key, vf, vt, tx, json.dumps(payload, sort_keys=True)),
            )

    def resolve(self, tenant, key, valid_at, known_at):
        valid_at, known_at = instant(valid_at), instant(known_at)
        rows = self.db.execute(
            """SELECT * FROM reference_version WHERE tenant=? AND ref_key=?
            AND valid_from<=? AND (valid_to IS NULL OR ?<valid_to)
            AND recorded_from<=? AND (recorded_to IS NULL OR ?<recorded_to) ORDER BY id""",
            (tenant, key, valid_at, valid_at, known_at, known_at),
        ).fetchall()
        return [dict(r, payload=json.loads(r["payload"])) for r in rows]

    def close(self):
        self.db.close()


def effective_sops(tables, tenant, valid_at):
    """All tenant document families; free-text site scope is never guessed."""
    from collections import defaultdict

    from adjudication.temporal.timezone import utc

    groups = defaultdict(list)
    for row in tables.get("05_SOP_Index", []):
        if (
            row["tenant_code"] == tenant
            and utc(row["effective_from"]) <= utc(valid_at)
            and (not row["effective_to"] or utc(valid_at) < utc(row["effective_to"]))
        ):
            groups[row["doc_id"]].append(row)
    return [
        {
            "doc_id": doc,
            "status": "AMBIGUOUS" if len(rows) > 1 else "CANDIDATE_SITE_SCOPE_UNVERIFIED",
            "candidates": rows,
        }
        for doc, rows in sorted(groups.items())
    ]
