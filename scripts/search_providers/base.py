"""Shared types and helpers for search providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any

SearchResult = dict[str, Any]


class SearchProviderError(RuntimeError):
    """Raised when a search provider cannot return results."""


class SearchProvider(ABC):
    name = 'base'
    mode = 'base'

    @abstractmethod
    def search(self, query: str, max_results: int = 20) -> list[SearchResult]:
        """Return normalized search results."""


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_result(
    *,
    title: str,
    href: str,
    body: str,
    provider: str,
    engine: str = '',
    query: str = '',
    fetched_at: str | None = None,
) -> SearchResult:
    return {
        'title': title or '',
        'href': href or '',
        'body': body or '',
        'provider': provider,
        'engine': engine or '',
        'query': query,
        'fetched_at': fetched_at or utc_now_iso(),
        'evidence_level': 'search_snippet_only',
    }


def dedupe_by_href(results: list[SearchResult]) -> list[SearchResult]:
    seen: set[str] = set()
    deduped: list[SearchResult] = []
    for result in results:
        href = (result.get('href') or '').strip()
        key = href or f"{result.get('provider', '')}:{result.get('title', '')}"
        if key in seen:
            continue
        seen.add(key)
        deduped.append(result)
    return deduped
