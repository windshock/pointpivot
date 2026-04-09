#!/usr/bin/env python3
"""
data/tier1_logs/*.json 을 읽어 티어2 트리거에 해당하는 IP를 나열하거나 큐에 반영.

과거에 `investigate_ip`만 돌리고 티어2 큐 기능이 없을 때 저장된 JSON도 소급 적용 가능.
`tier2_default`가 있으면 eligible 여부·행 내용은 JSON 우선(재계산 생략); 구버전만 compute.
종료 시 stderr에 후보 수와 임베드/재계산 건수를 요약한다.

사용법:
    python scripts/suggest_tier2_from_tier1_logs.py
    python scripts/suggest_tier2_from_tier1_logs.py --apply
    python scripts/suggest_tier2_from_tier1_logs.py --tier2-min-hit-domains 1 --tier2-fraud-single
    python scripts/suggest_tier2_from_tier1_logs.py --force-recompute   # tier2_default 무시
    python scripts/suggest_tier2_from_tier1_logs.py path/to/a.json path/to/b.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from utils import (  # noqa: E402
    append_tier2_followup_queue,
    compute_tier2_followup_row,
    tier2_followup_for_tier1_record_with_source,
)

DEFAULT_LOGDIR = ROOT / 'data' / 'tier1_logs'


def record_to_ddg_kw(rec: dict) -> tuple[str, dict] | None:
    ip = (rec.get('ip') or '').strip()
    if not ip:
        return None
    ddg = dict(rec.get('ddg_site') or {})
    ddg['_pivot_ip'] = ip
    return ip, ddg


def main() -> None:
    ap = argparse.ArgumentParser(description='tier1_logs → 티어2 후보/큐')
    ap.add_argument(
        'files',
        nargs='*',
        type=Path,
        help='지정 시 이 JSON만 (없으면 --log-dir/*.json)',
    )
    ap.add_argument('--log-dir', type=Path, default=DEFAULT_LOGDIR)
    ap.add_argument('--apply', action='store_true', help='data/tier2_queue.md에 append (당일·동일 IP 중복 생략)')
    ap.add_argument('--tier2-min-hit-domains', type=int, default=2)
    ap.add_argument('--tier2-fraud-single', action='store_true')
    ap.add_argument(
        '--force-recompute',
        action='store_true',
        help='tier2_default 무시하고 ddg_site만으로 compute_tier2_followup_row',
    )
    ap.add_argument('--markdown-rows', action='store_true', help='표 한 줄을 stdout에 출력')
    args = ap.parse_args()

    paths = list(args.files) if args.files else sorted(args.log_dir.glob('*.json'))
    if not paths:
        print('JSON 없음.', file=sys.stderr)
        return

    n_suggest = 0
    n_apply = 0
    n_from_embed = 0
    n_from_compute = 0
    for path in paths:
        if not path.exists():
            print(f'없음: {path}', file=sys.stderr)
            continue
        try:
            rec = json.loads(path.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, OSError) as e:
            print(f'건너뜀 {path.name}: {e}', file=sys.stderr)
            continue
        parsed = record_to_ddg_kw(rec)
        if not parsed:
            continue
        ip, ddg = parsed
        if args.force_recompute:
            comp = compute_tier2_followup_row(
                ip,
                ddg,
                min_hit_domains=args.tier2_min_hit_domains,
                also_single_domain_fraud_snippet=args.tier2_fraud_single,
            )
            src = 'compute' if comp else None
        else:
            pair = tier2_followup_for_tier1_record_with_source(
                rec,
                ip,
                ddg,
                min_hit_domains=args.tier2_min_hit_domains,
                also_single_domain_fraud_snippet=args.tier2_fraud_single,
            )
            if pair:
                comp, src = pair
            else:
                comp = None
        if not comp:
            continue
        row, summary, _meta = comp
        n_suggest += 1
        if src == 'embed':
            n_from_embed += 1
        else:
            n_from_compute += 1
        print(summary)
        if args.markdown_rows:
            print(row.rstrip())
        if args.apply:
            msg = append_tier2_followup_queue(
                ip,
                ddg,
                min_hit_domains=args.tier2_min_hit_domains,
                also_single_domain_fraud_snippet=args.tier2_fraud_single,
                precomputed=comp,
            )
            if msg:
                n_apply += 1
                print(f'  → 큐 추가: {msg}', file=sys.stderr)

    src = (
        f'임베드 {n_from_embed}, 재계산 {n_from_compute}'
        if n_suggest
        else '—'
    )
    print(
        f'후보 {n_suggest}건 ({src}), --apply 반영 {n_apply}건',
        file=sys.stderr,
    )


if __name__ == '__main__':
    main()
