"""SearXNG search provider."""

from __future__ import annotations

import os
from typing import Any

try:
    import requests
    from requests import RequestException
except ImportError:
    requests = None
    RequestException = Exception

from .base import SearchProvider, SearchProviderError, normalize_result, utc_now_iso

URL_ENVS = ('POINTPIVOT_SEARXNG_URL', 'SEARXNG_URL')
TIMEOUT_ENV = 'POINTPIVOT_SEARCH_TIMEOUT'


def _env_url() -> str:
    for name in URL_ENVS:
        value = os.environ.get(name)
        if value:
            return value.rstrip('/')
    return 'http://localhost:8080'


def _env_timeout() -> float:
    raw = os.environ.get(TIMEOUT_ENV, '15')
    try:
        return float(raw)
    except ValueError as exc:
        raise SearchProviderError(f'{TIMEOUT_ENV} must be numeric, got {raw!r}') from exc


def _engine_name(item: dict[str, Any]) -> str:
    engine = item.get('engine', '')
    if isinstance(engine, str):
        return engine
    engines = item.get('engines', '')
    if isinstance(engines, list):
        return ','.join(str(e) for e in engines)
    return str(engine or engines or '')


class SearXNGProvider(SearchProvider):
    name = 'searxng'
    mode = 'searxng'

    def __init__(self, url: str | None = None, timeout: float | None = None) -> None:
        self.url = (url or _env_url()).rstrip('/')
        self.timeout = timeout if timeout is not None else _env_timeout()

    def search(self, query: str, max_results: int = 20) -> list[dict]:
        if requests is None:
            raise SearchProviderError(
                'requests package is not installed; run '
                '.venv/bin/python -m pip install -r scripts/requirements.txt'
            )

        fetched_at = utc_now_iso()
        try:
            response = requests.get(
                f'{self.url}/search',
                params={'q': query, 'format': 'json', 'language': 'ko-KR'},
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
        except RequestException as exc:
            raise SearchProviderError(f'SearXNG request failed: {exc}') from exc
        except ValueError as exc:
            raise SearchProviderError(f'SearXNG returned invalid JSON: {exc}') from exc

        rows = payload.get('results') or []
        if not isinstance(rows, list):
            raise SearchProviderError('SearXNG JSON does not contain a results list')

        return [
            normalize_result(
                title=item.get('title', ''),
                href=item.get('url', ''),
                body=item.get('content', ''),
                provider=self.name,
                engine=_engine_name(item),
                query=query,
                fetched_at=fetched_at,
            )
            for item in rows[:max_results]
            if isinstance(item, dict)
        ]
