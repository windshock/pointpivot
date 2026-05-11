#!/usr/bin/env python3
"""Smoke tests for PointPivot Markdown parsers.

Run:
  .venv/bin/python scripts/test_utils.py
"""

from __future__ import annotations

import re
import os
import sys
import unittest
from contextlib import contextmanager
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

from search_providers import create_search_provider  # noqa: E402
from search_providers.base import SearchProvider, SearchProviderError, normalize_result  # noqa: E402
from search_providers.hybrid import HybridProvider  # noqa: E402
from utils import get_unverified_ips, parse_index, parse_seed_ips  # noqa: E402


def services(entry) -> set[str]:
    return {s.strip() for s in entry.service.split(',') if s.strip()}


@contextmanager
def without_env(*names: str):
    old = {name: os.environ.get(name) for name in names}
    for name in names:
        os.environ.pop(name, None)
    try:
        yield
    finally:
        for name, value in old.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


class FailingProvider(SearchProvider):
    name = 'failing'
    mode = 'failing'

    def search(self, query: str, max_results: int = 20) -> list[dict]:
        raise SearchProviderError('simulated failure')


class StaticProvider(SearchProvider):
    name = 'static'
    mode = 'static'

    def search(self, query: str, max_results: int = 20) -> list[dict]:
        return [
            normalize_result(
                title='result',
                href='https://example.test/result',
                body='body',
                provider=self.name,
                engine='test',
                query=query,
            )
        ][:max_results]


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

    def test_default_search_provider_is_ddg(self) -> None:
        with without_env('POINTPIVOT_SEARCH_PROVIDER'):
            provider = create_search_provider()
        self.assertEqual(provider.name, 'ddg')
        self.assertEqual(provider.mode, 'ddg')

    def test_normalized_search_result_marks_snippet_only(self) -> None:
        result = normalize_result(
            title='t',
            href='https://example.test',
            body='b',
            provider='searxng',
            engine='duckduckgo',
            query='"1.2.3.4"',
        )
        self.assertEqual(result['provider'], 'searxng')
        self.assertEqual(result['engine'], 'duckduckgo')
        self.assertEqual(result['query'], '"1.2.3.4"')
        self.assertEqual(result['evidence_level'], 'search_snippet_only')

    def test_hybrid_falls_back_when_searxng_fails(self) -> None:
        provider = HybridProvider(
            searxng=FailingProvider(),
            ddg=StaticProvider(),
            hybrid_mode='fallback',
        )
        results = provider.search('"1.2.3.4"')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['provider'], 'static')


if __name__ == '__main__':
    unittest.main(verbosity=2)
