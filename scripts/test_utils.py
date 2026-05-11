#!/usr/bin/env python3
"""Smoke tests for PointPivot Markdown parsers.

Run:
  .venv/bin/python scripts/test_utils.py
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

from utils import get_unverified_ips, parse_index, parse_seed_ips  # noqa: E402


def services(entry) -> set[str]:
    return {s.strip() for s in entry.service.split(',') if s.strip()}


class ParserSmokeTests(unittest.TestCase):
    def test_pos_entries_are_excluded_from_default_seed_parse(self) -> None:
        default_entries = parse_seed_ips()
        all_entries = parse_seed_ips(include_pos=True)
        pos_entries = [e for e in all_entries if 'pos' in services(e)]

        self.assertGreater(len(pos_entries), 0)
        self.assertFalse(any('pos' in services(e) for e in default_entries))
        self.assertIn('202.8.191.102', {e.ip for e in pos_entries})

    def test_cluster3_reverse_pivot_section_is_parsed(self) -> None:
        cluster3_ips = {e.ip for e in parse_index() if 'Cluster#3' in e.cluster}

        self.assertIn('118.235.12.181', cluster3_ips)
        self.assertIn('39.7.230.236', cluster3_ips)
        self.assertGreaterEqual(len(cluster3_ips), 14)

    def test_default_unverified_batch_does_not_include_pos(self) -> None:
        pos_ips = {
            e.ip
            for e in parse_seed_ips(include_pos=True)
            if 'pos' in services(e)
        }

        self.assertFalse(set(get_unverified_ips()) & pos_ips)
        self.assertIn('202.8.191.102', set(get_unverified_ips('pos')))

    def test_tier2_queue_does_not_contain_pos_ips(self) -> None:
        queue = ROOT / 'data' / 'tier2_queue.md'
        if not queue.exists():
            return

        queued_ips = set(re.findall(r'\b\d{1,3}(?:\.\d{1,3}){3}\b', queue.read_text()))
        pos_ips = {
            e.ip
            for e in parse_seed_ips(include_pos=True)
            if 'pos' in services(e)
        }
        self.assertFalse(queued_ips & pos_ips)


if __name__ == '__main__':
    unittest.main(verbosity=2)
