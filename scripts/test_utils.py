#!/usr/bin/env python3
"""Smoke tests for PointPivot Markdown parsers.

Run:
  .venv/bin/python scripts/test_utils.py
"""

from __future__ import annotations

import re
import os
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

from search_providers import create_search_provider  # noqa: E402
from search_providers.base import SearchProvider, SearchProviderError, normalize_result  # noqa: E402
from search_providers.hybrid import HybridProvider  # noqa: E402
from proxy_collectors.base import (  # noqa: E402
    dedupe_proxy_records,
    normalize_proxy_record,
    normalize_proxy_url,
    proxy_provenance_from_env,
    write_json,
    write_yaml,
)
from proxy_collectors.export_searxng_proxies import build_searxng_proxy_config  # noqa: E402
from proxy_collectors.validator import (  # noqa: E402
    ProxyError,
    build_live_inventory,
    validate_proxy_record,
)
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


class MockResponse:
    def __init__(self, status_code: int = 200, payload=None) -> None:
        self.status_code = status_code
        self._payload = payload if payload is not None else {'origin': '203.0.113.10'}
        self.headers = {'content-type': 'application/json'}

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


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

    def test_proxy_url_normalization_supports_no_scheme(self) -> None:
        url, protocol = normalize_proxy_url('1.2.3.4:8080', default_protocol='http')

        self.assertEqual(url, 'http://1.2.3.4:8080')
        self.assertEqual(protocol, 'http')

    def test_proxy_record_dedupe_uses_normalized_url(self) -> None:
        collected_at = '2026-05-11T00:00:00+00:00'
        first = normalize_proxy_record(
            'HTTP://1.2.3.4:8080',
            source='proxygather',
            source_url='https://example.test/http.txt',
            default_protocol='http',
            collected_at=collected_at,
        )
        second = normalize_proxy_record(
            '1.2.3.4:8080',
            source='proxygather',
            source_url='https://example.test/http.txt',
            default_protocol='http',
            collected_at=collected_at,
        )

        self.assertEqual(len(dedupe_proxy_records([first, second])), 1)

    def test_proxy_validator_accepts_neutral_json_response(self) -> None:
        record = normalize_proxy_record(
            '1.2.3.4:8080',
            source='proxygather',
            source_url='https://example.test/http.txt',
        )

        result = validate_proxy_record(
            record,
            request_get=lambda *args, **kwargs: MockResponse(payload={'origin': '1.2.3.4'}),
        )

        self.assertTrue(result['validated'])
        self.assertIsNone(result['failure_reason'])

    def test_proxy_validator_rejects_bad_response(self) -> None:
        record = normalize_proxy_record(
            '1.2.3.4:8080',
            source='proxygather',
            source_url='https://example.test/http.txt',
        )

        result = validate_proxy_record(
            record,
            request_get=lambda *args, **kwargs: MockResponse(payload={'html': '<body>ad</body>'}),
        )

        self.assertFalse(result['validated'])
        self.assertEqual(result['failure_reason'], 'bad_response')

    def test_proxy_validator_records_proxy_errors_without_crashing(self) -> None:
        record = normalize_proxy_record(
            '1.2.3.4:8080',
            source='proxygather',
            source_url='https://example.test/http.txt',
        )

        def fail_proxy(*args, **kwargs):
            raise ProxyError('Tunnel connection failed: 400 Bad Request')

        result = validate_proxy_record(record, request_get=fail_proxy)

        self.assertFalse(result['validated'])
        self.assertEqual(result['failure_reason'], 'connection_error')

    def test_searxng_proxy_export_includes_only_validated_records(self) -> None:
        records = [
            {'url': 'http://1.2.3.4:8080', 'validated': True},
            {'url': 'http://5.6.7.8:3128', 'validated': False},
        ]

        payload = build_searxng_proxy_config(records)

        self.assertEqual(
            payload['outgoing']['proxies']['all://'],
            ['http://1.2.3.4:8080'],
        )

    def test_proxy_provenance_is_disabled_by_default(self) -> None:
        with without_env('POINTPIVOT_PROXY_MODE', 'POINTPIVOT_PROXY_INVENTORY'):
            self.assertEqual(proxy_provenance_from_env(), {})

    def test_proxy_provenance_summary_omits_proxy_urls(self) -> None:
        inventory = build_live_inventory([
            {
                'url': 'http://1.2.3.4:8080',
                'protocol': 'http',
                'source': 'proxygather',
                'validated': True,
                'validated_at': '2026-05-11T00:00:00+00:00',
                'failure_reason': None,
            }
        ], target_url='https://httpbin.org/ip')

        with tempfile.TemporaryDirectory() as tmp:
            inventory_path = Path(tmp) / 'live_proxies.yml'
            write_yaml(inventory_path, inventory)
            with without_env('POINTPIVOT_PROXY_MODE', 'POINTPIVOT_PROXY_INVENTORY'):
                os.environ['POINTPIVOT_PROXY_MODE'] = 'searxng_outgoing'
                os.environ['POINTPIVOT_PROXY_INVENTORY'] = str(inventory_path)
                provenance = proxy_provenance_from_env()

        self.assertEqual(provenance['proxy_mode'], 'searxng_outgoing')
        self.assertEqual(provenance['proxy_source'], 'proxygather')
        self.assertEqual(provenance['proxy_count'], 1)
        self.assertNotIn('1.2.3.4', str(provenance))


if __name__ == '__main__':
    unittest.main(verbosity=2)
