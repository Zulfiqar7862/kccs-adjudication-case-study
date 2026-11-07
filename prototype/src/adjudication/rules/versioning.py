"""Immutable release identity; unknown historical transaction time stays explicit."""

from adjudication import __version__


def manifest(pack, valid_at):
    return {
        "engine": __version__,
        "rules": "eligibility-2",
        "input_sha256": pack.sha256,
        "reference_snapshot": "source extract; transaction history unavailable",
        "valid_at": valid_at,
        "model": "none",
        "api": "cli-v1",
    }
