#!/usr/bin/env python3
"""
investigate_ip → export_tier1_logs(--tier2-columns) → suggest_tier2_from_tier1_logs 를 한 번에 실행.

티어2 임계값(`--tier2-min-hit-domains`, `--tier2-fraud-single`)은 이 스크립트가 단일 소스로
investigate·export·suggest에 동일하게 넘긴다(알 수 없는 인자에 동일 플래그가 있으면 제거 후 주입).

사용법:
    python scripts/run_investigate_pipeline.py 221.143.197.13
    python scripts/run_investigate_pipeline.py --batch --limit 3
    python scripts/run_investigate_pipeline.py --no-export --no-suggest 1.2.3.4
    python scripts/run_investigate_pipeline.py --suggest-apply --tier2-fraud-single 1.2.3.4
    python scripts/run_investigate_pipeline.py -o /tmp/t1.csv --izana-list-pages 0 1.2.3.4
    python scripts/run_investigate_pipeline.py --tier2-force-recompute 1.2.3.4
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = Path(__file__).resolve().parent


def strip_tier2_from_argv(argv: list[str]) -> list[str]:
    out: list[str] = []
    i = 0
    while i < len(argv):
        if argv[i] == '--tier2-min-hit-domains' and i + 1 < len(argv):
            i += 2
            continue
        if argv[i] == '--tier2-fraud-single':
            i += 1
            continue
        out.append(argv[i])
        i += 1
    return out


def build_tier2_suffix(min_hit: int, fraud_single: bool) -> list[str]:
    suf = ['--tier2-min-hit-domains', str(min_hit)]
    if fraud_single:
        suf.append('--tier2-fraud-single')
    return suf


def main() -> None:
    ap = argparse.ArgumentParser(
        description='investigate_ip → export → suggest (단일 티어2 임계값)',
    )
    ap.add_argument(
        '-o',
        '--export-output',
        type=Path,
        default=ROOT / 'data' / 'tier1_export.csv',
        help='export_tier1_logs -o (기본: data/tier1_export.csv)',
    )
    ap.add_argument('--no-export', action='store_true', help='CSV export 생략')
    ap.add_argument('--no-suggest', action='store_true', help='suggest 스크립트 생략')
    ap.add_argument(
        '--suggest-apply',
        action='store_true',
        help='suggest_tier2_from_tier1_logs.py --apply',
    )
    ap.add_argument('--tier2-min-hit-domains', type=int, default=2, metavar='N')
    ap.add_argument('--tier2-fraud-single', action='store_true')
    ap.add_argument(
        '--tier2-force-recompute',
        action='store_true',
        help='export에 --tier2-force-recompute, suggest에 --force-recompute 전달',
    )
    args, unknown = ap.parse_known_args()

    if not unknown:
        ap.print_help()
        print('\n뒤에 investigate_ip 인자를 붙이세요 (예: IP 또는 --batch --limit 3).', file=sys.stderr)
        sys.exit(2)

    py = sys.executable
    inv_base = strip_tier2_from_argv(unknown)
    t2 = build_tier2_suffix(args.tier2_min_hit_domains, args.tier2_fraud_single)
    investigate_cmd = [py, str(SCRIPTS / 'investigate_ip.py')] + inv_base + t2

    def run_step(cmd: list[str], label: str) -> None:
        print(f'[pipeline] {label}:', ' '.join(cmd), file=sys.stderr)
        subprocess.check_call(cmd, cwd=str(ROOT))

    run_step(investigate_cmd, 'investigate_ip')

    if not args.no_export:
        export_cmd = [
            py,
            str(SCRIPTS / 'export_tier1_logs.py'),
            '--tier2-columns',
            '-o',
            str(args.export_output),
        ] + t2
        if args.tier2_force_recompute:
            export_cmd.append('--tier2-force-recompute')
        run_step(export_cmd, 'export_tier1_logs')

    if not args.no_suggest:
        suggest_cmd = [py, str(SCRIPTS / 'suggest_tier2_from_tier1_logs.py')] + t2
        if args.tier2_force_recompute:
            suggest_cmd.append('--force-recompute')
        if args.suggest_apply:
            suggest_cmd.append('--apply')
        run_step(suggest_cmd, 'suggest_tier2_from_tier1_logs')

    print('[pipeline] 완료', file=sys.stderr)


if __name__ == '__main__':
    main()
