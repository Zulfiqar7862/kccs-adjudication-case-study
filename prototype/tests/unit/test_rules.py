import csv
import json
import os
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest
from adjudication.cli import main, run
from adjudication.config import Config
from adjudication.evidence.service import resolve_study
from adjudication.exceptions import DataContractError
from adjudication.ingestion.validators import validate_tables
from adjudication.recommendations.guardrails import enforce
from adjudication.reporting.report_builder import build_report


def test_synthetic_golden_report(pack, fixtures_dir):
    report = build_report(pack)
    expected = json.loads((fixtures_dir / "expected_outputs/sample_adjudication_report.json").read_text())
    assert {k: report["summary"][k] for k in expected} == expected
    assert all(not c["proposed_auto_close"] and c["signed_disposition"] is None for c in report["cases"])


def test_document_and_calibration_hazards(pack, kernel):
    p = pack.tables["02_Product_Master"][0]
    study = dict(
        tenant_code="SYN-A",
        study_ref=p["stability_study_ref"],
        readable="N — synthetic illegible scan",
        study_type="Accelerated",
        permitted_excursion_text="synthetic limit not authoritative",
        product_text_as_written="Example vial",
        file_path_text="/T-FOREIGN/synthetic.pdf",
    )
    pack.tables["06_Stability_Index"] = [study]
    issues = resolve_study(pack.tables, p)["issues"]
    assert {"STUDY_UNREADABLE", "WRONG_PRESENTATION", "OWNERSHIP_PATH_CONFLICT", "NO_USABLE_EXCURSION_LIMIT"} <= set(
        issues
    )
    study.update(
        readable="Partial", product_text_as_written="Synthetic product", study_type="Excursion / thermal cycling"
    )
    pack.tables["06_Stability_Index"].append(deepcopy(study))
    assert {"STUDY_PARTIAL", "STUDY_AMBIGUOUS", "PRESENTATION_UNVERIFIED"} <= set(
        resolve_study(pack.tables, p)["issues"]
    )
    study["tenant_code"] = "FOREIGN"
    pack.tables["06_Stability_Index"] = [study]
    assert resolve_study(pack.tables, p)["issues"] == ["STUDY_NOT_INDEXED"]


def test_labels_never_affect_eligibility(pack, kernel):
    event = deepcopy(pack.events[0])
    before = kernel.evaluate(event)
    event.update(
        final_disposition="DESTROY",
        triage_outcome="NON_ACTIONABLE",
        rules_engine_recommendation="DESTROY",
        reviewer_overrode="Y",
    )
    assert kernel.evaluate(event) == before


@pytest.mark.parametrize(
    "alteration", [{"signed_disposition": "RELEASE"}, {"proposed_auto_close": True}, {"status": "SAFE"}]
)
def test_output_guardrails(alteration):
    with pytest.raises(ValueError):
        enforce(
            dict(status="NEEDS_EVIDENCE", **{k: v for k, v in alteration.items() if k != "status"})
            if "status" not in alteration
            else alteration
        )


def test_validator_rejects_bad_data(pack):
    tables = deepcopy(pack.tables)
    tables["01_Excursion_Events"].append(deepcopy(tables["01_Excursion_Events"][0]))
    with pytest.raises(DataContractError):
        validate_tables(tables)
    with pytest.raises(DataContractError):
        validate_tables({})
    tables = deepcopy(pack.tables)
    del tables["01_Excursion_Events"][0]["logger_fw"]
    with pytest.raises(DataContractError):
        validate_tables(tables)
    for value in ("bad", float("nan")):
        tables = deepcopy(pack.tables)
        tables["01_Excursion_Events"][0]["max_temp_c"] = value
        with pytest.raises(DataContractError):
            validate_tables(tables)
    tables = deepcopy(pack.tables)
    tables["01_Excursion_Events"][0]["tenant_code"] = ""
    with pytest.raises(DataContractError):
        validate_tables(tables)


def test_fixture_cli_reproducibility_and_exports(fixtures_dir, tmp_path):
    report = run(output=tmp_path / "one", fixtures=fixtures_dir)
    run(output=tmp_path / "two", fixtures=fixtures_dir)
    assert report["summary"]["events"] == 4
    names = {
        "adjudication_report.json",
        "adjudication_summary.csv",
        "case_audit_log.csv",
        "evidence_gaps.csv",
        "run_manifest.json",
    }
    assert {p.name for p in (tmp_path / "one").iterdir()} == names
    for name in names:
        assert (tmp_path / "one" / name).read_bytes() == (tmp_path / "two" / name).read_bytes()
    with (tmp_path / "one/case_audit_log.csv").open() as f:
        assert len(list(csv.DictReader(f))) == 4
    assert main(["--fixtures", str(fixtures_dir), "--out", str(tmp_path / "three")]) == 0
    p = subprocess.run(
        [sys.executable, "-m", "adjudication.cli", "--fixtures", str(fixtures_dir), "--out", str(tmp_path / "four")],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[2] / "src")},
    )
    assert p.returncode == 0, p.stderr
    assert json.loads(p.stdout)["events"] == 4


def test_config_from_environment(monkeypatch):
    monkeypatch.setenv("ADJUDICATION_OUTPUT", "synthetic-output")
    monkeypatch.setenv("ADJUDICATION_WORKBOOK", "synthetic.xlsx")
    config = Config.from_env()
    assert config.output == Path("synthetic-output") and config.workbook == Path("synthetic.xlsx")
