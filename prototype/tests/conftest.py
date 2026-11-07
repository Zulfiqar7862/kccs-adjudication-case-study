"""All unit tests use hand-made public fixtures; no private source is required."""

from pathlib import Path

import pytest
from adjudication.ingestion.workbook_loader import Pack
from adjudication.rules.engine import EvidenceKernel

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def fixtures_dir():
    return ROOT / "prototype/tests/fixtures"


@pytest.fixture
def pack(fixtures_dir):
    return Pack.from_csv(fixtures_dir)


@pytest.fixture
def kernel(pack):
    return EvidenceKernel(pack)
