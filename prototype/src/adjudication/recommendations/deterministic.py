"""A useful evidence task list, never a pharmaceutical disposition."""


def recommend(issues):
    return {"action": "REQUEST_VERIFIED_EVIDENCE", "requires_human": True, "blocker_count": len(set(issues))}
