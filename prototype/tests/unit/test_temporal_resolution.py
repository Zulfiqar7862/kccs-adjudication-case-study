import pytest
from adjudication.temporal.effective_dating import TemporalStore, effective_sops


def test_correction_preserves_two_axis_history(tmp_path):
    store = TemporalStore(tmp_path / "reference.db")
    store.put("SYN-A", "DOC", "2030-01-01", "2031-01-01", "2030-01-02", {"revision": 1})
    store.correct("SYN-A", "DOC", "2030-02-01", "2030-01-01", "2031-01-01", {"revision": 2})
    assert store.resolve("SYN-A", "DOC", "2030-01-20", "2030-01-25")[0]["payload"]["revision"] == 1
    assert store.resolve("SYN-A", "DOC", "2030-01-20", "2030-02-01")[0]["payload"]["revision"] == 2
    assert store.resolve("SYN-B", "DOC", "2030-01-20", "2030-02-01") == []
    assert store.resolve("SYN-A", "DOC", "2031-01-01", "2030-02-01") == []
    store.close()
    reopened = TemporalStore(tmp_path / "reference.db")
    assert reopened.resolve("SYN-A", "DOC", "2030-01-20", "2030-02-01")
    reopened.close()


def test_overlaps_remain_visible():
    store = TemporalStore()
    for revision in (1, 2):
        store.put("SYN-A", "DOC", "2030-01-01", None, "2030-01-01", {"revision": revision})
    assert len(store.resolve("SYN-A", "DOC", "2030-02-01", "2030-03-01")) == 2
    with pytest.raises(ValueError):
        store.correct("SYN-A", "DOC", "2030-04-01", "2030-01-01", None, {})
    store.close()


@pytest.mark.parametrize("start,end", [("2031-01-01", "2030-01-01"), ("invalid", None)])
def test_invalid_intervals(start, end):
    store = TemporalStore()
    with pytest.raises(ValueError):
        store.put("SYN-A", "DOC", start, end, "2030-01-01", {})
    store.close()


def test_invalid_corrections_and_offsets():
    store = TemporalStore()
    with pytest.raises(ValueError):
        store.correct("SYN-A", "DOC", "2030-02-01", "2030-01-01", None, {})
    store.put("SYN-A", "DOC", "2030-01-01T01:00:00+01:00", None, "2030-01-01", {})
    with pytest.raises(ValueError):
        store.correct("SYN-A", "DOC", "2029-01-01", "2030-01-01", None, {})
    with pytest.raises(ValueError):
        store.correct("SYN-A", "DOC", "2031-01-01", "2030-01-01", "2029-01-01", {})
    assert store.resolve("SYN-A", "DOC", "2030-01-01Z", "2030-01-02")
    store.close()


def test_sop_scope_is_unverified_and_overlap_not_ranked(pack):
    base = dict(tenant_code="SYN-A", doc_id="SYN-DOC", effective_from="2029-01-01", effective_to=None)
    pack.tables["05_SOP_Index"] = [dict(base, revision="1"), dict(base, revision="2")]
    assert effective_sops(pack.tables, "SYN-A", "2030-01-01")[0]["status"] == "AMBIGUOUS"
    pack.tables["05_SOP_Index"].pop()
    assert effective_sops(pack.tables, "SYN-A", "2030-01-01")[0]["status"] == "CANDIDATE_SITE_SCOPE_UNVERIFIED"
    assert effective_sops(pack.tables, "SYN-B", "2030-01-01") == []
