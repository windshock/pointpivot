"""
PointPivot 사이트별 스크래퍼 플러그인.
izanaholdings 직접 스크래핑 + 피해 사이트 목록 기반 DDG site: 검색.
"""

from .izanaholdings import scrape_izanaholdings
from .generic_ddg import scrape_spam_sites_keywords_via_ddg
from .registry import ddg_scrape_domains

__all__ = [
    'scrape_izanaholdings',
    'scrape_spam_sites_keywords_via_ddg',
    'ddg_scrape_domains',
]
