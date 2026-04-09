#!/usr/bin/env python3
"""
data/tier2_queue.md 8열 표에서 「추가일」이 N일 이전인 데이터 행을 stdout에 출력.
처리 완료·재검증용 체크리스트로 쓰기 좋음.

사용법:
    python scripts/report_tier2_queue_stale.py
    python scripts/report_tier2_queue_stale.py --days 14
    python scripts/report_tier2_queue_stale.py --count-only
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_QUEUE = ROOT / 'data' / 'tier2_queue.md'


def iter_tier2_data_rows(text: str):
    """각 행을 셀 리스트로 반환 (8열 티어2 표)."""
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped.startswith('|') and ' IP ' in stripped and '우선순위' in stripped:
            break
        i += 1
    if i >= len(lines):
        return
    i += 2  # 헤더 + 구분선
    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped.startswith('|'):
            break
        if stripped.startswith('|---'):
            i += 1
            continue
        parts = [p.strip() for p in stripped.strip('|').split('|')]
        if len(parts) >= 8 and parts[0] != 'IP':
            yield parts
        i += 1


def main() -> None:
    ap = argparse.ArgumentParser(description='tier2_queue.md 오래된 행 나열')
    ap.add_argument('--path', type=Path, default=DEFAULT_QUEUE)
    ap.add_argument('--days', type=int, default=7, metavar='N', help='추가일이 오늘−N일보다 이전이면 stale')
    ap.add_argument('--count-only', action='store_true', help='개수만 stderr')
    args = ap.parse_args()

    if not args.path.exists():
        print(f'없음: {args.path}', file=sys.stderr)
        sys.exit(1)

    text = args.path.read_text(encoding='utf-8')
    cutoff = date.today() - timedelta(days=args.days)
    stale: list[list[str]] = []
    bad_date = 0

    for parts in iter_tier2_data_rows(text):
        ds = parts[6] if len(parts) > 6 else ''
        try:
            row_d = date.fromisoformat(ds)
        except ValueError:
            bad_date += 1
            continue
        if row_d < cutoff:
            stale.append(parts)

    if args.count_only:
        print(f'stale={len(stale)} (cutoff {cutoff}, rows_with_bad_date={bad_date})', file=sys.stderr)
        return

    for parts in stale:
        print('\t'.join(parts[:8]))
    print(
        f'# stale {len(stale)}건 (추가일 < {cutoff}, --days {args.days}, 날짜파싱실패 {bad_date})',
        file=sys.stderr,
    )


if __name__ == '__main__':
    main()
