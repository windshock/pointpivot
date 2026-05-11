#!/usr/bin/env python3
"""Local, network-free repository checks for PointPivot.

Run:
  .venv/bin/python scripts/check_repo.py
"""

from __future__ import annotations

import compileall
import re
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

from generate_reports import build_summary  # noqa: E402
from utils import parse_seed_ips  # noqa: E402


CHECK_PATHS = [
    '.gitignore',
    'README.md',
    'METHODOLOGY.md',
    'OPS.md',
    'config',
    'investigations/TEMPLATE.md',
    'data/seed_ips.md',
    'data/tier2_queue.md',
    'reports/summary.md',
    'scripts',
]


def run_command(cmd: list[str]) -> None:
    print('+', ' '.join(cmd))
    proc = subprocess.run(cmd, cwd=ROOT, check=False)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)


def check_compileall() -> None:
    print('+ compileall scripts')
    ok = compileall.compile_dir(str(SCRIPTS), quiet=1)
    if not ok:
        raise SystemExit('compileall failed')


def check_summary_current() -> None:
    summary_path = ROOT / 'reports' / 'summary.md'
    expected = build_summary()
    actual = summary_path.read_text(encoding='utf-8') if summary_path.exists() else ''
    if actual != expected:
        raise SystemExit(
            'reports/summary.md is stale; run '
            '.venv/bin/python scripts/generate_reports.py'
        )
    print('+ summary current')


def check_tier2_has_no_pos_ips() -> None:
    queue_path = ROOT / 'data' / 'tier2_queue.md'
    if not queue_path.exists():
        print('+ tier2 POS check skipped: queue missing')
        return

    queued_ips = set(re.findall(r'\b\d{1,3}(?:\.\d{1,3}){3}\b', queue_path.read_text()))
    pos_ips = {
        e.ip
        for e in parse_seed_ips(include_pos=True)
        if 'pos' in {s.strip() for s in e.service.split(',') if s.strip()}
    }
    overlap = sorted(queued_ips & pos_ips)
    if overlap:
        raise SystemExit(f'tier2_queue.md contains POS IPs: {", ".join(overlap)}')
    print('+ tier2 has no POS IPs')


def main() -> None:
    check_compileall()
    run_command([sys.executable, str(SCRIPTS / 'test_utils.py')])
    check_summary_current()
    check_tier2_has_no_pos_ips()
    run_command(['git', 'diff', '--check', '--', *CHECK_PATHS])
    print('OK')


if __name__ == '__main__':
    main()
