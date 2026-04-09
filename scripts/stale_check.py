#!/usr/bin/env python3
"""
INDEX의 DONE IP 및 조사 보고서의 last_verified 기준 재검증 후보 출력.
`--auto`는 investigate_ip.py를 다시 호출(네트워크 필요).

사용법:
    python scripts/stale_check.py
    python scripts/stale_check.py --auto --limit 3
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    default_ttl_days_for_infra,
    parse_index,
    read_report_lifecycle,
)


def main():
    p = argparse.ArgumentParser(description='STALE / 재검증 큐')
    p.add_argument('--auto', action='store_true', help='후보별 investigate_ip.py 실행')
    p.add_argument('--limit', type=int, default=10)
    args = p.parse_args()

    today = date.today()
    candidates: list[tuple[str, str, int]] = []

    for e in parse_index():
        if e.status != 'DONE':
            continue
        lc = read_report_lifecycle(e.report_path)
        lv = lc.get('last_verified')
        ttl = lc.get('ttl_days') or default_ttl_days_for_infra(e.infra)
        if lv is None:
            candidates.append((e.ip, e.report_path, 9999))
            continue
        half = max(ttl // 2, 14)
        if lv + timedelta(days=half) < today:
            days_ago = (today - lv).days
            candidates.append((e.ip, e.report_path, days_ago))

    candidates.sort(key=lambda x: -x[2])
    print(f'재검증 후보 (DONE, last_verified+TTL/2 경과 또는 미기재): {len(candidates)}건\n')
    for ip, rp, d in candidates[: args.limit]:
        print(f'  {ip}  (보고서: {rp}, 우선순위점수: {d})')

    if args.auto and candidates:
        root = Path(__file__).parent.parent
        for ip, _, _ in candidates[: args.limit]:
            print(f'\n[auto] investigate_ip.py {ip}')
            subprocess.run(
                [sys.executable, str(root / 'scripts' / 'investigate_ip.py'), ip],
                check=False,
            )


if __name__ == '__main__':
    main()
