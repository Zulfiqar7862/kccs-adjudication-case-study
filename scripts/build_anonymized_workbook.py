"""Rebuild a public evaluation copy; never copy source package parts or free text."""
import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from sentinel.evidence.analysis import parse_time
from sentinel.ingestion.workbook import load

NS = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
DOC_REL = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
CT = 'http://schemas.openxmlformats.org/package/2006/content-types'
IDENTIFIERS = {
    'event_id', 'shipment_ref', 'tenant_code', 'product_code', 'sap_material_no',
    'wms_sku', 'lims_code', 'facility_id', 'carrier_code', 'logger_id', 'batch_number',
    'contract_id', 'sop_id', 'study_id', 'stability_ref', 'gmp_license', 'reviewer_id',
    'override_id', 'incident_id', 'obs_id', 'question_id', 'raw_value', 'other_value',
    'product_ref_as_received', 'origin_ref_as_received', 'dest_ref_as_received',
    'carrier_ref_as_received', 'internal_sku', 'gtin', 'legacy_code',
    'stability_study_ref', 'study_ref', 'doc_id', 'record_id', 'log_id', 'case_ref',
    'system_id', 'ref', 'string_a', 'string_b', 'code_in_source', 'gmp_licence_ref',
    'brand_as_labelled', 'product_text_as_written', 'name_in_source',
}
DATES = {
    'excursion_start_utc', 'excursion_end_utc', 'alert_raised_utc', 'received_utc',
    'alert_ts_utc', 'last_updated', 'record_created', 'confirmed_on',
    'local_start', 'local_end', 'closed_utc', 'effective_from', 'effective_to', 'retired_date', 'date',
}
NUMBERS = {
    'duration_min': '60', 'readings_in_window': '60', 'gateway_gap_min': '0',
    'reg_window_hours': '72', 'duration_minutes': '60', 'min_temp_c': '2', 'max_temp_c': '9',
    'mean_temp_c': '5', 'time_above_8c_min': '30', 'time_below_2c_min': '0',
    'review_hours': '1', 'notification_window_h': '72', 'label_storage_min_c': '2',
    'label_storage_max_c': '8', 'max_permitted_excursion_c': '10',
    'max_permitted_excursion_min': '120', 'shelf_life_months': '12',
    'claim_window_days': '30', 'active_review_min': '30', 'systems_consulted': '2',
    'queue_wait_hours': '1', 'interruptions': '0', 'minutes_typical': '10',
    'what_pct_of_cases': '50', 'overrule_rate': '0',
}
FLAGS = {'telemetry_gap', 'interpolated', 'repeat_excursion', 'regulator_reportable',
         'has_site_annex', 'signature_required', 'active', 'same_real_world_entity'}
DISPOSITIONS = {'RELEASE', 'RELEASE_WITH_NOTE', 'SHORTEN_EXPIRY', 'QUARANTINE',
                'REWORK', 'RETURN', 'DESTROY'}


def safe_time(value):
    try:
        return parse_time(value)
    except ValueError:
        return None


def rebuild(source, destination):
    if Path(source).resolve() == Path(destination).resolve():
        raise ValueError('Output must not overwrite the private source')
    tables = load(source)
    # Only reviewed schema labels are permitted in a publishable output.
    schema = json.loads(Path(__file__).with_name('evaluation_workbook_schema.json').read_text())
    if set(tables) != set(schema):
        raise ValueError('Unexpected workbook sheets; review schema before publishing')
    for sheet, rows in tables.items():
        if any(set(row) - {'_row'} != set(schema[sheet]) for row in rows):
            raise ValueError('Unexpected workbook columns; review schema before publishing')
    identifiers = {}
    instants = set()
    for rows in tables.values():
        for row in rows:
            for key, value in row.items():
                if key in IDENTIFIERS and value:
                    identifiers.setdefault(str(value), f'REF-{len(identifiers) + 1:05d}')
                if key in DATES and value:
                    parsed = safe_time(value)
                    if parsed:
                        instants.add(parsed)
    times = {t: (datetime(2020, 1, 1, tzinfo=timezone.utc) + timedelta(hours=i)).isoformat()
             for i, t in enumerate(sorted(instants))}

    def transform(key, value):
        if value == '' or value is None:
            return ''
        if key in IDENTIFIERS:
            return identifiers[str(value)]
        if key in DATES:
            return times.get(safe_time(value), '')
        if key in NUMBERS:
            return NUMBERS[key]
        if key in FLAGS:
            return str(value) if str(value) in {'Y', 'N'} else 'UNKNOWN'
        if key in {'final_disposition', 'engine_recommendation', 'reviewer_decision'}:
            return str(value) if str(value) in DISPOSITIONS else 'UNKNOWN'
        if key == 'who_signs_a_disposition':
            return 'Synthetic site QA and corporate QA (dual)'
        if key in {'timezone', 'timezone_in_source'}:
            return 'UTC'
        return 'REDACTED - evaluation copy'

    output = {sheet: [[transform(key, row.get(key, '')) for key in schema[sheet]]
                      for row in rows] for sheet, rows in tables.items()}
    notice = ('ANONYMIZED EVALUATION COPY: source structure and row counts retained; '
              'identifiers replaced; narratives removed; dates and measurements synthetic. '
              'Not the original workbook, clinical evidence, or outcome-equivalent data.')
    output['00_README'] = [[notice] for _ in tables['00_README']]
    write_xlsx(destination, schema, output)


def write_xlsx(destination, schema, tables):
    workbook = ET.Element(f'{{{NS}}}workbook')
    sheets = ET.SubElement(workbook, f'{{{NS}}}sheets')
    relationships = ET.Element('Relationships', xmlns=REL)
    content = ET.Element('Types', xmlns=CT)
    ET.SubElement(content, 'Default', Extension='rels', ContentType='application/vnd.openxmlformats-package.relationships+xml')
    ET.SubElement(content, 'Default', Extension='xml', ContentType='application/xml')
    ET.SubElement(content, 'Override', PartName='/xl/workbook.xml',
                  ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml')
    parts = {}
    for index, (name, headers) in enumerate(schema.items(), 1):
        ET.SubElement(sheets, f'{{{NS}}}sheet', {'name': name, 'sheetId': str(index), f'{{{DOC_REL}}}id': f'rId{index}'})
        ET.SubElement(relationships, 'Relationship', Id=f'rId{index}', Type=f'{DOC_REL}/worksheet',
                      Target=f'worksheets/sheet{index}.xml')
        ET.SubElement(content, 'Override', PartName=f'/xl/worksheets/sheet{index}.xml',
                      ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml')
        sheet = ET.Element(f'{{{NS}}}worksheet')
        data = ET.SubElement(sheet, f'{{{NS}}}sheetData')
        for row_index, values in enumerate([headers, *tables[name]], 1):
            row = ET.SubElement(data, f'{{{NS}}}row', r=str(row_index))
            for col, value in enumerate(values, 1):
                letters, n = '', col
                while n:
                    n, digit = divmod(n - 1, 26)
                    letters = chr(65 + digit) + letters
                cell = ET.SubElement(row, f'{{{NS}}}c', r=f'{letters}{row_index}', t='inlineStr')
                ET.SubElement(ET.SubElement(cell, f'{{{NS}}}is'), f'{{{NS}}}t').text = str(value)
        parts[f'xl/worksheets/sheet{index}.xml'] = sheet
    root_rels = ET.Element('Relationships', xmlns=REL)
    ET.SubElement(root_rels, 'Relationship', Id='rId1', Type=f'{DOC_REL}/officeDocument', Target='xl/workbook.xml')
    parts.update({'[Content_Types].xml': content, '_rels/.rels': root_rels,
                  'xl/workbook.xml': workbook, 'xl/_rels/workbook.xml.rels': relationships})
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(destination, 'w', compression=ZIP_DEFLATED) as archive:
        for name, element in parts.items():
            info = ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            archive.writestr(info, ET.tostring(element, encoding='utf-8', xml_declaration=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if args.source.resolve() == args.output.resolve():
        parser.error('Output must not overwrite the private source')
    rebuild(args.source, args.output)
