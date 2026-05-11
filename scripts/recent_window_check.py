#!/usr/bin/env python3
"""Recent observation-window search and contamination check.

Run:
  .venv/bin/python scripts/recent_window_check.py --today 2026-05-11
"""

from __future__ import annotations

import argparse
import html
import json
import re
import ssl
import time
from collections import Counter
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit, urlunsplit
from urllib.request import Request, urlopen

try:
    from ddgs import DDGS
except ImportError:
    print('필요 패키지 없음: pip install ddgs')
    raise SystemExit(1)


ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / 'reports'

DEFAULT_QUERIES = [
    '"@GO174"',
    '"GO174" 텔',
    '"텔GO174"',
    '"GO174" 먹튀',
    '"GO174" 충전계좌',
    '"@Muo52S"',
    '"Muo52S"',
    '"텔Muo52S"',
    '"Muo52S" 파워볼',
    '"Muo52S" 밸런스',
    'site:outoftrunk.com "GO174"',
    'site:outoftrunk.com "Muo52S"',
    'site:outoftrunk.com "118.235"',
    'site:tojonghongsam.com "GO174"',
    'site:petroute.co.kr "GO174"',
    'site:gs3m.co.kr "GO174"',
    'site:baumshouse.com "GO174"',
    '"118.235.25.44" "GO174"',
    '"118.235.12.181" "GO174"',
    '"118.235.2.186" "Muo52S"',
    '"39.7.230.236" "GO174"',
    '"118.235" "GO174"',
    '"118.235" "Muo52S"',
    '"39.7" "GO174"',
]

EXACT_TERMS = [
    '@GO174',
    'GO174',
    '텔GO174',
    '@Muo52S',
    'Muo52S',
    '텔Muo52S',
    '118.235.25.44',
    '118.235.12.181',
    '118.235.2.186',
    '39.7.230.236',
    '118.235',
    '39.7',
]

FRAUD_KEYWORDS = [
    '먹튀',
    '충전계좌',
    '계좌',
    '통장협박',
    '보피돈',
    '파워볼',
    '밸런스',
    '스포츠픽',
    '도박',
    '문서위조',
]

NOISE_DOMAINS = (
    'wikipedia.org',
    'opencode.ai',
    'sunglasshut.com',
    'ipinfo.io',
    'ipshu.com',
    'speedguide.net',
    'ip.zone',
    'ipaddress.my',
    'db-ip.com',
    'tiktok.com',
    'steamcommunity.com',
)


@dataclass
class SearchRow:
    query: str
    title: str
    href: str
    body: str
    exact_terms: list[str]
    fraud_keywords: list[str]
    level: str
    domain: str
    fetch_status: str = 'not_fetched'
    source_date: date | None = None
    author_ips: list[str] = field(default_factory=list)
    fetched_exact_terms: list[str] = field(default_factory=list)
    fetched_fraud_keywords: list[str] = field(default_factory=list)
    classification: str = 'search_only'
    source_snippet: str = ''


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='최근 관측 window 검색 결과가 오래된 증거로 오염되는지 점검'
    )
    parser.add_argument('--days', type=int, default=7, help='관측 window 일수 (기본: 7)')
    parser.add_argument(
        '--today',
        default=date.today().isoformat(),
        help='window 종료일 YYYY-MM-DD (기본: 오늘)',
    )
    parser.add_argument('--max-results', type=int, default=8, help='쿼리별 검색 결과 수')
    parser.add_argument(
        '--fetch-limit',
        type=int,
        default=30,
        help='exact IOC 후보 원문 fetch 최대 수',
    )
    parser.add_argument(
        '--output',
        default='',
        help='보고서 경로 (기본: reports/recent_window_YYYY-MM-DD_YYYY-MM-DD.md)',
    )
    parser.add_argument(
        '--json-output',
        default='',
        help='원시 결과 JSON 경로 (기본: reports/recent_window_YYYY-MM-DD_YYYY-MM-DD.json)',
    )
    return parser.parse_args()


def normalize_url(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit(
        (
            parts.scheme,
            parts.netloc,
            quote(parts.path, safe='/%'),
            quote(parts.query, safe='=&?/:%'),
            parts.fragment,
        )
    )


def visible_text(raw: str) -> str:
    text = re.sub(r'(?is)<script.*?</script>|<style.*?</style>', ' ', raw)
    text = re.sub(r'(?s)<[^>]+>', ' ', text)
    text = html.unescape(text)
    return re.sub(r'\s+', ' ', text).strip()


def parse_source_date(raw: str) -> date | None:
    patterns = [
        r'"datePublished"\s*:\s*"([^"]+)"',
        r'<meta[^>]+(?:property|name)=["\']article:published_time["\'][^>]+content=["\']([^"\']+)["\']',
        r'<time[^>]+datetime=["\']([^"\']+)["\']',
        r'작성일</strong>\s*<span[^>]*>\s*([0-9]{4}[-./][0-9]{1,2}[-./][0-9]{1,2})',
    ]
    for pattern in patterns:
        m = re.search(pattern, raw, re.IGNORECASE)
        if not m:
            continue
        parsed = parse_date_text(m.group(1))
        if parsed:
            return parsed

    candidates = []
    for m in re.finditer(r'\b20\d{2}[-./]\d{1,2}[-./]\d{1,2}\b', raw):
        parsed = parse_date_text(m.group(0))
        if parsed and parsed.year < 2099:
            candidates.append(parsed)
    return min(candidates) if candidates else None


def parse_date_text(value: str) -> date | None:
    value = value.strip().replace('.', '-').replace('/', '-')
    value = re.sub(r'T.*$', '', value)
    value = value.split()[0]
    for fmt in ('%Y-%m-%d', '%Y-%m-%dT%H:%M:%S%z'):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass
    try:
        parts = value.split('-')
        if len(parts) == 3:
            y, m, d = (int(p) for p in parts)
            return date(y, m, d)
    except ValueError:
        return None
    return None


def classify_search_result(
    query: str,
    title: str,
    href: str,
    body: str,
) -> SearchRow:
    text = f'{title} {href} {body}'
    exact_terms = [term for term in EXACT_TERMS if term in text]
    fraud_keywords = [kw for kw in FRAUD_KEYWORDS if kw in text]
    domain = urlsplit(href).netloc.lower()
    is_noise = any(noise in domain for noise in NOISE_DOMAINS)

    level = 'noise'
    if exact_terms and fraud_keywords:
        level = 'candidate_exact_ioc_and_fraud'
    elif exact_terms:
        level = 'candidate_exact_ioc'
    elif fraud_keywords:
        level = 'keyword_only'
    if is_noise and level == 'candidate_exact_ioc':
        level = 'ip_directory_or_generic'

    return SearchRow(
        query=query,
        title=title,
        href=href,
        body=body,
        exact_terms=exact_terms,
        fraud_keywords=fraud_keywords,
        level=level,
        domain=domain,
    )


def fetch_candidate(row: SearchRow, start: date, end: date) -> None:
    url = normalize_url(row.href)
    try:
        req = Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 PointPivot recent-window-check'},
        )
        with urlopen(req, timeout=15, context=ssl.create_default_context()) as response:
            raw = response.read(500_000).decode('utf-8', 'ignore')
        row.fetch_status = 'fetched'
    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
        row.fetch_status = f'fetch_failed: {type(exc).__name__}'
        row.classification = 'source_unverified'
        return

    row.source_date = parse_source_date(raw)
    row.author_ips = sorted(set(re.findall(r'\b\d{1,3}(?:\.\d{1,3}){3}\b', raw)))
    row.fetched_exact_terms = [term for term in EXACT_TERMS if term in raw]
    row.fetched_fraud_keywords = [kw for kw in FRAUD_KEYWORDS if kw in raw]
    text = visible_text(raw)
    pivot = -1
    for needle in ('GO174', 'Muo52S', '계좌', '먹튀'):
        pivot = text.find(needle)
        if pivot != -1:
            break
    if pivot != -1:
        row.source_snippet = text[max(0, pivot - 160):pivot + 360]

    if row.source_date is None:
        row.classification = 'undated_source'
    elif start <= row.source_date <= end:
        if row.fetched_exact_terms and row.fetched_fraud_keywords:
            row.classification = 'verified_recent_candidate'
        else:
            row.classification = 'recent_but_ioc_not_in_source'
    elif row.fetched_exact_terms and row.fetched_fraud_keywords:
        row.classification = 'stale_source_contamination'
    else:
        row.classification = 'stale_or_unrelated_source'


def run_search(max_results: int) -> tuple[list[SearchRow], list[dict]]:
    rows: list[SearchRow] = []
    query_status = []
    with DDGS() as ddgs:
        for query in DEFAULT_QUERIES:
            try:
                results = list(ddgs.text(query, max_results=max_results, timelimit='w'))
                query_status.append({'query': query, 'count': len(results), 'error': None})
            except Exception as exc:
                query_status.append(
                    {
                        'query': query,
                        'count': 0,
                        'error': f'{type(exc).__name__}: {exc}',
                    }
                )
                continue

            for result in results:
                rows.append(
                    classify_search_result(
                        query,
                        (result.get('title') or '').strip(),
                        (result.get('href') or '').strip(),
                        (result.get('body') or '').strip().replace('\n', ' '),
                    )
                )
            time.sleep(0.6)
    return rows, query_status


def row_to_json(row: SearchRow) -> dict:
    return {
        'query': row.query,
        'title': row.title,
        'href': row.href,
        'body': row.body,
        'exact_terms': row.exact_terms,
        'fraud_keywords': row.fraud_keywords,
        'level': row.level,
        'domain': row.domain,
        'fetch_status': row.fetch_status,
        'source_date': row.source_date.isoformat() if row.source_date else None,
        'author_ips': row.author_ips,
        'fetched_exact_terms': row.fetched_exact_terms,
        'fetched_fraud_keywords': row.fetched_fraud_keywords,
        'classification': row.classification,
        'source_snippet': row.source_snippet,
    }


def build_report(
    rows: list[SearchRow],
    query_status: list[dict],
    start: date,
    end: date,
) -> str:
    level_counts = Counter(row.level for row in rows)
    class_counts = Counter(row.classification for row in rows)
    fetched = [row for row in rows if row.fetch_status == 'fetched']
    candidates = [
        row for row in rows
        if row.level in ('candidate_exact_ioc_and_fraud', 'candidate_exact_ioc')
    ]
    verified_recent = [row for row in rows if row.classification == 'verified_recent_candidate']
    stale = [row for row in rows if row.classification == 'stale_source_contamination']
    source_ip_rows = [row for row in fetched if row.author_ips]

    query_rows = '\n'.join(
        f"| `{status['query']}` | {status['count']} | {status['error'] or '-'} |"
        for status in query_status
    )
    classification_rows = '\n'.join(
        f'| {name} | {count} |'
        for name, count in sorted(class_counts.items())
    )

    candidate_rows = []
    for row in candidates[:40]:
        source_date = row.source_date.isoformat() if row.source_date else '-'
        exact = ', '.join(row.fetched_exact_terms or row.exact_terms) or '-'
        fraud = ', '.join(row.fetched_fraud_keywords or row.fraud_keywords) or '-'
        author_ips = ', '.join(row.author_ips) or '-'
        candidate_rows.append(
            '| '
            + ' | '.join(
                [
                    row.classification,
                    source_date,
                    author_ips,
                    exact.replace('|', '｜'),
                    fraud.replace('|', '｜'),
                    f'[{row.domain}]({row.href})',
                ]
            )
            + ' |'
        )
    candidate_table = '\n'.join(candidate_rows) if candidate_rows else '| - | - | - | - | - | - |'

    conclusion = (
        '최근 7일 게시일 기준으로 검증된 Cluster#3 신규 source는 확인되지 않았다.'
        if not verified_recent
        else f'최근 7일 게시일 기준 Cluster#3 후보 {len(verified_recent)}건이 확인됐다.'
    )
    contamination = (
        f'DDG 주간 검색 결과 안에 과거 source 오염 {len(stale)}건이 확인됐다.'
        if stale
        else 'DDG 주간 검색 결과에서 과거 source 오염은 확인되지 않았다.'
    )
    ip_note = (
        f'원문에서 IP가 노출된 후보 {len(source_ip_rows)}건이 있었다.'
        if source_ip_rows
        else '원문 fetch 후보에서 작성자 IP 노출은 확인되지 않았다.'
    )

    return f"""# 최근 7일 관측 window 검증 ({start.isoformat()} ~ {end.isoformat()})

> 생성 명령: `.venv/bin/python scripts/recent_window_check.py --today {end.isoformat()}`
>
> 목적: AI/검색 자동화가 최근 7일 판단에 오래된 게시글·carrier IP·스니펫 결과를 섞어 Cluster#3 귀속을 오염시키는지 확인한다.

## 결론

- {conclusion}
- {contamination}
- {ip_note}
- 따라서 이 window에서는 `@GO174` 검색 노출은 계속 보이지만, 검색 노출일과 게시일을 분리하지 않으면 2025년 11월 증거가 "최근 활동"처럼 오염될 수 있다.
- 모바일/CGNAT IP는 이번 window에서 신규 차단 IOC로 승격하지 않는다. 최근 source date + 직접 게시 증거 + 행위 IOC가 함께 확인될 때만 승격한다.

## 집계

| 항목 | 값 |
|---|---:|
| 검색 쿼리 | {len(query_status)} |
| 검색 결과 행 | {len(rows)} |
| exact IOC 후보 | {len(candidates)} |
| 원문 fetch 성공 | {len(fetched)} |
| 최근 window 검증 후보 | {len(verified_recent)} |
| 과거 source 오염 | {len(stale)} |
| 작성자 IP 원문 노출 | {len(source_ip_rows)} |

## 검색 결과 레벨

| 레벨 | 건수 |
|---|---:|
{''.join(f'| {name} | {count} |' + chr(10) for name, count in sorted(level_counts.items()))}
## 원문 검증 분류

| 분류 | 건수 |
|---|---:|
{classification_rows}

## 쿼리 상태

| 쿼리 | 결과 수 | 오류 |
|---|---:|---|
{query_rows}

## 후보 원문 검증

| 분류 | source date | 원문 IP | exact IOC | fraud keyword | URL |
|---|---|---|---|---|---|
{candidate_table}

## 운영 개선 메모

- DDG `timelimit='w'`는 게시일 기준 window가 아니라 최근 노출/색인 window로 동작할 수 있다.
- 최근성 판단은 검색 결과의 "n days ago"가 아니라 원문 `datePublished` / `작성일` / 캡처 시점으로 해야 한다.
- `stale_source_contamination`은 조사 기록에는 남기되, 현재 차단·귀속·활성 상태 갱신에 사용하지 않는다.
- `verified_recent_candidate`가 아닌 mobile/carrier IP는 `tier2_queue.md` 또는 blocklist 산출물에 넣지 않는다.
"""


def main() -> None:
    args = parse_args()
    end = datetime.strptime(args.today, '%Y-%m-%d').date()
    start = end - timedelta(days=args.days)
    output = (
        Path(args.output)
        if args.output
        else REPORTS / f'recent_window_{start.isoformat()}_{end.isoformat()}.md'
    )
    json_output = (
        Path(args.json_output)
        if args.json_output
        else REPORTS / f'recent_window_{start.isoformat()}_{end.isoformat()}.json'
    )

    rows, query_status = run_search(args.max_results)
    candidates = [
        row for row in rows
        if row.level in ('candidate_exact_ioc_and_fraud', 'candidate_exact_ioc')
    ]
    for row in candidates[: args.fetch_limit]:
        fetch_candidate(row, start, end)
        time.sleep(0.5)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_report(rows, query_status, start, end), encoding='utf-8')
    json_output.write_text(
        json.dumps(
            {
                'window': {'start': start.isoformat(), 'end': end.isoformat()},
                'query_status': query_status,
                'rows': [row_to_json(row) for row in rows],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding='utf-8',
    )
    print(f'report: {output}')
    print(f'json: {json_output}')


if __name__ == '__main__':
    main()
