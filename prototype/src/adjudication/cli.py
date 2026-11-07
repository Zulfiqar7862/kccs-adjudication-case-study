"""CLI: actual workbook or synthetic CSV fixtures to deterministic evidence dossiers."""

import argparse
import json
from pathlib import Path

from adjudication.config import Config
from adjudication.ingestion.workbook_loader import Pack
from adjudication.reporting.exporters import export
from adjudication.reporting.report_builder import build_report


def run(workbook=None, output="prototype/output", fixtures=None):
    pack = Pack.from_csv(fixtures) if fixtures is not None else Pack(workbook)
    report = build_report(pack)
    export(report, pack, output)
    return report


def main(argv=None):
    defaults = Config.from_env()
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--workbook", type=Path)
    source.add_argument("--fixtures", type=Path)
    parser.add_argument("--out", type=Path, default=defaults.output)
    args = parser.parse_args(argv)
    report = run(args.workbook or defaults.workbook, args.out, args.fixtures)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
