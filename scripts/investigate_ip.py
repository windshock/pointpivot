#!/usr/bin/env python3
"""
investigate_ip.py - DuckDuckGo + 다중 사이트 스크래핑(izanaholdings + DDG site:) 기반 IP 자동 조사

사용법:
    python scripts/investigate_ip.py 221.143.197.13
    python scripts/investigate_ip.py 221.143.197.13 --izana-list-pages 0   # 이자나 목록 생략(얕게)
    python scripts/investigate_ip.py 221.143.197.13 --ddg-site-limit 8    # 피해 사이트 DDG 8도메인만
    # 티어1 JSON: data/tier1_logs/  티어2 큐: data/tier2_queue.md (--no-tier1-json / --no-tier2-queue)
    # 소급: scripts/suggest_tier2_from_tier1_logs.py [--apply]  |  원스톱: run_investigate_pipeline.py
    python scripts/investigate_ip.py --batch --limit 5
    python scripts/investigate_ip.py --batch --service svc_a --limit 3
"""

from __future__ import annotations

import argparse
import sys
import time
import warnings
from datetime import date
from pathlib import Path

warnings.filterwarnings('ignore')

try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        print('필요 패키지 없음: pip install ddgs')
        sys.exit(1)

sys.path.insert(0, str(Path(__file__).parent))
from scrapers.generic_ddg import FRAUD_KEYWORDS as DDG_FRAUD_KW
from scrapers.izanaholdings import (
    ISWEB_RE,
    TELEGRAM_RE,
    NON_TG_TOKENS,
    scrape_izanaholdings,
)
from scrapers.generic_ddg import scrape_spam_sites_keywords_via_ddg
from utils import (
    INVESTIGATIONS,
    ROOT,
    append_pivot_queue,
    append_tier2_followup_queue,
    compute_tier2_followup_row,
    get_unverified_ips,
    infer_cluster,
    register_new_domains,
    register_new_telegrams,
    update_index_ip,
    write_tier1_scan_json,
)

UNCLASSIFIED = INVESTIGATIONS / 'unclassified'


def search(query: str, max_results: int = 20) -> list[dict]:
    try:
        with DDGS() as ddgs:
            return list(ddgs.text(query, max_results=max_results))
    except Exception as e:
        print(f'  [DDG 오류] {query!r}: {e}')
        return []


def build_queries(ip: str) -> list[tuple[str, str]]:
    return [
        (f'"{ip}"', 'exact'),
        (f'"{ip}" 내구제 OR 유심 OR 기프티콘 OR 텔레그램', 'fraud'),
    ]


def build_tier1_json_payload(
    ip: str,
    data: dict,
    *,
    tier2_min_hit_domains: int = 2,
    tier2_fraud_single: bool = False,
) -> tuple[dict, tuple[str, str, dict] | None]:
    """JSON 직렬화용 요약 (sets 등 비직렬화 필드 제외).

    반환: (payload, tier2_row). tier2_row는 티어2 트리거 시 compute_tier2_followup_row 결과 튜플,
    미트리거면 None — 큐 append 시 재계산 생략용.
    """
    ddg = data.get('ddg_site_kw') or {}
    kw = dict(ddg)
    kw['_pivot_ip'] = ip
    t2 = compute_tier2_followup_row(
        ip,
        kw,
        min_hit_domains=tier2_min_hit_domains,
        also_single_domain_fraud_snippet=tier2_fraud_single,
    )
    if t2:
        _row, summary, meta = t2
        tier2_default = {
            'eligible': True,
            'summary': summary,
            'priority': meta.get('priority'),
            'trigger': meta.get('trigger'),
            'recommend': meta.get('recommend'),
            'dom_summary': meta.get('dom_summary'),
            'snippet_keywords': meta.get('snippet_keywords'),
            'n_hit_domains': meta.get('n_hit_domains'),
        }
    else:
        tier2_default = {
            'eligible': False,
            'min_hit_domains': tier2_min_hit_domains,
            'fraud_single': tier2_fraud_single,
        }

    payload = {
        'schema_version': 1,
        'ip': ip,
        'ddg_site': {
            'domains_checked': ddg.get('domains_checked'),
            'hits': ddg.get('hits'),
            'keywords': ddg.get('keywords'),
            'per_domain': ddg.get('per_domain'),
        },
        'izana_direct_posts': len(data.get('izana', {}).get('posts', [])),
        'confidence': data.get('confidence'),
        'direct_post': data.get('direct_post'),
        'tier2_default': tier2_default,
    }
    return payload, t2


def extract_iocs(text: str) -> dict:
    tgs = [t for t in TELEGRAM_RE.findall(text) if t.lower() not in NON_TG_TOKENS]
    return {
        'telegram': sorted(set(tgs)),
        'isweb': sorted(set(ISWEB_RE.findall(text))),
        'keywords': [kw for kw in DDG_FRAUD_KW if kw in text],
    }


def investigate(
    ip: str,
    *,
    ddg_site_limit: int | None = None,
    izana_list_pages: int = 15,
) -> dict:
    print(f"\n{'='*60}")
    print(f'  조사 대상: {ip}')
    print(f"{'='*60}")

    all_results: list[dict] = []
    all_iocs: dict = {'telegram': set(), 'isweb': set(), 'keywords': set()}

    for query, label in build_queries(ip):
        print(f'  [DDG:{label}] {query}')
        results = search(query)
        print(f'           결과 {len(results)}건')
        all_results.extend(results)
        combined = ' '.join(r.get('title', '') + ' ' + r.get('body', '') for r in results)
        iocs = extract_iocs(combined)
        all_iocs['keywords'].update(iocs['keywords'])
        time.sleep(1.5)

    izana_data = scrape_izanaholdings(ip, max_list_pages=izana_list_pages)
    all_iocs['telegram'].update(izana_data['iocs']['telegram'])
    all_iocs['isweb'].update(izana_data['iocs']['isweb'])
    all_iocs['keywords'].update(izana_data['iocs']['keywords'])

    ddg_site_kw = scrape_spam_sites_keywords_via_ddg(
        ip, search, max_domains=ddg_site_limit
    )
    all_iocs['keywords'].update(ddg_site_kw['keywords'])
    doms = ddg_site_kw.get('domains_checked') or []
    hits = ddg_site_kw.get('hits') or {}
    with_hits = [d for d, n in hits.items() if n]
    print(
        f"  [DDG:피해사이트] 도메인 {len(doms)}개 순회, "
        f"검색결과>0인 도메인 {len(with_hits)}개"
        + (f": {with_hits[:12]}{'…' if len(with_hits) > 12 else ''}" if with_hits else '')
    )
    if ddg_site_kw['keywords']:
        print(f"  [DDG:피해사이트] 키워드 힌트: {ddg_site_kw['keywords']}")

    direct_post = len(izana_data['posts']) > 0
    has_keywords = bool(all_iocs['keywords'])
    has_telegram = bool(all_iocs['telegram'])
    direct_ioc_count = len(izana_data['iocs']['telegram']) + len(izana_data['iocs']['isweb'])

    if direct_post and direct_ioc_count >= 2:
        confidence = 'HIGH'
    elif direct_post:
        confidence = 'MEDIUM'
    elif has_keywords and has_telegram:
        confidence = 'LOW'
    elif has_keywords or has_telegram:
        confidence = 'LOW'
    elif all_results:
        confidence = 'LOW'
    else:
        confidence = 'UNVERIFIED'

    return {
        'ip': ip,
        'results': all_results,
        'iocs': {k: sorted(v) for k, v in all_iocs.items()},
        'izana': izana_data,
        'ddg_site_kw': ddg_site_kw,
        'has_spam': bool(has_keywords or has_telegram),
        'direct_post': direct_post,
        'confidence': confidence,
    }


def generate_report(data: dict) -> str:
    ip = data['ip']
    iocs = data['iocs']
    results = data['results']
    izana = data.get('izana', {})
    ddg_site_kw = data.get('ddg_site_kw') or {}
    today = date.today().isoformat()

    result_rows = []
    for r in results[:8]:
        title = r.get('title', '').replace('|', '｜')[:55]
        url = r.get('href', '')[:70]
        snippet = r.get('body', '').replace('\n', ' ').replace('|', '｜')[:70]
        result_rows.append(f'| {title} | {url} | {snippet} |')
    results_table = '\n'.join(result_rows) if result_rows else '| (결과 없음) | - | - |'

    izana_posts = izana.get('posts', [])
    izana_rows = []
    for p in izana_posts:
        title = p['title'].replace('|', '｜')[:60]
        url = p['url'][:80]
        author_ip = p.get('author_ip', '-')
        izana_rows.append(f'| {title} | {url} | {author_ip} |')
    izana_table = '\n'.join(izana_rows) if izana_rows else '| (게시글 없음) | - | - |'

    ioc_rows = []
    for tg in iocs['telegram']:
        src = 'izanaholdings.com (직접)' if tg in izana.get('iocs', {}).get('telegram', []) else '간접'
        ioc_rows.append(f'| 텔레그램 | {tg} | {src} | {today} | ❌ |')
    for domain in iocs['isweb']:
        src = 'izanaholdings.com (직접)' if domain in izana.get('iocs', {}).get('isweb', []) else '간접'
        ioc_rows.append(f'| 도메인 | {domain} | {src} | {today} | ❌ |')
    ioc_table = '\n'.join(ioc_rows) if ioc_rows else '| (IOC 없음) | - | - | - | - |'

    author_ips = izana.get('author_ips', [])
    direct_note = (
        f'✅ izanaholdings.com에서 직접 게시 {len(izana_posts)}건 확인'
        if izana_posts
        else '❌ izanaholdings.com 직접 게시 미확인'
    )
    status = 'DONE' if izana_posts else ('PARTIAL' if results else 'UNVERIFIED')

    sources = []
    if results:
        sources.append(f'DuckDuckGo {len(results)}건')
    if izana_posts:
        sources.append(f'izanaholdings 직접 {len(izana_posts)}건')
    doms = ddg_site_kw.get('domains_checked') or []
    if doms:
        sources.append(f'피해사이트 DDG site: 검색 {len(doms)}개 도메인')

    ddg_note = ''
    if doms_chk := ddg_site_kw.get('domains_checked'):
        hmap = ddg_site_kw.get('hits') or {}
        wh = [f'{d}({hmap[d]})' for d in doms_chk if hmap.get(d)]
        ddg_note = (
            f'\n**피해 사이트 DDG 요약 (`spammed_sites.md` ddg_site):** '
            f'{len(doms_chk)}도메인 순회, 검색결과>0인 도메인 {len(wh)}개'
            + (f' — {", ".join(wh[:15])}' + (' …' if len(wh) > 15 else '') if wh else ' — (없음)')
            + '\n'
        )
    if ddg_site_kw.get('keywords'):
        ddg_note += f"**피해 사이트 DDG 키워드 힌트:** {', '.join(ddg_site_kw['keywords'])} (스니펫만, 직접 본문 확인 권장)\n"

    report = f"""# 조사 보고서: {ip}

> ⚠️ 자동 생성 초안. IOC 신규 발견 시 `data/ioc_registry.md` 수동 등록 필요.

**조사일:** {today}
**조사자:** auto (investigate_ip.py + scrapers)
**상태:** {status}
**클러스터:** {data.get('cluster', '미분류')}
**신뢰도:** {data['confidence']}

---

## IP 기본 정보

| 항목 | 값 |
|---|---|
| IP | {ip} |
| ISP / ASN | (수동 확인 필요) |
| IP 범위 (/24) | {'.'.join(ip.split('.')[:3])}.0/24 |
| AbuseIPDB | (수동 확인 필요) |
| 인프라 유형 | (수동 확인 필요) |

---

## 사용된 검색 방법

- [x] DuckDuckGo: `"{ip}"`
- [x] DuckDuckGo: `"{ip}" 내구제 OR 유심 OR 기프티콘 OR 텔레그램`
- [x] izanaholdings.com 게시판 직접 검색
- [x] `data/spammed_sites.md` 등록 도메인에 대한 `site:도메인 "{ip}"` DDG 검색 (키워드 힌트만)

**수집 결과:** {', '.join(sources) if sources else '결과 없음'}
{ddg_note}
---

## izanaholdings.com 직접 게시 확인

{direct_note}

| 게시글 제목 | URL | 작성자 IP |
|---|---|---|
{izana_table}

{"**추가 발견 작성자 IP:** " + ', '.join(author_ips) if author_ips else ''}

---

## DuckDuckGo 검색 결과 (상위 8건)

| 제목 | URL | 스니펫 |
|---|---|---|
{results_table}

---

## 추출된 IOC

| IOC 유형 | 값 | 출처 | 발견일 | ioc_registry 등록 |
|---|---|---|---|---|
{ioc_table}

**발견된 사기 키워드:** {', '.join(iocs['keywords']) if iocs['keywords'] else '없음'}

---

## 클러스터 귀속 근거

> 신뢰도 `{data['confidence']}` — {'izana 직접 게시 확인됨' if izana_posts else 'DDG 스니펫 기반, 직접 검증 권장'}

---

## 다음 피벗 대상

{"".join(f"- [ ] {tg} — 텔레그램 핸들 피벗 (investigate_ioc.py){chr(10)}" for tg in iocs['telegram'])}{"".join(f"- [ ] {d} — 도메인 직접 조회{chr(10)}" for d in iocs['isweb'])}{"".join(f"- [ ] {aip} — 새로 발견된 작성자 IP 조사{chr(10)}" for aip in author_ips if aip != ip)}- [ ] ioc_registry.md에 신규 IOC 등록
"""
    return report


def main():
    parser = argparse.ArgumentParser(description='IP 자동 조사 스크립트')
    parser.add_argument('ip', nargs='?', help='조사할 IP 주소')
    parser.add_argument('--batch', action='store_true', help='seed_ips.md에서 UNVERIFIED IP 배치 조사')
    parser.add_argument('--limit', type=int, default=5, help='배치 최대 처리 수 (기본: 5)')
    parser.add_argument('--service', choices=['svc_a', 'gifticon', 'svc_c'], help='특정 서비스만 처리')
    parser.add_argument('--dry-run', action='store_true', help='파일 저장 없이 출력만')
    parser.add_argument(
        '--ddg-site-limit',
        type=int,
        default=None,
        metavar='N',
        help='피해 사이트 DDG site: 순회를 상위 N도메인으로 제한 (기본: 전부)',
    )
    parser.add_argument(
        '--izana-list-pages',
        type=int,
        default=15,
        metavar='N',
        help='izanaholdings 목록 순회 최대 페이지 (0=검색만, 목록 생략. 기본 15)',
    )
    parser.add_argument(
        '--no-tier1-json',
        action='store_true',
        help='data/tier1_logs/*.json 저장 생략',
    )
    parser.add_argument(
        '--tier2-min-hit-domains',
        type=int,
        default=2,
        metavar='N',
        help='피해 도메인 중 DDG 결과>0 이 N개 이상이면 data/tier2_queue.md에 후속 행 추가 (기본 2)',
    )
    parser.add_argument(
        '--tier2-fraud-single',
        action='store_true',
        help='히트 도메인 1개여도 스니펫에 사기 키워드가 있으면 티어2 큐에 추가',
    )
    parser.add_argument(
        '--no-tier2-queue',
        action='store_true',
        help='티어2 후속 큐(tier2_queue.md) 자동 추가 안 함',
    )
    args = parser.parse_args()

    UNCLASSIFIED.mkdir(parents=True, exist_ok=True)

    if args.batch:
        ips = get_unverified_ips(args.service)
        if not ips:
            print('조사할 UNVERIFIED IP가 없습니다.')
            return
        ips = ips[: args.limit]
        print(f'배치 조사 시작: {len(ips)}개 IP')
        for ip in ips:
            run_single(
                ip,
                args.dry_run,
                ddg_site_limit=args.ddg_site_limit,
                izana_list_pages=args.izana_list_pages,
                write_tier1_json=not args.no_tier1_json,
                tier2_queue=not args.no_tier2_queue,
                tier2_min_hit_domains=args.tier2_min_hit_domains,
                tier2_fraud_single=args.tier2_fraud_single,
            )
            time.sleep(3)
    elif args.ip:
        run_single(
            args.ip,
            args.dry_run,
            ddg_site_limit=args.ddg_site_limit,
            izana_list_pages=args.izana_list_pages,
            write_tier1_json=not args.no_tier1_json,
            tier2_queue=not args.no_tier2_queue,
            tier2_min_hit_domains=args.tier2_min_hit_domains,
            tier2_fraud_single=args.tier2_fraud_single,
        )
    else:
        parser.print_help()


def run_single(
    ip: str,
    dry_run: bool = False,
    *,
    ddg_site_limit: int | None = None,
    izana_list_pages: int = 15,
    write_tier1_json: bool = True,
    tier2_queue: bool = True,
    tier2_min_hit_domains: int = 2,
    tier2_fraud_single: bool = False,
):
    data = investigate(
        ip,
        ddg_site_limit=ddg_site_limit,
        izana_list_pages=izana_list_pages,
    )
    iocs = data['iocs']
    today = date.today().isoformat()

    cluster = infer_cluster(iocs['telegram'] + iocs['isweb'])
    data['cluster'] = cluster

    izana = data.get('izana', {})
    author_ips = [a for a in izana.get('author_ips', []) if a != ip]

    tier1_payload: dict | None = None
    tier2_pre: tuple[str, str, dict] | None = None
    if not dry_run and write_tier1_json:
        tier1_payload, tier2_pre = build_tier1_json_payload(
            ip,
            data,
            tier2_min_hit_domains=tier2_min_hit_domains,
            tier2_fraud_single=tier2_fraud_single,
        )
        t1_path = write_tier1_scan_json(ip, tier1_payload)
        try:
            rel = t1_path.relative_to(ROOT)
        except ValueError:
            rel = t1_path
        print(f'  티어1 JSON 저장: {rel}')
    elif not dry_run and tier2_queue:
        tier1_payload, tier2_pre = build_tier1_json_payload(
            ip,
            data,
            tier2_min_hit_domains=tier2_min_hit_domains,
            tier2_fraud_single=tier2_fraud_single,
        )

    if not dry_run and tier2_queue:
        if tier2_pre is not None:
            t2_msg = append_tier2_followup_queue(
                ip,
                data.get('ddg_site_kw') or {},
                min_hit_domains=tier2_min_hit_domains,
                also_single_domain_fraud_snippet=tier2_fraud_single,
                precomputed=tier2_pre,
            )
        else:
            t2_msg = append_tier2_followup_queue(
                ip,
                data.get('ddg_site_kw') or {},
                min_hit_domains=tier2_min_hit_domains,
                also_single_domain_fraud_snippet=tier2_fraud_single,
                assume_ineligible=True,
            )
        if t2_msg:
            print(f'  티어2 큐 추가: {t2_msg}')

    if not dry_run:
        new_tg = register_new_telegrams(iocs['telegram'], ip, today)
        new_dom = register_new_domains(iocs['isweb'], ip, today)
        if new_tg:
            print(f'  ioc_registry 신규 등록 (텔레그램): {new_tg}')
        if new_dom:
            print(f'  ioc_registry 신규 등록 (도메인): {new_dom}')
        added = append_pivot_queue(author_ips, f'izanaholdings pivot from {ip}', '')
        if added:
            print(f'  pivot_queue.md 추가: {added}')

    report = generate_report(data)
    out_path = UNCLASSIFIED / f'{ip}.md'

    if dry_run:
        print('\n[dry-run] 보고서 미리보기:')
        print(report[:1200] + '\n...')
    else:
        out_path.write_text(report, encoding='utf-8')
        print(f'\n  보고서 저장: {out_path}')
        rel_path = str(out_path.relative_to(INVESTIGATIONS))
        updated = update_index_ip(ip, 'PARTIAL', rel_path)
        if updated:
            print(f'  INDEX.md 업데이트: {ip} → PARTIAL')

    print(f'\n  결과 요약:')
    print(f"    검색 결과: {len(data['results'])}건 (DDG) + izana {len(izana.get('posts', []))}건")
    print(f"    텔레그램:  {iocs['telegram'] or '없음'}")
    print(f"    도메인:    {iocs['isweb'] or '없음'}")
    print(f"    키워드:    {iocs['keywords'] or '없음'}")
    print(f'    클러스터:  {cluster}')
    print(f"    신뢰도:    {data['confidence']}")


if __name__ == '__main__':
    main()
