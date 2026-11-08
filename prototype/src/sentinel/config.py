"""Local output configuration; .env files are never loaded implicitly."""
import os
from pathlib import Path


def output_directory():
    value = os.environ.get('SENTINEL_OUTPUT', 'prototype/output').strip()
    if not value:
        raise ValueError('SENTINEL_OUTPUT must not be blank')
    return Path(value)
