#!/usr/bin/env python3
"""Validate optional proxy candidates locally before SearXNG export.

Run:
  .venv/bin/python scripts/proxy_collectors/validator.py \
    --input config/proxy_candidates.json \
    --output config/live_proxies.yml
"""

from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable

try:
    import requests
    from requests import RequestException
except ImportError:
    requests = None
    RequestException = Exception

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

from proxy_collectors.base import (  # noqa: E402
    DEFAULT_LIVE_PROXY_PATH,
    DEFAULT_PROXY_CANDIDATES_PATH,
    DEFAULT_PROXY_VALIDATION_LOG_DIR,
    ProxyRecord,
    read_candidate_records,
    utc_now_iso,
    write_json,
    write_yaml,
)

DEFAULT_TARGET_URL = 'https://httpbin.org/ip'


def _base_result(record: ProxyRecord, *, latency_ms: int | None = None) -> ProxyRecord:
    return {
        'url': record.get('url', ''),
        'protocol': record.get('protocol', ''),
        'source': record.get('source', ''),
        'source_url': record.get('source_url', ''),
        'collected_at': record.get('collected_at', ''),
        'validated': False,
        'latency_ms': latency_ms,
        'validated_at': utc_now_iso(),
        'failure_reason': None,
    }


def _failure(record: ProxyRecord, reason: str, latency_ms: int | None) -> ProxyRecord:
    result = _base_result(record, latency_ms=latency_ms)
    result['failure_reason'] = reason
    return result


def _classify_exception(exc: Exception) -> str:
    text = str(exc).lower()
    if requests is not None and isinstance(exc, requests.Timeout):
        return 'timeout'
    if '407' in text or 'auth' in text:
        return 'auth_required'
    if requests is not None and isinstance(exc, requests.ProxyError):
        return 'connection_error'
    if requests is not None and isinstance(exc, requests.ConnectionError):
        return 'connection_error'
    if 'socks' in text or 'protocol' in text or 'scheme' in text:
        return 'protocol_error'
    return 'connection_error'


def validate_proxy_record(
    record: ProxyRecord,
    *,
    target_url: str = DEFAULT_TARGET_URL,
    timeout: float = 5.0,
    request_get: Callable | None = None,
) -> ProxyRecord:
    if requests is None and request_get is None:
        raise RuntimeError(
            'requests package is not installed; run '
            '.venv/bin/python -m pip install -r scripts/requirements.txt'
        )

    proxy_url = str(record.get('url') or '')
    proxies = {'http': proxy_url, 'https': proxy_url}
    getter = request_get or requests.get
    started = time.monotonic()

    try:
        response = getter(target_url, proxies=proxies, timeout=timeout)
    except Exception as exc:
        latency_ms = int((time.monotonic() - started) * 1000)
        return _failure(record, _classify_exception(exc), latency_ms)

    latency_ms = int((time.monotonic() - started) * 1000)
    status_code = getattr(response, 'status_code', None)
    if status_code == 407:
        return _failure(record, 'auth_required', latency_ms)
    if status_code != 200:
        return _failure(record, 'bad_response', latency_ms)

    try:
        payload = response.json()
    except ValueError:
        return _failure(record, 'bad_response', latency_ms)

    if not isinstance(payload, dict) or not (payload.get('origin') or payload.get('ip')):
        return _failure(record, 'bad_response', latency_ms)

    result = _base_result(record, latency_ms=latency_ms)
    result['validated'] = True
    return result


def validate_records(
    records: list[ProxyRecord],
    *,
    target_url: str = DEFAULT_TARGET_URL,
    timeout: float = 5.0,
    concurrency: int = 10,
) -> list[ProxyRecord]:
    if concurrency < 1:
        raise ValueError('concurrency must be >= 1')

    if concurrency == 1:
        return [
            validate_proxy_record(record, target_url=target_url, timeout=timeout)
            for record in records
        ]

    results: list[ProxyRecord | None] = [None] * len(records)
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        future_map = {
            pool.submit(
                validate_proxy_record,
                record,
                target_url=target_url,
                timeout=timeout,
            ): idx
            for idx, record in enumerate(records)
        }
        for future in as_completed(future_map):
            results[future_map[future]] = future.result()

    return [r for r in results if r is not None]


def build_live_inventory(
    validation_results: list[ProxyRecord],
    *,
    target_url: str,
) -> dict:
    live = [r for r in validation_results if r.get('validated') is True]
    return {
        'schema_version': 1,
        'generated_at': utc_now_iso(),
        'validation_target': target_url,
        'valid_count': len(live),
        'proxies': live,
    }


def default_log_path() -> Path:
    stamp = utc_now_iso().replace(':', '').replace('+00:00', 'Z')
    return DEFAULT_PROXY_VALIDATION_LOG_DIR / f'{stamp}.json'


def main() -> None:
    parser = argparse.ArgumentParser(description='Validate proxy candidates locally')
    parser.add_argument('--input', type=Path, default=DEFAULT_PROXY_CANDIDATES_PATH)
    parser.add_argument('--output', type=Path, default=DEFAULT_LIVE_PROXY_PATH)
    parser.add_argument('--target-url', default=DEFAULT_TARGET_URL)
    parser.add_argument('--timeout', type=float, default=5.0)
    parser.add_argument('--concurrency', type=int, default=10)
    parser.add_argument('--limit', type=int, default=None)
    parser.add_argument('--log-output', type=Path, default=None)
    args = parser.parse_args()

    records = read_candidate_records(args.input)
    if args.limit is not None:
        records = records[: args.limit]
    results = validate_records(
        records,
        target_url=args.target_url,
        timeout=args.timeout,
        concurrency=args.concurrency,
    )
    inventory = build_live_inventory(results, target_url=args.target_url)
    write_yaml(args.output, inventory)

    if args.log_output:
        write_json(args.log_output, {
            'schema_version': 1,
            'generated_at': utc_now_iso(),
            'validation_target': args.target_url,
            'results': results,
        })

    print(
        f'live proxies written: {args.output} '
        f"({inventory['valid_count']}/{len(results)} validated)"
    )


if __name__ == '__main__':
    main()
