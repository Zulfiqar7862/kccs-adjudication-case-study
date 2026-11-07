"""Read every workbook sheet and validate events; print only safe aggregate metadata."""

import argparse
import json

from adjudication.ingestion.workbook_loader import Pack


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook")
    args = parser.parse_args()
    pack = Pack(args.workbook)
    print(
        json.dumps(
            {
                "sheet_count": len(pack.tables),
                "events": len(pack.events),
                "columns_per_sheet": {k: v["columns"] for k, v in pack.inventory.items()},
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
