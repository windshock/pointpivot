#!/usr/bin/env python3
"""
generate_reports.py - 조사 결과에서 방어 산출물 자동 생성

생성 파일:
  reports/blocklist_ip.txt       - 신뢰도 HIGH/MEDIUM 확인된 IP
  reports/ioc_telegram.txt       - 확인된 텔레그램 핸들
  reports/detection_keywords.txt - 탐지 키워드 (브랜드명 + 사기 키워드)
  reports/summary.md             - 전체 현황 요약

사용법:
  python scripts/generate_reports.py
  python scripts/generate_reports.py --min-confidence MEDIUM
  python scripts/generate_reports.py --verbose
"""

import argparse
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

# utils.py가 같은 scripts/ 폴더에 있음
sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    ROOT, INVESTIGATIONS,
    parse_index, parse_seed_ips, parse_telegram_iocs, parse_domain_iocs,
    parse_brand_names, parse_spammed_sites,
    read_report_confidence,
    read_report_lifecycle,
    default_ttl_days_for_infra,
    blocklist_entry_expired,
)

REPORTS = ROOT / "reports"
TODAY = date.today().isoformat()

CONFIDENCE_RANK = {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1, 'UNVERIFIED': 0}

DETECTION_KEYWORDS = [
    # 사기 서비스 키워드
    '선불유심', '내구제', '유심내구제', '유심매입', '소액대출', '급전', '비상금',
    '포인트현금화', '기프티콘현금화', '상품권매입', '계정구매', '아이디매매',
    # 플랫폼 키워드
    '서비스A', '기프티콘', '서비스C',
]


def get_blocklist_ips(min_confidence: str = 'MEDIUM') -> list[dict]:
    """블록리스트에 포함할 IP 목록 반환"""
    min_rank = CONFIDENCE_RANK.get(min_confidence, 2)
    entries = parse_index()
    result = []

    for entry in entries:
        if entry.status != 'DONE':
            continue

        # 보고서 파일에서 신뢰도 읽기
        confidence, cluster = read_report_confidence(entry.report_path)
        entry.confidence = confidence

        lc = read_report_lifecycle(entry.report_path)
        if lc.get('lifecycle_state') in ('STALE', 'RETIRED'):
            continue

        ttl = lc.get('ttl_days')
        if ttl is None:
            ttl = default_ttl_days_for_infra(entry.infra)
        last_seen = lc.get('last_seen')
        if blocklist_entry_expired(last_seen, ttl, date.today()):
            continue

        rank = CONFIDENCE_RANK.get(confidence, 0)
        if rank >= min_rank:
            exp_s = ''
            if last_seen and ttl:
                exp = last_seen + timedelta(days=ttl)
                exp_s = f'expires {exp.isoformat()}'
            result.append({
                'ip': entry.ip,
                'confidence': confidence,
                'cluster': cluster or entry.cluster,
                'service': entry.service,
                'status': entry.status,
                'expires_note': exp_s,
            })

    # 중복 제거 (동일 IP 여러 서비스)
    seen = {}
    deduped = []
    for r in result:
        if r['ip'] not in seen:
            seen[r['ip']] = r
            deduped.append(r)
        else:
            # 서비스 병합
            existing = seen[r['ip']]
            for s in r['service'].split(','):
                if s and s not in existing['service']:
                    existing['service'] += f',{s}'
            if r.get('expires_note') and not existing.get('expires_note'):
                existing['expires_note'] = r['expires_note']

    return sorted(deduped, key=lambda x: (x['cluster'], x['ip']))


def write_blocklist(ips: list[dict], min_confidence: str):
    path = REPORTS / 'blocklist_ip.txt'
    lines = [
        f'# PointPivot IP Blocklist',
        f'# Generated: {TODAY}',
        f'# Min confidence: {min_confidence}',
        f'# Total: {len(ips)} IPs',
        f'# Format: IP  # Cluster | Confidence | Services',
        '',
    ]

    cluster_groups = defaultdict(list)
    for entry in ips:
        cluster_groups[entry['cluster']].append(entry)

    for cluster, group in sorted(cluster_groups.items()):
        lines.append(f'# --- {cluster} ---')
        for e in group:
            tail = e.get('expires_note', '')
            extra = f' | {tail}' if tail else ''
            lines.append(f"{e['ip']}  # {e['cluster']} | {e['confidence']} | {e['service']}{extra}")
        lines.append('')

    path.write_text('\n'.join(lines), encoding='utf-8')
    print(f'  blocklist_ip.txt: {len(ips)}개 IP')
    return len(ips)


def write_telegram_iocs():
    path = REPORTS / 'ioc_telegram.txt'
    iocs = parse_telegram_iocs()
    active = [t for t in iocs if t.pivot_status in ('DONE', 'PARTIAL')]

    lines = [
        f'# PointPivot Telegram IOC List',
        f'# Generated: {TODAY}',
        f'# Total: {len(active)} handles',
        '',
    ]

    for t in active:
        brand = f' ({t.brand})' if t.brand and t.brand != '-' else ''
        lines.append(f'{t.handle}{brand}  # {t.cluster} | {t.pivot_status}')

    path.write_text('\n'.join(lines), encoding='utf-8')
    print(f'  ioc_telegram.txt: {len(active)}개 핸들')
    return len(active)


def write_domain_iocs():
    path = REPORTS / 'ioc_domains.txt'
    iocs = parse_domain_iocs()
    active = [d for d in iocs if d.pivot_status in ('DONE', 'PARTIAL', 'UNVERIFIED')]

    lines = [
        f'# PointPivot Domain IOC List',
        f'# Generated: {TODAY}',
        f'# Total: {len(active)} domains',
        '',
    ]

    for d in active:
        lines.append(f'{d.domain}  # {d.ioc_type} | {d.linked_handle} | {d.cluster}')

    path.write_text('\n'.join(lines), encoding='utf-8')
    print(f'  ioc_domains.txt: {len(active)}개 도메인')
    return len(active)


def write_detection_keywords():
    path = REPORTS / 'detection_keywords.txt'
    brands = parse_brand_names()

    lines = [
        f'# PointPivot Detection Keywords',
        f'# Generated: {TODAY}',
        f'# WAF/IDS 차단 룰, 스팸 필터에 활용',
        '',
        '# === 브랜드명 (확인된 사기 조직) ===',
    ]
    for b in brands:
        lines.append(b)

    lines += ['', '# === 사기 서비스 키워드 ===']
    for kw in DETECTION_KEYWORDS:
        lines.append(kw)

    path.write_text('\n'.join(lines), encoding='utf-8')
    print(f'  detection_keywords.txt: 브랜드 {len(brands)}개 + 키워드 {len(DETECTION_KEYWORDS)}개')


def write_summary(blocklist_count: int, tg_count: int):
    path = REPORTS / 'summary.md'
    entries = parse_index()
    seed_entries = parse_seed_ips()
    sites = parse_spammed_sites()
    tg_iocs = parse_telegram_iocs()
    domain_iocs = parse_domain_iocs()

    # 진행률 집계
    by_service: dict[str, dict] = defaultdict(lambda: {'total': 0, 'done': 0, 'partial': 0})
    for e in seed_entries:
        for svc in e.service.split(','):
            svc = svc.strip()
            if svc:
                by_service[svc]['total'] += 1
                if e.status == 'DONE':
                    by_service[svc]['done'] += 1
                elif e.status == 'PARTIAL':
                    by_service[svc]['partial'] += 1

    # 중복 IP 제거
    seen_ips: set[str] = set()
    unique_entries = []
    for e in entries:
        if e.ip not in seen_ips:
            seen_ips.add(e.ip)
            unique_entries.append(e)
    progress_entries = []
    seen_seed_ips: set[str] = set()
    for e in seed_entries:
        if e.ip in seen_seed_ips:
            continue
        seen_seed_ips.add(e.ip)
        progress_entries.append(e)
    total_unique = len(progress_entries)
    done_unique = sum(1 for e in progress_entries if e.status == 'DONE')
    partial_unique = sum(1 for e in progress_entries if e.status == 'PARTIAL')

    svc_label = {'svc_a': '서비스A', 'gifticon': '기프티콘', 'svc_c': '서비스C'}
    svc_order = ('svc_a', 'gifticon', 'svc_c')
    svc_rows = []
    for svc in svc_order:
        if svc not in by_service:
            continue
        stats = by_service[svc]
        t = stats['total']
        d = stats['done']
        p = stats['partial']
        u = t - d - p
        pct = round((d + p) / t * 100) if t else 0
        svc_rows.append(f"| {svc_label.get(svc, svc)} | {t} | {d} | {p} | {u} | {pct}% |")

    progress_total = sum(stats['total'] for stats in by_service.values())
    progress_done = sum(stats['done'] for stats in by_service.values())
    progress_partial = sum(stats['partial'] for stats in by_service.values())
    progress_unverified = progress_total - progress_done - progress_partial
    progress_pct = round((progress_done + progress_partial) / progress_total * 100) if progress_total else 0

    n_cluster1 = sum(1 for e in unique_entries if 'Cluster#1' in e.cluster)
    n_cluster2 = sum(1 for e in unique_entries if 'Cluster#2' in e.cluster)
    n_unclassified = sum(1 for e in unique_entries if e.cluster.strip() in ('-', '미분류', ''))
    total_tracked = len(unique_entries)

    content = f"""# PointPivot 현황 요약 (Summary)

> 자동 생성: {TODAY}

---

## 조사 커버리지 (seed IP 기준)

| 서비스 | 전체 | DONE | PARTIAL | UNVERIFIED | 1차 스캔 커버리지 |
|---|---|---|---|---|---|
{''.join(row + chr(10) for row in svc_rows)}| **합계** | **{progress_total}** | **{progress_done}** | **{progress_partial}** | **{progress_unverified}** | **{progress_pct}%** |

> **1차 스캔 커버리지** = DONE + PARTIAL (DDG 검색·초안 보고서까지 완료된 비율).  
> **확정률 (DONE)** = {progress_done}/{progress_total} ({round(progress_done/progress_total*100) if progress_total else 0}%) — 직접 게시 증거 또는 복수 출처로 확인 완료.

---

## 추적 IP 및 클러스터 배분

| 클러스터 | 상태 | IP 수 | 핵심 IOC |
|---|---|---|---|
| Cluster#1 | 🔴 활성 | {n_cluster1} | @brrsim_77, @abab1768, @the_usim (내구제/유심 스팸) |
| Cluster#2 | 🟡 부분 확인 | {n_cluster2} | @YY77882 (불법 의약품 자동화, Vultr VPS) |
| 미분류 | 추가 조사 필요 | {n_unclassified} | 기프티콘 KR_RESIDENTIAL 등 — DDG에서 IOC 미발견 |
| **전체** | | **{total_tracked}** | seed {progress_total} + 피벗 {total_tracked - progress_total} |

---

## 식별된 IOC

| 유형 | 개수 | 비고 |
|---|---|---|
| 텔레그램 핸들 | {len(tg_iocs)} | DONE/PARTIAL: {sum(1 for t in tg_iocs if t.pivot_status in ('DONE','PARTIAL'))} |
| 도메인/URL | {len(domain_iocs)} | isweb.co.kr 기반 홍보 사이트 |
| 피해 사이트 | {len(sites)} | 스팸 게시글 확인된 사이트 수 |

---

## 방어 산출물

| 산출물 | 항목 수 | 기준 |
|---|---|---|
| blocklist_ip.txt | {blocklist_count} | 신뢰도 MEDIUM 이상, DONE 상태, TTL 이내 |
| ioc_telegram.txt | {tg_count} | 피벗 상태 PARTIAL 이상 |

---

## 다음 우선 작업

→ [`STATUS.md`](../STATUS.md) 참조
"""
    path.write_text(content, encoding='utf-8')
    print(f'  summary.md 생성 완료')


def main():
    parser = argparse.ArgumentParser(description='PointPivot 보고서 자동 생성')
    parser.add_argument('--min-confidence', default='MEDIUM',
                        choices=['HIGH', 'MEDIUM', 'LOW'],
                        help='블록리스트 최소 신뢰도 (기본: MEDIUM)')
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()

    REPORTS.mkdir(exist_ok=True)
    print(f'\n보고서 생성 중 ({TODAY})...')

    ips = get_blocklist_ips(args.min_confidence)
    ip_count = write_blocklist(ips, args.min_confidence)
    tg_count = write_telegram_iocs()
    write_domain_iocs()
    write_detection_keywords()
    write_summary(ip_count, tg_count)

    print(f'\n완료. reports/ 폴더 확인: {REPORTS}')

    if args.verbose:
        print('\n[블록리스트 IP]')
        for e in ips:
            print(f"  {e['ip']} ({e['confidence']}, {e['cluster']})")


if __name__ == '__main__':
    main()
