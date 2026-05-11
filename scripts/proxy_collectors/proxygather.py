#!/usr/bin/env python3
"""Collect optional ProxyGather proxy candidates.

Run:
  .venv/bin/python scripts/proxy_collectors/proxygather.py --limit 200
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

try:
    import requests
    from requests import RequestException
except ImportError:
    requests = None
    RequestException = Exception

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

from proxy_collectors.base import (  # noqa: E402
    DEFAULT_PROXY_CANDIDATES_PATH,
    DEFAULT_PROXY_SOURCES_PATH,
    ProxyRecord,
    dedupe_proxy_records,
    normalize_proxy_record,
    read_yaml,
    utc_now_iso,
    write_json,
)

DEFAULT_SOURCES = [
    {
        'name': 'proxygather_all',
        'url': 'https://raw.githubusercontent.com/Skillter/ProxyGather/refs/heads/master/proxies/working-proxies-all.txt',
        'protocol': None,
    },
    {
        'name': 'proxygather_http',
        'url': 'https://raw.githubusercontent.com/Skillter/ProxyGather/refs/heads/master/proxies/working-proxies-http.txt',
        'protocol': 'http',
    },
    {
        'name': 'proxygather_socks4',
        'url': 'https://raw.githubusercontent.com/Skillter/ProxyGather/refs/heads/master/proxies/working-proxies-socks4.txt',
        'protocol': 'socks4',
    },
    {
        'name': 'proxygather_socks5',
        'url': 'https://raw.githubusercontent.com/Skillter/ProxyGather/refs/heads/master/proxies/working-proxies-socks5.txt',
        'protocol': 'socks5',
    },
]


def infer_protocol_from_source(source: dict[str, Any]) -> str | None:
    protocol = source.get('protocol')
    if protocol:
        return str(protocol).lower()

    name = str(source.get('name') or '').lower()
    url_name = str(source.get('url') or '').lower().rsplit('/', 1)[-1]
    label = f'{name} {url_name}'
    if 'socks5' in label:
        return 'socks5'
    if 'socks4' in label:
        return 'socks4'
    if 'http' in label and 'all' not in label:
        return 'http'
    return None


def load_sources(config_path: Path) -> tuple[list[dict[str, Any]], float]:
    if not config_path.exists():
        return DEFAULT_SOURCES, 15.0

    payload = read_yaml(config_path)
    if not isinstance(payload, dict):
        raise ValueError(f'{config_path} must contain a YAML object')

    timeout = float(payload.get('timeout', 15))
    raw_sources = payload.get('sources') or []
    sources: list[dict[str, Any]] = []
    for item in raw_sources:
        if isinstance(item, str):
            sources.append({'name': 'proxygather', 'url': item, 'protocol': None})
        elif isinstance(item, dict) and item.get('url'):
            sources.append(dict(item))
    if not sources:
        raise ValueError(f'{config_path} does not define any proxy sources')
    return sources, timeout


def collect_source(source: dict[str, Any], timeout: float) -> tuple[list[ProxyRecord], dict]:
    if requests is None:
        raise RuntimeError(
            'requests package is not installed; run '
            '.venv/bin/python -m pip install -r scripts/requirements.txt'
        )

    source_url = str(source['url'])
    source_name = str(source.get('source') or 'proxygather')
    default_protocol = infer_protocol_from_source(source)
    collected_at = utc_now_iso()
    response = requests.get(source_url, timeout=timeout)
    response.raise_for_status()

    records: list[ProxyRecord] = []
    invalid = 0
    for line in response.text.splitlines():
        try:
            records.append(
                normalize_proxy_record(
                    line,
                    source=source_name,
                    source_url=source_url,
                    default_protocol=default_protocol or 'http',
                    collected_at=collected_at,
                )
            )
        except ValueError:
            invalid += 1

    return records, {
        'url': source_url,
        'records': len(records),
        'invalid': invalid,
        'error': None,
    }


def collect_proxygather(
    sources: list[dict[str, Any]],
    *,
    timeout: float,
    limit: int | None = None,
) -> tuple[list[ProxyRecord], list[dict]]:
    records: list[ProxyRecord] = []
    summaries: list[dict] = []
    for source in sources:
        try:
            source_records, summary = collect_source(source, timeout)
            records.extend(source_records)
            summaries.append(summary)
        except (RequestException, RuntimeError, OSError, ValueError) as exc:
            summaries.append({
                'url': source.get('url', ''),
                'records': 0,
                'invalid': 0,
                'error': str(exc),
            })

    deduped = dedupe_proxy_records(records)
    if limit is not None:
        deduped = deduped[:limit]
    return deduped, summaries


def build_payload(records: list[ProxyRecord], source_summaries: list[dict]) -> dict:
    return {
        'schema_version': 1,
        'generated_at': utc_now_iso(),
        'source': 'proxygather',
        'summary': {
            'sources': len(source_summaries),
            'failed_sources': sum(1 for s in source_summaries if s.get('error')),
            'records': len(records),
        },
        'source_summaries': source_summaries,
        'proxies': records,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Collect ProxyGather proxy candidates')
    parser.add_argument('--config', type=Path, default=DEFAULT_PROXY_SOURCES_PATH)
    parser.add_argument('--output', type=Path, default=DEFAULT_PROXY_CANDIDATES_PATH)
    parser.add_argument('--limit', type=int, default=None)
    parser.add_argument('--timeout', type=float, default=None)
    args = parser.parse_args()

    sources, config_timeout = load_sources(args.config)
    timeout = args.timeout if args.timeout is not None else config_timeout
    records, summaries = collect_proxygather(sources, timeout=timeout, limit=args.limit)
    payload = build_payload(records, summaries)
    write_json(args.output, payload)

    failed = sum(1 for s in summaries if s.get('error'))
    print(
        f'proxy candidates written: {args.output} '
        f'({len(records)} proxies, {failed}/{len(summaries)} sources failed)'
    )


if __name__ == '__main__':
    main()
