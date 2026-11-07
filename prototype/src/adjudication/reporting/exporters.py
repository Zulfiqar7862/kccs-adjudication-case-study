"""Five deterministic local-only outputs. Never commit real-source dossiers."""

import csv
import hashlib
import json
from pathlib import Path

from adjudication.audit.event_store import EventStore
from adjudication.evidence.gaps import gap_rows
from adjudication.rules.versioning import manifest


def write_csv(path, rows, fields):
    with Path(path).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def export(report, pack, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    (output / "adjudication_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True, default=str) + "\n"
    )
    write_csv(
        output / "adjudication_summary.csv",
        [{"metric": k, "value": json.dumps(v, sort_keys=True)} for k, v in report["summary"].items()],
        ["metric", "value"],
    )
    write_csv(output / "evidence_gaps.csv", gap_rows(report["cases"]), ["event_id", "tenant_code", "gap"])
    store = EventStore()
    for case in report["cases"]:
        store.append(case["tenant_code"], case["event_id"], {"action": "EVIDENCE_EVALUATED", "status": case["status"]})
    if not store.verify():
        raise RuntimeError("Audit chain invalid")
    write_csv(output / "case_audit_log.csv", store.all(), ["seq", "tenant", "case_id", "body", "previous_hash", "hash"])
    store.close()
    release = manifest(pack, "per-event valid time")
    release["outputs_sha256"] = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(output.iterdir())
        if p.name in {"adjudication_report.json", "adjudication_summary.csv", "case_audit_log.csv", "evidence_gaps.csv"}
    }
    (output / "run_manifest.json").write_text(json.dumps(release, indent=2, sort_keys=True) + "\n")
    return release
