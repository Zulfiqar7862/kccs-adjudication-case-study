"""Tenant-scoped candidate resolution; exact source equality is weaker than verified identity."""

from adjudication.identity.aliases import propose
from adjudication.identity.confidence import confidence_for
from adjudication.ingestion.normalizer import normalize as norm

COLUMNS = ("brand_as_labelled", "generic_inn", "internal_sku", "gtin", "legacy_code")


def resolve_product(tables, tenant, ref):
    rows = [x for x in tables["02_Product_Master"] if x["tenant_code"] == tenant]
    exact = [x for x in rows if norm(ref) and any(norm(x[k]) == norm(ref) for k in COLUMNS)]
    targets, sources = propose(tables, ref) if not exact else (set(), [])
    candidates = exact or [x for x in rows if targets and any(norm(x[k]) in targets for k in COLUMNS)]
    status = (
        ("EXACT_SOURCE_MATCH" if len(exact) == 1 else "AMBIGUOUS")
        if exact
        else ("UNVERIFIED_ALIAS" if candidates else "MISSING")
    )
    return {"status": status, "confidence": confidence_for(status), "candidates": candidates, "alias_sources": sources}
