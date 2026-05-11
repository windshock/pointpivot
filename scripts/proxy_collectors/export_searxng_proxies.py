#!/usr/bin/env python3
"""Export validated proxies into a SearXNG outgoing.proxies YAML fragment.

Run:
  .venv/bin/python scripts/proxy_collectors/export_searxng_proxies.py \
    --input config/live_proxies.yml \
    --output config/searxng_proxies.generated.yml
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

from proxy_collectors.base import (  # noqa: E402
    DEFAULT_LIVE_PROXY_PATH,
    DEFAULT_SEARXNG_PROXY_EXPORT_PATH,
    ProxyRecord,
    live_proxy_records,
    write_yaml,
)


def build_searxng_proxy_config(
    records: list[ProxyRecord],
    *,
    extra_proxy_timeout: float = 10.0,
    retries: int = 2,
    limit: int | None = None,
) -> dict:
    urls = [
        str(record.get('url'))
        for record in records
        if record.get('validated') is True and record.get('url')
    ]
    if limit is not None:
        urls = urls[:limit]
    return {
        'outgoing': {
            'extra_proxy_timeout': float(extra_proxy_timeout),
            'retries': int(retries),
            'proxies': {
                'all://': urls,
            },
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Export SearXNG proxy YAML fragment')
    parser.add_argument('--input', type=Path, default=DEFAULT_LIVE_PROXY_PATH)
    parser.add_argument('--output', type=Path, default=DEFAULT_SEARXNG_PROXY_EXPORT_PATH)
    parser.add_argument('--extra-proxy-timeout', type=float, default=10.0)
    parser.add_argument('--retries', type=int, default=2)
    parser.add_argument('--limit', type=int, default=None)
    args = parser.parse_args()

    records = live_proxy_records(args.input)
    payload = build_searxng_proxy_config(
        records,
        extra_proxy_timeout=args.extra_proxy_timeout,
        retries=args.retries,
        limit=args.limit,
    )
    write_yaml(args.output, payload)
    proxy_count = len(payload['outgoing']['proxies']['all://'])
    print(f'SearXNG proxy fragment written: {args.output} ({proxy_count} proxies)')


if __name__ == '__main__':
    main()
