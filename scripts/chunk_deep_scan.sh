#!/usr/bin/env bash
# chunk_deep_scan.sh
# 1시간 단위(약 15개 IP)로 끊어서 심층 스캔(DDG site: 검색 포함)을 실행하는 래퍼 스크립트.

set -euo pipefail

cd "$(dirname "$0")/.."

LIMIT=${1:-15}

echo "==========================================================="
echo "  [POS 제휴사 IP 심층 스캔 (1시간 청크)]"
echo "  처리 대상: 최대 ${LIMIT}개 IP"
echo "  모드: --batch --service pos --ddg-site-limit 제거 (전수 검사)"
echo "==========================================================="

.venv/bin/python scripts/investigate_ip.py --batch --service pos --limit "$LIMIT"

echo "==========================================================="
echo "  청크 처리 완료. 남은 작업은 스크립트를 다시 실행하세요."
echo "==========================================================="
