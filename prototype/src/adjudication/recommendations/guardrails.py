"""Enforce the prototype's no-disposition/no-autoclosure boundary."""


def enforce(dossier):
    if dossier.get("signed_disposition") is not None or dossier.get("proposed_auto_close"):
        raise ValueError("Clinical disposition and auto-closure are outside this prototype")
    if dossier["status"] != "NEEDS_EVIDENCE":
        raise ValueError("Unknown evidence status")
    return dossier
