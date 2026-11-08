"""Portable local/CI check entry point. Private tests are opt-in via environment."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for arguments in [
    ['-m', 'compileall', '-q', 'prototype/src', 'prototype/tests', 'scripts'],
    ['-m', 'unittest', 'discover', '-s', 'prototype/tests', '-v'],
    ['-m', 'sentinel', 'demo'],
]:
    result = subprocess.run([sys.executable, *arguments], cwd=ROOT, check=False)
    if result.returncode:
        raise SystemExit(result.returncode)
print('All requested checks passed. Private integrations are skipped unless SENTINEL_WORKBOOK is set.')
