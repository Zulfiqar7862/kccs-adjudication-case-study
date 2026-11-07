"""Pure orchestration of tenant-scoped evidence eligibility and independent clock replay."""

from adjudication.domain.models import Dossier
from adjudication.evidence.document_stub import DocumentStub
from adjudication.evidence.gaps import BASE_GAPS
from adjudication.evidence.service import resolve_study
from adjudication.identity.resolver import resolve_product
from adjudication.recommendations.assistant_stub import AssistantStub
from adjudication.recommendations.guardrails import enforce
from adjudication.rules.policies import temperature_interval
from adjudication.rules.versioning import manifest
from adjudication.temporal.clock import notification
from adjudication.temporal.effective_dating import effective_sops


class EvidenceKernel:
    def __init__(self, pack):
        self.pack = pack

    def evaluate(self, event):
        tenant = event["tenant_code"]
        product = resolve_product(self.pack.tables, tenant, event["product_ref_as_received"])
        issues = list(BASE_GAPS)
        if product["status"] != "EXACT_SOURCE_MATCH":
            issues.append("PRODUCT_" + product["status"])
        studies = [resolve_study(self.pack.tables, p) for p in product["candidates"]]
        issues += [issue for study in studies for issue in study["issues"]]
        sops = effective_sops(self.pack.tables, tenant, event["excursion_start_utc"])
        if any(s["status"] == "AMBIGUOUS" for s in sops):
            issues.append("SOP_OVERLAP")
        if event["logger_fw"] == "TT-2.14.3":
            issues.append("CALIBRATION_UNCERTAINTY_0_TO_PLUS_1_8_C")
        if event["interpolated"] == "Y" or event["gateway_gap_min"] > 0:
            issues.append("MEASUREMENT_GAP_OR_INTERPOLATION")
        if event["source_system"] == "SYS-03":
            issues.append("BMS_PRODUCT_OCCUPANCY_UNVERIFIED")
        result = Dossier(event["event_id"], tenant, sorted(set(issues))).to_dict()
        result.update(
            product=product,
            studies=studies,
            sop_candidates=sops,
            temperature_max_interval_c=temperature_interval(event["max_temp_c"], event["logger_fw"]),
            temperature_min_interval_c=temperature_interval(event["min_temp_c"], event["logger_fw"]),
            notification=notification(event),
            manifest=manifest(self.pack, event["excursion_start_utc"]),
            event_source=f"{event['_sheet']}!A{event['_row']}",
            document_dependency=DocumentStub().fetch(tenant, "governing-documents"),
        )
        result["recommendation"] = AssistantStub().draft(result)
        return enforce(result)
