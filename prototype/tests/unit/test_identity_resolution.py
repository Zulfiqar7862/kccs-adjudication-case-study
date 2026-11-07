from copy import deepcopy

import pytest
from adjudication.identity.confidence import confidence_for
from adjudication.identity.resolver import resolve_product
from adjudication.ingestion.normalizer import normalize


def test_same_sku_is_tenant_scoped(pack):
    a = resolve_product(pack.tables, "SYN-A", "SYN-SKU-1")
    b = resolve_product(pack.tables, "SYN-B", "SYN-SKU-1")
    assert a["candidates"][0]["brand_as_labelled"] != b["candidates"][0]["brand_as_labelled"]
    assert a["confidence"] == "SOURCE_ONLY"
    assert resolve_product(pack.tables, "FOREIGN", "SYN-SKU-1")["status"] == "MISSING"


@pytest.mark.parametrize("ref", [None, "", "unrecognised"])
def test_missing_identity(pack, ref):
    assert resolve_product(pack.tables, "SYN-A", ref)["status"] == "MISSING"


def test_aliases_propose_never_authorise(pack):
    pack.tables["07_Alias_Observations"] = [
        dict(
            entity_kind="PRODUCT",
            same_real_world_thing="Y",
            string_a="a synthetic synonym",
            string_b="SYN-SKU-1",
            _sheet="07_Alias_Observations",
            _row=2,
        )
    ]
    result = resolve_product(pack.tables, "SYN-A", "a synthetic synonym")
    assert result["status"] == "UNVERIFIED_ALIAS" and result["confidence"] == "UNVERIFIED"
    assert len(result["alias_sources"]) == 1
    pack.tables["07_Alias_Observations"][0]["same_real_world_thing"] = "N"
    assert resolve_product(pack.tables, "SYN-A", "a synthetic synonym")["status"] == "MISSING"


def test_ambiguous_identity_is_not_latest(pack):
    pack.tables["02_Product_Master"].append(deepcopy(pack.tables["02_Product_Master"][0]))
    assert resolve_product(pack.tables, "SYN-A", "SYN-SKU-1")["status"] == "AMBIGUOUS"
    assert confidence_for("AMBIGUOUS") == "CONFLICT"
    assert normalize("  A   B ") == "a b"
    assert normalize("00001") == "00001"
