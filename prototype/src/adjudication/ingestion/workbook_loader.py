"""Read-only ingestion with original cell coordinates and immutable input fingerprint."""

import hashlib
import json
from pathlib import Path

import openpyxl
from openpyxl.utils import get_column_letter

from adjudication.ingestion.validators import validate_tables


class Pack:
    def __init__(self, path):
        self.path = Path(path)
        self.sha256 = hashlib.sha256(self.path.read_bytes()).hexdigest()
        formulas = openpyxl.load_workbook(self.path, data_only=False)
        values = openpyxl.load_workbook(self.path, data_only=True)
        self.tables = {}
        self.inventory = {}
        self.cells = {}
        for sheet in formulas:
            name = sheet.title
            self.cells[name] = {c.coordinate: c.value for row in sheet for c in row if c.value is not None}
            headers = [c.value for c in sheet[1]]
            self.tables[name] = [
                dict(zip(headers, row), _sheet=name, _row=i) for i, row in enumerate(values[name].values, 1) if i > 1
            ]
            self.inventory[name] = {
                "rows_including_header": sheet.max_row,
                "columns": sheet.max_column,
                "headers": headers,
                "nonempty_cells": len(self.cells[name]),
                "formulas": [c.coordinate for row in sheet for c in row if c.data_type == "f"],
                "error_cells": [c.coordinate for row in sheet for c in row if c.data_type == "e"],
                "merged_ranges": [str(x) for x in sheet.merged_cells.ranges],
                "charts": len(sheet._charts),
                "images": len(sheet._images),
                "blank_by_column": {
                    get_column_letter(i): sum(sheet.cell(r, i).value is None for r in range(2, sheet.max_row + 1))
                    for i in range(1, sheet.max_column + 1)
                },
            }
        formulas.close()
        values.close()
        self.events = self.tables["01_Excursion_Events"]
        validate_tables(self.tables)

    @classmethod
    def from_csv(cls, directory):
        import csv

        self = cls.__new__(cls)
        self.path = Path(directory)
        self.tables = {}
        content = b""
        numeric = {"max_temp_c", "min_temp_c", "gateway_gap_min", "reg_window_hours", "hours_to_notification"}
        for filename, table in (
            ("sample_events.csv", "01_Excursion_Events"),
            ("sample_products.csv", "02_Product_Master"),
        ):
            path = self.path / filename
            content += path.read_bytes()
            with path.open(newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.tables[table] = [
                dict(
                    {k: (None if v == "" else float(v) if k in numeric else v) for k, v in row.items()},
                    _sheet=table,
                    _row=i,
                )
                for i, row in enumerate(rows, 2)
            ]
        for table in ("05_SOP_Index", "06_Stability_Index", "07_Alias_Observations"):
            self.tables[table] = []
        self.sha256 = hashlib.sha256(content).hexdigest()
        self.inventory = {}
        self.cells = {}
        self.events = self.tables["01_Excursion_Events"]
        validate_tables(self.tables)
        return self

    def audit(self):
        return {
            "sheet_count": len(self.tables),
            "events": len(self.events),
            "inventory": self.inventory,
            "workbook_sha256": self.sha256,
        }


def source(row):
    return f"{row['_sheet']}!A{row['_row']}"


def dump_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, default=str) + "\n")
