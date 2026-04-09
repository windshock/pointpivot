#!/usr/bin/env python3
"""
generate_reports.py - 조사 데이터에서 현황 요약 자동 생성

생성 파일:
  reports/summary.md  - 전체 현황 요약 (커버리지·클러스터·IOC 집계)

IOC 원본은 data/ioc_registry.md, IP 원본은 investigations/INDEX.md.
STIX/CSV 표준 포맷 export는 미래 계획(충분한 DONE 확보 후).

사용법:
  python scripts/generate_reports.py
"""

import argparse
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

# utils.py가 같은 scripts/ 폴더에 있음
sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    ROOT,
    parse_index, parse_seed_ips, parse_telegram_iocs, parse_domain_iocs,
    parse_spammed_sites,
)

REPORTS = ROOT / "reports"
TODAY = date.today().isoformat()


def write_summary():
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

## IOC 원본 경로

- **IP 전체 목록·상태:** [`investigations/INDEX.md`](../investigations/INDEX.md)
- **텔레그램·도메인·닉네임:** [`data/ioc_registry.md`](../data/ioc_registry.md)
- **클러스터 상세:** [`data/campaigns.md`](../data/campaigns.md)
- **피해 사이트:** [`data/spammed_sites.md`](../data/spammed_sites.md)

> 표준 포맷 export(STIX/CSV)는 DONE IP가 충분히 확보된 뒤 계획.

---

## 다음 우선 작업

→ [`STATUS.md`](../STATUS.md) 참조
"""
    path.write_text(content, encoding='utf-8')
    print(f'  summary.md 생성 완료')


def main():
    parser = argparse.ArgumentParser(description='PointPivot 현황 요약 생성')
    parser.parse_args()

    REPORTS.mkdir(exist_ok=True)
    print(f'\n현황 요약 생성 중 ({TODAY})...')

    write_summary()

    print(f'\n완료. reports/summary.md 확인: {REPORTS / "summary.md"}')


if __name__ == '__main__':
    main()
