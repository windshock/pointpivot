"""Search provider factory for PointPivot."""

from __future__ import annotations

import os

from .base import SearchProvider, SearchProviderError, SearchResult
from .ddg import DDGProvider
from .hybrid import HybridProvider
from .searxng import SearXNGProvider

PROVIDER_ENV = 'POINTPIVOT_SEARCH_PROVIDER'


def create_search_provider(name: str | None = None) -> SearchProvider:
    provider = (name or os.environ.get(PROVIDER_ENV) or 'ddg').strip().lower()
    if provider == 'ddg':
        return DDGProvider()
    if provider == 'searxng':
        return SearXNGProvider()
    if provider == 'hybrid':
        return HybridProvider()
    raise SearchProviderError(
        f'unknown search provider {provider!r}; expected ddg, searxng, or hybrid'
    )


__all__ = [
    'DDGProvider',
    'HybridProvider',
    'SearXNGProvider',
    'SearchProvider',
    'SearchProviderError',
    'SearchResult',
    'create_search_provider',
]
