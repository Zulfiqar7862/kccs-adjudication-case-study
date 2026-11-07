"""Categorical provenance strength, deliberately not an invented probability."""


def confidence_for(status):
    return {"EXACT_SOURCE_MATCH": "SOURCE_ONLY", "UNVERIFIED_ALIAS": "UNVERIFIED", "AMBIGUOUS": "CONFLICT"}.get(
        status, "NONE"
    )
