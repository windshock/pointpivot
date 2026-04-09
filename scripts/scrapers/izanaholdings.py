"""izanaholdings.com 게시판 — 작성자 IP 노출이 확실한 1차 소스."""

from __future__ import annotations

import re
import time
from typing import Callable

from .http import fetch

TELEGRAM_RE = re.compile(r'@[a-zA-Z0-9_]{3,32}')
ISWEB_RE = re.compile(r'[a-zA-Z0-9_-]+\.isweb\.co\.kr')
NON_TG_TOKENS = {'@naver', '@media'}
FRAUD_KEYWORDS = [
    '내구제', '선불유심', '유심매입', '기프티콘', '포인트현금화',
    '소액대출', '급전', '계정구매', '약물', '엑스터시',
]

IZANA_BASE = 'https://izanaholdings.com'
IZANA_SEARCH = f'{IZANA_BASE}/bbs/board?search_key=subject_content&key={{ip}}&paged={{page}}'


def _update_iocs(iocs: dict, text: str) -> None:
    tgs = [t for t in TELEGRAM_RE.findall(text) if t.lower() not in NON_TG_TOKENS]
    iocs['telegram'].update(tgs)
    iocs['isweb'].update(ISWEB_RE.findall(text))
    iocs['keywords'].update(kw for kw in FRAUD_KEYWORDS if kw in text)


def scrape_izanaholdings(
    ip: str,
    fetch_fn: Callable[[str], str | None] | None = None,
    *,
    max_search_pages: int = 3,
    max_list_pages: int = 15,
    list_page_range: tuple[int, int] | None = None,
    board_code: str = 'board',
) -> dict:
    """
    반환: {posts: [...], iocs: {telegram,isweb,keywords}, author_ips: [...] }

    list_page_range: (시작, 끝) 포함 구간. 지정 시 max_list_pages 기본 목록 루프 대신 이 구간만 순회.
    max_search_pages=0 이면 사이트 검색만 건너뛰고 목록 순회만 할 수 있음.
    """
    fetcher = fetch_fn or fetch
    result = {
        'posts': [],
        'iocs': {'telegram': set(), 'isweb': set(), 'keywords': set()},
        'author_ips': set(),
    }

    print(f'  [izana] 게시판 직접 검색: {ip} (board_code={board_code})')
    seen_idxs: set[str] = set()

    def list_url(page: int) -> str:
        return f'{IZANA_BASE}/bbs_shop/list.htm?board_code={board_code}&page={page}'

    def post_url(idx: str) -> str:
        return (
            f'{IZANA_BASE}/bbs_shop/read.htm?board_code={board_code}'
            f'&idx={idx}&cate_sub_idx=0'
        )

    def inspect_listing(url: str) -> bool:
        html = fetcher(url)
        if not html:
            return False
        post_idxs = re.findall(r'idx=(\d+)', html)
        found_any = False

        for idx in post_idxs:
            if idx in seen_idxs or not idx.isdigit() or int(idx) < 1:
                continue
            seen_idxs.add(idx)

            post_html = fetcher(post_url(idx))
            if not post_html:
                continue

            author_ip_m = re.search(
                r'<span>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</span>\s*</dt>',
                post_html,
            )
            if not author_ip_m:
                author_ip_m = re.search(
                    r'<li>\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*</li>',
                    post_html,
                )
            author_ip = author_ip_m.group(1) if author_ip_m else ''
            # 부분 문자열 매칭 금지: "221.143.197.13" 이 221.143.197.130 등에 포함되는 오탐 방지
            if author_ip != ip:
                continue

            found_any = True
            title_m = re.search(r'<title[^>]*>([^<]+)</title>', post_html)
            title = title_m.group(1).strip() if title_m else f'게시글 #{idx}'

            if author_ip:
                result['author_ips'].add(author_ip)

            _update_iocs(result['iocs'], post_html)
            result['posts'].append({
                'idx': idx,
                'title': title,
                'url': post_url(idx),
                'author_ip': author_ip,
            })
            time.sleep(0.5)

        return found_any

    for page in range(1, max_search_pages + 1):
        url = IZANA_SEARCH.format(ip=ip, page=page)
        if not inspect_listing(url):
            break
        time.sleep(1)

    if not result['posts']:
        if list_page_range is not None:
            lp_lo, lp_hi = list_page_range
            print(
                f'         exact 검색 결과 없음 → 목록 순회 board_code={board_code!r} '
                f'(page {lp_lo}–{lp_hi})'
            )
            page_iter = range(lp_lo, lp_hi + 1)
        else:
            if max_list_pages < 1:
                print(
                    f'         exact 검색 결과 없음 → 목록 순회 생략 '
                    f'(얕은 모드: max_list_pages={max_list_pages})'
                )
                page_iter = range(0)
            else:
                print(
                    f'         exact 검색 결과 없음 → 최근 목록 직접 순회 '
                    f'(board_code={board_code!r}, page 1–{max_list_pages})'
                )
                page_iter = range(1, max_list_pages + 1)
        for page in page_iter:
            inspect_listing(list_url(page))
            time.sleep(1)

    result['iocs'] = {k: sorted(v) for k, v in result['iocs'].items()}
    result['author_ips'] = sorted(result['author_ips'])
    print(
        f"         게시글 {len(result['posts'])}건, TG: {result['iocs']['telegram']}, "
        f"작성자IP: {result['author_ips']}"
    )
    return result
