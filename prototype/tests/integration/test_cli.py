"""Exercise installed CLI commands in separate processes without private data."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class CliTests(unittest.TestCase):
    def run_cli(self, directory, *args, expected=0):
        result = subprocess.run([sys.executable, '-m', 'sentinel', *args], cwd=directory,
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, expected, result.stderr + result.stdout)
        return result

    def test_sample_import_report_export_and_private_credentials(self):
        with tempfile.TemporaryDirectory() as directory:
            self.run_cli(directory, 'sample')
            first = json.loads(self.run_cli(directory, 'import', 'prototype/output/sample.xlsx').stdout)
            self.assertGreater(first['created'], 0)
            replay = json.loads(self.run_cli(directory, 'import', 'prototype/output/sample.xlsx').stdout)
            self.assertTrue(replay['replayed'])
            written = self.run_cli(directory, 'report', '--output', 'prototype/output/report.json')
            self.assertEqual(json.loads(written.stdout), {'written': 'prototype/output/report.json'})
            report = json.loads((Path(directory) / 'prototype/output/report.json').read_text(encoding='utf-8'))
            self.assertEqual(report['states'], {'WAITING_EVIDENCE': first['created']})
            self.assertNotIn('cases', written.stdout)
            case = report['cases'][0]
            unknown = self.run_cli(directory, 'tick', '--tenant', 'NOT-IMPORTED', expected=1)
            self.assertIn('Unknown tenant', unknown.stderr)
            ticked = json.loads(self.run_cli(directory, 'tick', '--tenant', case['tenant']).stdout)
            self.assertTrue(ticked['regulators_not_notified'])
            self.run_cli(directory, 'export', '--tenant', case['tenant'], '--case', case['id'],
                         '--output', 'prototype/output/audit.json')
            self.assertTrue(json.loads(self.run_cli(directory, 'verify', 'prototype/output/audit.json').stdout)['valid'])
            path = Path(directory) / 'prototype/output/audit.json'
            audit = json.loads(path.read_text(encoding='utf-8'))
            audit['state'] = 'DISPOSED'
            path.write_text(json.dumps(audit), encoding='utf-8')
            self.assertFalse(json.loads(self.run_cli(directory, 'verify', 'prototype/output/audit.json', expected=1).stdout)['valid'])
            created = self.run_cli(directory, 'credentials', '--tenant', case['tenant'])
            path = Path(directory) / 'prototype/output/local-credentials.json'
            credentials = json.loads(path.read_text(encoding='utf-8'))
            self.assertEqual(len(credentials), 5)
            for token in credentials:
                self.assertNotIn(token, created.stdout)
                self.assertGreaterEqual(len(token), 32)
            if os.name != 'nt':
                self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            duplicate = self.run_cli(directory, 'credentials', '--tenant', case['tenant'], expected=1)
            self.assertIn('already exists', duplicate.stderr)
            self.assertEqual(json.loads(path.read_text(encoding='utf-8')), credentials)
            missing = self.run_cli(directory, 'serve', '--credentials', 'prototype/output/absent.json', expected=1)
            self.assertIn('run `python -m sentinel credentials', missing.stderr)

    def test_missing_input_and_malformed_export_fail_cleanly(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_cli(directory, 'import', 'missing.xlsx', expected=1)
            self.assertNotIn('Traceback', result.stderr)
            path = Path(directory) / 'invalid.json'
            path.write_text('{}', encoding='utf-8')
            self.assertFalse(json.loads(self.run_cli(directory, 'verify', str(path), expected=1).stdout)['valid'])

    def test_output_environment_and_explicit_path_override(self):
        with tempfile.TemporaryDirectory() as directory:
            env = dict(os.environ, SENTINEL_OUTPUT='custom-output')
            result = subprocess.run([sys.executable, '-m', 'sentinel', 'sample'],
                                    cwd=directory, env=env, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((Path(directory) / 'custom-output/sample.xlsx').is_file())
            result = subprocess.run([sys.executable, '-m', 'sentinel', 'sample', '--output', 'explicit.xlsx'],
                                    cwd=directory, env=env, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((Path(directory) / 'explicit.xlsx').is_file())

    def test_http_lifecycle_demo(self):
        with tempfile.TemporaryDirectory() as directory:
            report = json.loads(self.run_cli(directory, 'demo').stdout)
            self.assertEqual(report['result'], 'PASS')
            self.assertTrue(report['prior_revision_preserved'])
            self.assertTrue(report['regulators_not_notified'])
            self.assertEqual(report['reminder_failure_and_retry'], 'PASS')

    def test_explained_demo_narrates_each_step(self):
        with tempfile.TemporaryDirectory() as directory:
            text = self.run_cli(directory, 'demo', '--explain').stdout
            narration, _, summary = text.partition('{')
            self.assertEqual([line[:6] for line in narration.splitlines()], [f'Step {n}' for n in range(1, 10)])
            self.assertEqual(json.loads('{' + summary)['result'], 'PASS')
