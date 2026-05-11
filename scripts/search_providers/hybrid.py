"""Hybrid search provider."""

from __future__ import annotations

import os
import sys

from .base import SearchProvider, SearchProviderError, dedupe_by_href
from .ddg import DDGProvider
from .searxng import SearXNGProvider

HYBRID_MODE_ENV = 'POINTPIVOT_SEARCH_HYBRID_MODE'


class HybridProvider(SearchProvider):
    name = 'hybrid'

    def __init__(
        self,
        searxng: SearchProvider | None = None,
        ddg: SearchProvider | None = None,
        hybrid_mode: str | None = None,
    ) -> None:
        self.searxng = searxng or SearXNGProvider()
        self.ddg = ddg or DDGProvider()
        self.hybrid_mode = (
            hybrid_mode or os.environ.get(HYBRID_MODE_ENV) or 'fallback'
        ).strip().lower()
        if self.hybrid_mode not in {'fallback', 'both'}:
            raise SearchProviderError(
                f'unknown hybrid mode {self.hybrid_mode!r}; expected fallback or both'
            )
        self.mode = f'hybrid:{self.hybrid_mode}'

    def search(self, query: str, max_results: int = 20) -> list[dict]:
        if self.hybrid_mode == 'both':
            return self._search_both(query, max_results)
        return self._search_fallback(query, max_results)

    def _search_fallback(self, query: str, max_results: int) -> list[dict]:
        try:
            results = self.searxng.search(query, max_results)
            if results:
                return results
            print(
                f'[hybrid] SearXNG returned 0 results for {query!r}; falling back to DDG',
                file=sys.stderr,
            )
        except SearchProviderError as exc:
            print(
                f'[hybrid] SearXNG failed for {query!r}: {exc}; falling back to DDG',
                file=sys.stderr,
            )
        return self.ddg.search(query, max_results)

    def _search_both(self, query: str, max_results: int) -> list[dict]:
        results: list[dict] = []
        try:
            results.extend(self.searxng.search(query, max_results))
        except SearchProviderError as exc:
            print(f'[hybrid] SearXNG failed for {query!r}: {exc}', file=sys.stderr)

        results.extend(self.ddg.search(query, max_results))
        return dedupe_by_href(results)[:max_results]
