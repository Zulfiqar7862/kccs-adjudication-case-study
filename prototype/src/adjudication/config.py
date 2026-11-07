"""Non-secret runtime configuration; environment settings can be overridden by CLI."""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    workbook: Path
    output: Path

    @classmethod
    def from_env(cls):
        return cls(
            Path(os.getenv("ADJUDICATION_WORKBOOK", "data/KCCS_Sentinel_Reference_Data_Pack.xlsx")),
            Path(os.getenv("ADJUDICATION_OUTPUT", "prototype/output")),
        )
