"""spammed_sites.md에서 DDG site: 검색 대상 도메인 목록 (izanaholdings 제외)."""

from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import parse_spammed_sites  # noqa: E402


def ddg_scrape_domains() -> list[str]:
    """스크래퍼 유형이 ddg_site 이거나, 컬럼 없을 때 izana가 아닌 도메인."""
    sites = parse_spammed_sites()
    out: list[str] = []
    seen: set[str] = set()
    for s in sites:
        raw = (s.get('url') or '').strip()
        if not raw:
            continue
        stype = (s.get('scraper_type') or '').strip().lower()
        if stype == 'izanaholdings':
            continue
        if 'izanaholdings' in raw.lower():
            continue
        if raw.startswith('http://') or raw.startswith('https://'):
            dom = urlparse(raw).netloc or raw
        else:
            dom = raw.split('/')[0].strip()
        dom = dom.lower().removeprefix('www.')
        if dom and dom not in seen:
            seen.add(dom)
            if not stype or stype in ('ddg_site', '-', ''):
                out.append(dom)
    return out
