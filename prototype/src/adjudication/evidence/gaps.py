"""Universal missing prerequisites and flat gap exports."""

BASE_GAPS = (
    "RAW_SERIES_NOT_PROVIDED",
    "SOP_CONTENT_AND_SITE_SCOPE_UNVERIFIED",
    "BATCH_HISTORY_NOT_PROVIDED",
    "EXTRACT_NOT_HISTORICAL_TRANSACTION_HISTORY",
)


def gap_rows(cases):
    return [
        {"event_id": c["event_id"], "tenant_code": c["tenant_code"], "gap": gap} for c in cases for gap in c["issues"]
    ]
