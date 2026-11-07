"""Fail-closed dependency stub: indexes are not actual controlled document bytes."""


class DocumentStub:
    available = False

    def fetch(self, tenant, document_id):
        return {
            "tenant": tenant,
            "document_id": document_id,
            "available": False,
            "reason": "Controlled source bytes not supplied; manual retrieval required",
        }
