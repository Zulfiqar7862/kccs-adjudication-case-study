"""Regression checks for the reviewed public evaluation artifact."""
import re
import runpy
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from defusedxml import ElementTree as ET
from sentinel.ingestion.workbook import load
from sentinel.workflow.service import Engine, verify_export

ROOT = Path(__file__).resolve().parents[3]
WORKBOOK = ROOT / 'data' / 'anonymized-evaluation.xlsx'


class PublicWorkbookTests(unittest.TestCase):
    def test_builder_cannot_overwrite_its_source(self):
        rebuild = runpy.run_path(str(ROOT / 'scripts' / 'build_anonymized_workbook.py'))['rebuild']
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'private.xlsx'
            source.write_bytes(b'private source must remain unchanged')
            with self.assertRaisesRegex(ValueError, 'must not overwrite'):
                rebuild(source, source)
            self.assertEqual(source.read_bytes(), b'private source must remain unchanged')

    def test_public_workbook_import_and_replay(self):
        tables = load(WORKBOOK)
        self.assertEqual(len(tables), 15)
        self.assertEqual(len(tables['01_Excursion_Events']), 420)
        with tempfile.TemporaryDirectory() as directory:
            engine = Engine(Path(directory) / 'evaluation.db')
            self.assertEqual(engine.ingest(WORKBOOK)['created'], 420)
            self.assertTrue(engine.ingest(WORKBOOK)['replayed'])
            for event in tables['01_Excursion_Events']:
                case = engine.get_case(event['tenant_code'], event['event_id'])
                self.assertEqual(case['state'], 'WAITING_EVIDENCE')
                self.assertIsNone(case['packet']['disposition'])
                self.assertTrue(case['packet']['analysis']['blockers'])
                self.assertTrue(verify_export(engine.export(event['tenant_code'], event['event_id'])))

    def test_package_contains_only_reviewed_plain_text_parts(self):
        with ZipFile(WORKBOOK) as archive:
            expected = {'[Content_Types].xml', '_rels/.rels', 'xl/workbook.xml', 'xl/_rels/workbook.xml.rels'}
            expected.update(f'xl/worksheets/sheet{i}.xml' for i in range(1, 16))
            self.assertEqual(set(archive.namelist()), expected)
            for name in archive.namelist():
                root = ET.fromstring(archive.read(name))
                for element in root.iter():
                    self.assertNotIn(element.tag.split('}')[-1], {'f', 'hyperlink', 'externalReference'})
                    self.assertNotIn(element.attrib.get('state'), {'hidden', 'veryHidden'})
                    self.assertNotEqual(element.attrib.get('TargetMode'), 'External')
            tables = load(WORKBOOK)
            for rows in tables.values():
                for row in rows:
                    for key, value in row.items():
                        if key.endswith('_id') or key in {'tenant_code', 'product_code', 'stability_ref'}:
                            self.assertTrue(not value or re.fullmatch(r'REF-\d{5}', str(value)), key)
