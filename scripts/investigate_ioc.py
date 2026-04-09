#!/usr/bin/env python3
"""
IOC → IP 역방향 피벗 (텔레그램 핸들, 닉네임 등).
DuckDuckGo 검색으로 스니펫·URL에서 IPv4를 추출하고 pivot_queue에 적재.
(izanaholdings는 IP 기반 스크래퍼만 있음 — 핸들 전용 직접 스크래핑은 브라우저 조사로 보완.)

사용법:
    python scripts/investigate_ioc.py "@brrsim_77"
    python scripts/investigate_ioc.py kimyoojin18 --nick
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        print('필요 패키지 없음: pip install ddgs')
        sys.exit(1)

from utils import append_pivot_queue

IP_RE = re.compile(
    r'\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b'
)


def search(q: str, max_results: int = 25) -> list[dict]:
    try:
        with DDGS() as ddgs:
            return list(ddgs.text(q, max_results=max_results))
    except Exception as e:
        print(f'[DDG 오류] {q!r}: {e}')
        return []


def extract_ips_from_results(results: list[dict]) -> set[str]:
    found: set[str] = set()
    for r in results:
        blob = (r.get('title') or '') + ' ' + (r.get('body') or '') + ' ' + (r.get('href') or '')
        for m in IP_RE.findall(blob):
            found.add(m)
    return found


def main():
    p = argparse.ArgumentParser(description='IOC 역방향 피벗 (DDG)')
    p.add_argument('ioc', help='텔레그램 @핸들 또는 문자열')
    p.add_argument('--nick', action='store_true', help='닉네임 검색어로 처리')
    args = p.parse_args()

    raw = args.ioc.strip()
    queries = []
    if args.nick:
        queries.append(f'"{raw}" 선불유심 OR 내구제')
        queries.append(f'site:izanaholdings.com "{raw}"')
    else:
        h = raw if raw.startswith('@') else '@' + raw
        queries.append(f'"{h}"')
        queries.append(f'"{h}" 선불유심 OR 내구제 OR 유심')

    all_ips: set[str] = set()
    for q in queries:
        print(f'[DDG] {q}')
        res = search(q)
        ips = extract_ips_from_results(res)
        print(f'      결과 {len(res)}건, IP 후보 {len(ips)}개')
        all_ips |= ips
        time.sleep(1.5)

    added = append_pivot_queue(sorted(all_ips), f'IOC pivot {raw}', 'investigate_ioc.py')
    print(f'\n추출 IP 수: {len(all_ips)}')
    print(f'pivot_queue 추가: {added or "(신규 없음 — 이미 INDEX/queue에 있음)"}')


if __name__ == '__main__':
    main()
