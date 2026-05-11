"""DuckDuckGo search provider."""

from __future__ import annotations

from .base import SearchProvider, SearchProviderError, normalize_result, utc_now_iso

try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None


class DDGProvider(SearchProvider):
    name = 'ddg'
    mode = 'ddg'

    def search(self, query: str, max_results: int = 20) -> list[dict]:
        if DDGS is None:
            raise SearchProviderError('ddgs package is not installed')

        fetched_at = utc_now_iso()
        try:
            with DDGS() as ddgs:
                rows = list(ddgs.text(query, max_results=max_results))
        except Exception as exc:
            raise SearchProviderError(str(exc)) from exc

        return [
            normalize_result(
                title=row.get('title', ''),
                href=row.get('href', ''),
                body=row.get('body', ''),
                provider=self.name,
                engine='duckduckgo',
                query=query,
                fetched_at=fetched_at,
            )
            for row in rows
        ]
