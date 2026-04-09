#!/usr/bin/env python3
"""
data/tier2_queue.md 테이블 데이터 행을 우선순위(내림차순)로 정렬해 다시 씀.
헤더·설명 문단은 유지.

사용법:
    python scripts/sort_tier2_queue.py
    python scripts/sort_tier2_queue.py --dry-run
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_QUEUE = ROOT / 'data' / 'tier2_queue.md'


def parse_queue_file(text: str) -> tuple[list[str], str, str, list[tuple[list[str], str]], list[str]]:
    """
    반환: (prefix_lines, header_line, separator_line, [(cells, raw_line), ...], suffix_lines)
    """
    lines = text.splitlines(keepends=True)
    prefix: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith('|') and ' IP ' in stripped and '우선순위' in stripped:
            break
        prefix.append(line)
        i += 1
    if i >= len(lines):
        return prefix, '', '', [], []

    header_line = lines[i]
    sep_line = lines[i + 1] if i + 1 < len(lines) else ''
    i += 2

    rows: list[tuple[list[str], str]] = []
    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()
        if not stripped.startswith('|'):
            break
        if stripped.startswith('|---'):
            i += 1
            continue
        parts = [p.strip() for p in stripped.strip('|').split('|')]
        if len(parts) >= 8 and parts[0] != 'IP':
            rows.append((parts, raw if raw.endswith('\n') else raw + '\n'))
        i += 1

    suffix = lines[i:]
    return prefix, header_line, sep_line, rows, suffix


def priority_key(item: tuple[list[str], str]) -> int:
    cells, _ = item
    try:
        return int(cells[1])
    except (ValueError, IndexError):
        return 0


def main() -> None:
    ap = argparse.ArgumentParser(description='tier2_queue.md 우선순위 정렬')
    ap.add_argument('--path', type=Path, default=DEFAULT_QUEUE)
    ap.add_argument('--dry-run', action='store_true', help='stdout에만 미리보기')
    args = ap.parse_args()

    if not args.path.exists():
        print(f'없음: {args.path}', file=sys.stderr)
        sys.exit(1)

    text = args.path.read_text(encoding='utf-8')
    prefix, header, sep, rows, suffix = parse_queue_file(text)
    if not header:
        print('8열 티어2 표 헤더를 찾지 못함.', file=sys.stderr)
        sys.exit(1)

    sorted_rows = sorted(rows, key=priority_key, reverse=True)
    body = ''.join(raw for _cells, raw in sorted_rows)
    out = ''.join(prefix) + header + sep + body + ''.join(suffix)

    if args.dry_run:
        print(out)
        return

    args.path.write_text(out, encoding='utf-8')
    print(f'Sorted {len(rows)} rows by priority (desc) → {args.path}', file=sys.stderr)


if __name__ == '__main__':
    main()
