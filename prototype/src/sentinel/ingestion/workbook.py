"""Small XLSX table reader with hardened XML parsing."""

from __future__ import annotations

import hashlib
import posixpath
import re
import zipfile
from defusedxml import ElementTree as ET
from pathlib import Path
from typing import Any

_MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
_DOC_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
_CELL_REF = re.compile(r"^([A-Z]+)")


def _column_number(reference: str) -> int:
    match = _CELL_REF.match(reference.upper())
    if not match:
        raise ValueError(f"Invalid Excel cell reference: {reference!r}")
    number = 0
    for char in match.group(1):
        number = number * 26 + ord(char) - ord("A") + 1
    return number


def _shared_strings(archive: zipfile.ZipFile) -> list[str]:
    try:
        root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    except KeyError:
        return []
    return ["".join(node.text or "" for node in item.iter(f"{{{_MAIN_NS}}}t")) for item in root]


def _cell_text(cell: ET.Element, shared: list[str]) -> str:
    kind = cell.get("t")
    if kind == "inlineStr":
        inline = cell.find(f"{{{_MAIN_NS}}}is")
        if inline is None:
            return ""
        return "".join(node.text or "" for node in inline.iter(f"{{{_MAIN_NS}}}t"))

    value = cell.find(f"{{{_MAIN_NS}}}v")
    if value is None or value.text is None:
        return ""
    raw = value.text
    if kind == "s":
        try:
            return shared[int(raw)]
        except (ValueError, IndexError):
            raise ValueError(f"Invalid shared string index: {raw!r}") from None
    return raw


def _worksheet_rows(archive: zipfile.ZipFile, target: str, shared: list[str]) -> list[tuple[int, list[str]]]:
    root = ET.fromstring(archive.read(target))
    parsed: list[tuple[int, list[str]]] = []
    for row in root.iter(f"{{{_MAIN_NS}}}row"):
        row_number = int(row.get("r", "0"))
        values: dict[int, str] = {}
        for cell in row.findall(f"{{{_MAIN_NS}}}c"):
            reference = cell.get("r")
            if reference:
                values[_column_number(reference)] = _cell_text(cell, shared)
        if values:
            parsed.append((row_number, [values.get(column, "") for column in range(1, max(values) + 1)]))
    return parsed


def _sheet_targets(archive: zipfile.ZipFile) -> list[tuple[str, str]]:
    workbook_path = "xl/workbook.xml"
    workbook = ET.fromstring(archive.read(workbook_path))
    relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    targets = {
        relationship.get("Id"): relationship.get("Target")
        for relationship in relationships.findall(f"{{{_PKG_REL_NS}}}Relationship")
        if relationship.get("Type", "").endswith("/worksheet")
    }

    sheets: list[tuple[str, str]] = []
    for sheet in workbook.iter(f"{{{_MAIN_NS}}}sheet"):
        relationship_id = sheet.get(f"{{{_DOC_REL_NS}}}id")
        target = targets.get(relationship_id)
        if not target:
            continue
        if target.startswith("/"):
            worksheet_path = target.lstrip("/")
        else:
            worksheet_path = posixpath.normpath(posixpath.join(posixpath.dirname(workbook_path), target))
        sheets.append((sheet.get("name", ""), worksheet_path))
    return sheets


def load(path: str | Path) -> dict[str, list[dict[str, Any]]]:
    """Load every workbook sheet into row dictionaries keyed by its tab name.

    The first non-empty worksheet row is treated as the header. Values remain
    strings and rows retain their original Excel row number in ``_row``.
    """
    result: dict[str, list[dict[str, Any]]] = {}
    with zipfile.ZipFile(path) as archive:
        shared = _shared_strings(archive)
        for name, target in _sheet_targets(archive):
            rows = _worksheet_rows(archive, target, shared)
            if not rows:
                result[name] = []
                continue

            _, header_values = rows[0]
            header_width = max(len(values) for _, values in rows)
            headers: list[str] = []
            for index in range(1, header_width + 1):
                value = header_values[index - 1] if index <= len(header_values) else ""
                header = value if value else f"_col_{index}"
                if header in headers:
                    suffix = 2
                    while f"{header}_{suffix}" in headers:
                        suffix += 1
                    header = f"{header}_{suffix}"
                headers.append(header)

            records: list[dict[str, Any]] = []
            for row_number, values in rows[1:]:
                if not any(value != "" for value in values):
                    continue
                record = {header: values[index] if index < len(values) else "" for index, header in enumerate(headers)}
                record["_row"] = row_number
                records.append(record)
            result[name] = records
    return result


def sha256(path: str | Path) -> str:
    """Return the lowercase SHA-256 hex digest of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
