"""Alias observations propose candidates only; no tenant/authority/time proof is invented."""

from adjudication.ingestion.normalizer import normalize as norm
from adjudication.ingestion.workbook_loader import source


def propose(tables, ref):
    targets, sources = set(), []
    for row in tables.get("07_Alias_Observations", []):
        if (
            row["entity_kind"] == "PRODUCT"
            and row["same_real_world_thing"] == "Y"
            and norm(ref)
            and norm(ref) in (norm(row["string_a"]), norm(row["string_b"]))
        ):
            targets.update((norm(row["string_a"]), norm(row["string_b"])))
            sources.append(source(row))
    return targets, sources
