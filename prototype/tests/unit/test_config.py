import os
import unittest
from pathlib import Path
from unittest.mock import patch

from sentinel.config import output_directory


class ConfigTests(unittest.TestCase):
    def test_default_and_explicit_output_directory(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(output_directory(), Path('prototype/output'))
        with patch.dict(os.environ, {'SENTINEL_OUTPUT': 'private-output'}):
            self.assertEqual(output_directory(), Path('private-output'))

    def test_blank_output_is_rejected(self):
        with patch.dict(os.environ, {'SENTINEL_OUTPUT': ' '}):
            with self.assertRaises(ValueError):
                output_directory()
