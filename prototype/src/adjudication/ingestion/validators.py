"""Fail-fast fixture/workbook contracts; unknown clinical evidence is handled later."""

import math

from adjudication.exceptions import DataContractError
from adjudication.temporal.timezone import utc

REQUIRED_EVENT = {
    "event_id",
    "tenant_code",
    "alert_ts_utc",
    "excursion_start_utc",
    "product_ref_as_received",
    "logger_fw",
    "max_temp_c",
    "min_temp_c",
    "source_system",
    "gateway_gap_min",
    "interpolated",
}
REQUIRED_PRODUCT = {
    "tenant_code",
    "brand_as_labelled",
    "generic_inn",
    "internal_sku",
    "gtin",
    "legacy_code",
    "stability_study_ref",
}


def validate_tables(tables):
    for name, required in (("01_Excursion_Events", REQUIRED_EVENT), ("02_Product_Master", REQUIRED_PRODUCT)):
        if name not in tables:
            raise DataContractError("Required input table missing: " + name)
        for row in tables[name]:
            if required - row.keys():
                raise DataContractError("Required columns missing in " + name)
    ids = [row["event_id"] for row in tables["01_Excursion_Events"]]
    if any(not x for x in ids) or len(ids) != len(set(ids)):
        raise DataContractError("Missing or duplicate event_id")
    for row in tables["01_Excursion_Events"]:
        try:
            utc(row["alert_ts_utc"])
            utc(row["excursion_start_utc"])
            numbers = [float(row[k]) for k in ("min_temp_c", "max_temp_c", "gateway_gap_min")]
            if not all(math.isfinite(x) for x in numbers) or numbers[0] > numbers[1] or numbers[2] < 0:
                raise ValueError("Invalid numerical measurement")
            if not row["tenant_code"]:
                raise ValueError("Tenant required")
        except (ValueError, TypeError) as exc:
            raise DataContractError("Invalid event measurement/time/tenant") from exc
