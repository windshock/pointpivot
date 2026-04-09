#!/usr/bin/env python3
"""
data/tier1_logs/*.json 을 도메인 단위 행으로 펼쳐 CSV로 출력 (피벗·필터용).

사용법:
    python scripts/export_tier1_logs.py -o data/tier1_export.csv
    python scripts/export_tier1_logs.py --stats -o /tmp/t1.csv
    python scripts/export_tier1_logs.py --tier2-columns -o data/tier1_export.csv
    python scripts/export_tier1_logs.py path/to/one.json

per_domain이 비면 domain=_scan_ 요약 행 1줄(--no-scan-summary-row 로 끔).
CSV에 source_json(원본 파일명) 포함. --tier2-columns 시 tier2_default 우선(utils와 suggest 정합);
임베드 불충분 시 재계산. --tier2-force-recompute 로 임베드 무시.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from utils import tier2_csv_sidecar_for_record  # noqa: E402

DEFAULT_LOGDIR = ROOT / 'data' / 'tier1_logs'

CSV_COLUMNS_BASE = [
    'saved_at',
    'ip',
    'domain',
    'n_results',
    'fraud_keywords',
    'sample_href_1',
    'izana_direct_posts',
    'confidence',
    'source_json',
]

CSV_COLUMNS_TIER2 = [
    'tier2_eligible',
    'tier2_priority',
    'tier2_trigger',
    'tier2_recommend',
    'tier2_summary',
]


def load_record(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def iter_domain_rows(rec: dict, source_json: str = '') -> list[tuple]:
    saved_at = rec.get('saved_at', '')
    ip = rec.get('ip', '')
    izana_n = rec.get('izana_direct_posts', '')
    conf = rec.get('confidence', '')
    ddg = rec.get('ddg_site') or {}
    per = ddg.get('per_domain')
    if not per:
        return []
    rows = []
    for p in per:
        dom = p.get('domain', '')
        n = p.get('n_results', 0)
        fk = ';'.join(p.get('fraud_keywords') or [])
        hrefs = p.get('sample_hrefs') or []
        h1 = (hrefs[0] or '') if hrefs else ''
        rows.append((saved_at, ip, dom, n, fk, h1, izana_n, conf, source_json))
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description='tier1_logs JSON → CSV')
    ap.add_argument(
        '--log-dir',
        type=Path,
        default=DEFAULT_LOGDIR,
        help=f'JSON 디렉터리 (기본: {DEFAULT_LOGDIR})',
    )
    ap.add_argument(
        '-o', '--output',
        type=Path,
        default=None,
        help='출력 CSV 경로 (미지정 시 stdout)',
    )
    ap.add_argument(
        'files',
        nargs='*',
        type=Path,
        help='지정 시 이 파일들만 (없으면 --log-dir/*.json)',
    )
    ap.add_argument(
        '--stats',
        action='store_true',
        help='도메인별 "n>0 인 고유 IP 수"를 stderr에 출력',
    )
    ap.add_argument(
        '--tier2-columns',
        action='store_true',
        help='스캔 IP 기준 티어2 트리거 여부·우선순위·권장 요약 열 추가',
    )
    ap.add_argument(
        '--tier2-min-hit-domains',
        type=int,
        default=2,
        help='--tier2-columns 시 compute_tier2와 동일 기본값',
    )
    ap.add_argument(
        '--tier2-fraud-single',
        action='store_true',
        help='--tier2-columns 시 단일 도메인+스니펫 키워드 트리거 허용',
    )
    ap.add_argument(
        '--tier2-force-recompute',
        action='store_true',
        help='--tier2-columns 시 tier2_default 무시하고 ddg_site만으로 재계산',
    )
    ap.add_argument(
        '--no-scan-summary-row',
        action='store_true',
        help='--tier2-columns 일 때 per_domain이 비어 있어도 `_scan_` 요약 행을 넣지 않음',
    )
    args = ap.parse_args()

    paths = list(args.files) if args.files else sorted(args.log_dir.glob('*.json'))
    all_rows: list[tuple] = []
    domain_ips: dict[str, set[str]] = defaultdict(set)
    cols = CSV_COLUMNS_BASE + (CSV_COLUMNS_TIER2 if args.tier2_columns else [])

    for path in paths:
        if not path.exists():
            print(f'없음: {path}', file=sys.stderr)
            continue
        try:
            rec = load_record(path)
        except (json.JSONDecodeError, OSError) as e:
            print(f'건너뜀 {path}: {e}', file=sys.stderr)
            continue
        src = path.name
        ip = rec.get('ip', '')
        t2_extra: tuple[str, str, str, str, str] = ('', '', '', '', '')
        if args.tier2_columns:
            t2_extra = tier2_csv_sidecar_for_record(
                rec,
                min_hit_domains=args.tier2_min_hit_domains,
                also_single_domain_fraud_snippet=args.tier2_fraud_single,
                ignore_embedded=args.tier2_force_recompute,
            )
        domain_rows = iter_domain_rows(rec, src)
        for row in domain_rows:
            if args.tier2_columns:
                all_rows.append(row + t2_extra)
            else:
                all_rows.append(row)
            dom = row[2]
            n = row[3]
            if n > 0 and dom and dom != '_scan_':
                domain_ips[dom].add(ip)

        if (
            args.tier2_columns
            and not args.no_scan_summary_row
            and not domain_rows
            and (ip or rec.get('ddg_site'))
        ):
            saved_at = rec.get('saved_at', '')
            izana_n = rec.get('izana_direct_posts', '')
            conf = rec.get('confidence', '')
            scan_row = (saved_at, ip or '-', '_scan_', 0, '', '', izana_n, conf, src) + t2_extra
            all_rows.append(scan_row)

    def write_csv(f) -> None:
        w = csv.writer(f)
        w.writerow(cols)
        w.writerows(sorted(all_rows, key=lambda r: (r[1] or '', r[2] or '', r[0] or '')))

    if args.output:
        with args.output.open('w', encoding='utf-8', newline='') as f:
            write_csv(f)
        print(f'Wrote {len(all_rows)} rows → {args.output}', file=sys.stderr)
    else:
        write_csv(sys.stdout)

    if args.stats:
        print('\n# 도메인별: DDG n>0 을 기록한 고유 IP 수', file=sys.stderr)
        for dom in sorted(domain_ips, key=lambda d: -len(domain_ips[d])):
            print(f'  {dom}\t{len(domain_ips[dom])}', file=sys.stderr)


if __name__ == '__main__':
    main()
