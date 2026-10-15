"""Prove named safety fixtures fail when the guarantee is deliberately removed."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class NegativeControls(unittest.TestCase):
    def test_stale_check_guard_is_observable(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            for name in ('think_loop', 'tests', 'examples'):
                shutil.copytree(ROOT / name, target / name, ignore=shutil.ignore_patterns('__pycache__'))
            core = target / 'think_loop/core.py'
            original = core.read_text()
            broken = original.replace(" and c.get('head') == head", '')
            self.assertNotEqual(original, broken)
            core.write_text(broken)
            env = dict(os.environ, PYTHONPATH=str(target))
            run = subprocess.run([sys.executable, '-m', 'unittest',
                                  'tests.test_loop.PolicyTests.test_stale_check_unknown'],
                                 cwd=target, env=env, capture_output=True, text=True, timeout=30)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn('FAIL:', run.stderr)
            self.assertNotIn('ERROR:', run.stderr)
