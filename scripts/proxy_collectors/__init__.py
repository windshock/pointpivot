"""Optional proxy collector helpers for SearXNG outgoing proxy exports."""

from __future__ import annotations

from .base import (
    DEFAULT_LIVE_PROXY_PATH,
    DEFAULT_PROXY_CANDIDATES_PATH,
    DEFAULT_SEARXNG_PROXY_EXPORT_PATH,
    ProxyRecord,
    dedupe_proxy_records,
    normalize_proxy_record,
    normalize_proxy_url,
    proxy_provenance_from_env,
    utc_now_iso,
)

__all__ = [
    'DEFAULT_LIVE_PROXY_PATH',
    'DEFAULT_PROXY_CANDIDATES_PATH',
    'DEFAULT_SEARXNG_PROXY_EXPORT_PATH',
    'ProxyRecord',
    'dedupe_proxy_records',
    'normalize_proxy_record',
    'normalize_proxy_url',
    'proxy_provenance_from_env',
    'utc_now_iso',
]
