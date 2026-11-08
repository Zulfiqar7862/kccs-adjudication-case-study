"""Assessment kernel against the public anonymized workbook and, when configured, the supplied pack."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from sentinel.evidence.assessment import AccessDenied, assess, extract_date
from sentinel.workflow.service import Engine

ROOT = Path(__file__).resolve().parents[3]
PUBLIC = ROOT / 'data' / 'anonymized-evaluation.xlsx'


class PublicWorkbookAssessmentTests(unittest.TestCase):
    def test_every_public_event_abstains_and_hashes_deterministically(self):
        with tempfile.TemporaryDirectory() as directory:
            engine = Engine(Path(directory) / 'public.db')
            engine.ingest(PUBLIC)
            tables = engine.tables()
            first = tables['01_Excursion_Events'][0]
            one = assess(tables, first['event_id'], principal_tenant=first['tenant_code'])
            self.assertEqual(one['conclusion']['disposition'], 'ABSTAIN')
            self.assertEqual(one['manifest']['workbook_sha256'], tables['_source_hash'])
            self.assertEqual(one['assessment_sha256'], assess(tables, first['event_id'])['assessment_sha256'])
            other_tenant = next(e['tenant_code'] for e in tables['01_Excursion_Events'] if e['tenant_code'] != first['tenant_code'])
            with self.assertRaises(AccessDenied):
                assess(tables, first['event_id'], principal_tenant=other_tenant)
            overlaps = sum(1 for e in tables['01_Excursion_Events'] if assess(tables, e['event_id'])['evidence']['sop']['conflicts'])
            self.assertGreater(overlaps, 0, 'The anonymized pack preserves overlapping SOP windows; none were detected')

    def test_cli_assess_all_and_package_verification(self):
        with tempfile.TemporaryDirectory() as directory:
            def run(*args, expected=0):
                result = subprocess.run([sys.executable, '-m', 'sentinel', '--db', 'public.db', *args], cwd=directory,
                                        capture_output=True, text=True, timeout=120)
                self.assertEqual(result.returncode, expected, result.stderr + result.stdout)
                return result
            run('import', str(PUBLIC))
            run('assess-all', '--compare-history', '--output', 'summary.json')
            summary = json.loads((Path(directory) / 'summary.json').read_text(encoding='utf-8'))
            self.assertEqual(summary['total'], 420)
            self.assertEqual(summary['disposition'], {'ABSTAIN': 420})
            self.assertIn('Not a population accuracy estimate', summary['notice'])
            self.assertIn('final_disposition', summary['review_candidates']['historical_fields_read_here_only'])
            event = next(e for e in Engine(Path(directory) / 'public.db').tables()['01_Excursion_Events'])
            run('assess', '--tenant', event['tenant_code'], '--event', event['event_id'], '--output', 'pkg.json')
            run('verify-assessment', 'pkg.json')
            wrong = run('assess', '--tenant', 'NOT-A-TENANT', '--event', event['event_id'], expected=1)
            self.assertNotIn('Traceback', wrong.stderr)
            bundle = json.loads((Path(directory) / 'pkg.json').read_text(encoding='utf-8'))
            bundle['assessment']['missing_inputs'] = []
            (Path(directory) / 'pkg.json').write_text(json.dumps(bundle), encoding='utf-8')
            run('verify-assessment', 'pkg.json', expected=1)


class ConfiguredWorkbookAssessmentTests(unittest.TestCase):
    @unittest.skipUnless(os.environ.get('SENTINEL_WORKBOOK'), 'SENTINEL_WORKBOOK is not configured')
    def test_supplied_pack_exhibits_documented_failure_modes(self):
        with tempfile.TemporaryDirectory() as directory:
            engine = Engine(Path(directory) / 'private.db')
            engine.ingest(Path(os.environ['SENTINEL_WORKBOOK']))
            tables = engine.tables()
            redacted = extract_date(tables) is None  # README tab redacted ⇒ anonymized evaluation copy
            seen = {'bulletin': 0, 'presentation': 0, 'overlap': 0, 'untagged': 0, 'alias': 0}
            hidden_before_bulletin = 0
            for event in tables['01_Excursion_Events']:
                result = assess(tables, event['event_id'])
                self.assertEqual(result['conclusion']['disposition'], 'ABSTAIN')
                self.assertNotIn('final_disposition', result['inputs']['event_fields_read'])
                telemetry = result['evidence']['telemetry']
                if any(b.get('effect') for b in telemetry['bulletins']):
                    seen['bulletin'] += 1
                    early = assess(tables, event['event_id'], known_at='2026-01-01T00:00:00+00:00')
                    hidden_before_bulletin += all(b.get('status') == 'NOT_KNOWN_AT_CUTOFF' for b in early['evidence']['telemetry']['bulletins'])
                seen['presentation'] += any('Presentation mismatch' in f for c in result['evidence']['stability']['candidates'] for f in c['flags'])
                seen['overlap'] += bool(result['evidence']['sop']['conflicts'])
                seen['untagged'] += telemetry['source_system'].upper() == 'SYS-03'
                seen['alias'] += any(e['kind'] == 'PRODUCT' and e['unverified_alias_candidates'] for e in result['entities'])
            for mode, count in seen.items():
                if redacted and mode != 'overlap':
                    continue  # the anonymized copy strips firmware, readability, constraints and incidents
                self.assertGreater(count, 0, f'Expected the supplied pack to exhibit {mode}')
            self.assertEqual(hidden_before_bulletin, seen['bulletin'], 'Bulletin knowledge leaked into pre-bulletin replay')


if __name__ == '__main__':
    unittest.main()
