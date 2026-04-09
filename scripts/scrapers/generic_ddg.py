"""
피해 사이트 도메인에 대해 DuckDuckGo `site:도메인 "IP"` 검색.
스니펫에서 사기 키워드만 수집 (텔레그램/도메인 자동 추출은 노이즈 위험으로 제외).
"""

from __future__ import annotations

import time
from typing import Callable

from .registry import ddg_scrape_domains

FRAUD_KEYWORDS = [
    '내구제', '선불유심', '유심매입', '기프티콘', '포인트현금화',
    '소액대출', '급전', '계정구매', '약물', '엑스터시',
]


def scrape_spam_sites_keywords_via_ddg(
    ip: str,
    search: Callable[[str, int], list[dict]],
    *,
    max_domains: int | None = None,
    sleep_s: float = 1.0,
) -> dict:
    """
    반환: {keywords, domains_checked, hits, per_domain}
    per_domain: [{domain, n_results, fraud_keywords, sample_hrefs}, ...]

    max_domains: None이면 `spammed_sites.md`에서 읽은 **ddg_site 도메인 전부** 순회.
    정수면 상위 N개만 (배치/테스트용).
    """
    domains = ddg_scrape_domains()
    if max_domains is not None:
        domains = domains[:max_domains]
    keywords: set[str] = set()
    hits: dict[str, int] = {}
    per_domain: list[dict] = []

    for dom in domains:
        query = f'site:{dom} "{ip}"'
        print(f'  [DDG:site:{dom}] {query[:70]}...')
        try:
            results = search(query, 15)
        except Exception as e:
            print(f'         오류: {e}')
            results = []
        hits[dom] = len(results)
        blob = ' '.join(
            (r.get('title') or '') + ' ' + (r.get('body') or '')
            for r in results
        )
        dom_kw = sorted({kw for kw in FRAUD_KEYWORDS if kw in blob})
        for kw in dom_kw:
            keywords.add(kw)
        per_domain.append({
            'domain': dom,
            'n_results': len(results),
            'fraud_keywords': dom_kw,
            'sample_hrefs': [(r.get('href') or '')[:200] for r in results[:3]],
        })
        time.sleep(sleep_s)

    return {
        'keywords': sorted(keywords),
        'domains_checked': domains,
        'hits': hits,
        'per_domain': per_domain,
    }
