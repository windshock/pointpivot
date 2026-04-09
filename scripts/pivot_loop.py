#!/usr/bin/env python3
"""
실험용: 여러 IP에 대해 investigate_ip.py를 순차 실행.
대량 실행 시 DDG·피해 사이트 부하 및 robots/이용약관을 준수할 것.

사용법:
    python scripts/pivot_loop.py 221.143.197.136 221.143.197.135
    python scripts/pivot_loop.py --from-queue --limit 3
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent
INVESTIGATE = ROOT / 'scripts' / 'investigate_ip.py'
QUEUE = ROOT / 'data' / 'pivot_queue.md'


def ips_from_queue(limit: int) -> list[str]:
    if not QUEUE.exists():
        return []
    text = QUEUE.read_text(encoding='utf-8')
    ips = []
    for m in re.finditer(r'^\|\s*(\d{1,3}(?:\.\d{1,3}){3})\s*\|', text, re.MULTILINE):
        ips.append(m.group(1))
    return ips[:limit]


def main():
    p = argparse.ArgumentParser(description='investigate_ip 배치 루프')
    p.add_argument('ips', nargs='*', help='조사할 IP 나열')
    p.add_argument('--from-queue', action='store_true', help='pivot_queue.md 상위 행')
    p.add_argument('--limit', type=int, default=5)
    p.add_argument('--sleep', type=float, default=5.0, help='IP 간 대기(초)')
    args = p.parse_args()

    ips = list(args.ips)
    if args.from_queue:
        ips.extend(ips_from_queue(args.limit))
    ips = ips[: args.limit] if not args.ips else ips

    if not ips:
        print('IP가 없습니다.')
        return

    for ip in ips:
        print(f'\n=== pivot_loop: {ip} ===')
        subprocess.run([sys.executable, str(INVESTIGATE), ip], check=False)
        time.sleep(args.sleep)


if __name__ == '__main__':
    main()
