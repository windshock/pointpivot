# 운영 플레이북 (OPS)

[METHODOLOGY.md](METHODOLOGY.md)가 **조사 기법**이고, [STATUS.md](STATUS.md)가 **현재 큐**라면, 이 문서는 **프로젝트를 어떻게 돌릴지**에 대한 최소 규약이다.

## 1. Seed 인입

`data/seed_ips.md`에 행을 추가할 때 최소한 다음을 적는다:

- **IP**, **서비스 구분** (서비스A / 기프티콘 / 서비스C)
- **인입 맥락** (차단 요청 티켓 ID, 내부 공유일 등 — 비고 컬럼)
- 가능하면 **첫 관측일**

## 2. 권장 주기

| 주기 | 작업 |
|------|------|
| **주 1회** | [STATUS.md](STATUS.md) 최우선 3~5건 처리, `python scripts/generate_reports.py` |
| **월 1회** | `python scripts/stale_check.py` 로 재검증 후보 검토 (필요 시 `--auto`) |
| **분기** | 블록리스트·클러스터 **lifecycle** 검토, RETIRED 처리, [anonymous-vps](https://github.com/windshock/anonymous-vps) 기여 여부 결정 |

## 3. 자동화 경계

| 자동 OK | 사람 확인 필수 |
|---------|------------------|
| `generate_reports.py`, `blocklist_ip.txt` 생성 | 클러스터 최종 귀속, `campaigns.md` 서술 |
| `investigate_ip.py` 초안 보고서 | DDG 스니펫만 있는 IOC의 **DONE** 판정 |
| `investigate_ioc.py` → `pivot_queue.md` | 무고한 IP·캐시 IP 오탐 제거 |
| izanaholdings **직접 본문**에서 추출한 작성자 IP | 동일 IP의 **법적·운영 차단** 요청 문구 |

DuckDuckGo 스니펫에서 텔레그램 자동 대량 등록은 **끔** — 노이즈 방지 (기존 결정 유지).

## 4. IP 수명 (TTL)

- 조사 보고서에 **`last_seen`**, **`last_verified`**, **`ttl_days`**, **`lifecycle_state`** 를 적는다 ([investigations/TEMPLATE.md](investigations/TEMPLATE.md)).
- 기본 TTL: **KR_RESIDENTIAL 90일**, **VPS_GLOBAL 30일**, **KR_MOBILE 60일** (`scripts/utils.py` 기준).
- `lifecycle_state` 가 `STALE` / `RETIRED` 이면 블록리스트에서 제외 (`generate_reports.py`).

## 5. 증거·민감정보

- URL·스크린샷·게시일을 보고서에 남긴다.
- 불필요한 **개인 식별정보**는 마스킹; 법적 검토가 필요한 공유는 별도 채널.

## 6. 관련 레포

- [RELATIONSHIPS.md](RELATIONSHIPS.md) — PointPivot ↔ anonymous-vps.

## 7. 빠른 명령 모음

```bash
python scripts/generate_reports.py
python scripts/stale_check.py
python scripts/investigate_ip.py 1.2.3.4
python scripts/investigate_ip.py 1.2.3.4 --izana-list-pages 0
python scripts/investigate_ip.py 1.2.3.4 --tier2-fraud-single --no-tier1-json
# 원스톱: 조사 → tier1_export.csv(--tier2-columns) → suggest (티어2 임계값 공통)
python scripts/run_investigate_pipeline.py 1.2.3.4
python scripts/run_investigate_pipeline.py --no-export --no-suggest 1.2.3.4 --dry-run
python scripts/run_investigate_pipeline.py --suggest-apply --tier2-fraud-single 1.2.3.4
python scripts/run_investigate_pipeline.py --tier2-force-recompute 1.2.3.4
python scripts/export_tier1_logs.py --tier2-columns --tier2-force-recompute -o data/tier1_export.csv
python scripts/export_tier1_logs.py -o data/tier1_export.csv
python scripts/export_tier1_logs.py --stats -o data/tier1_export.csv
python scripts/suggest_tier2_from_tier1_logs.py
python scripts/suggest_tier2_from_tier1_logs.py data/tier1_logs/2026-01-01_1_2_3_4.json
python scripts/suggest_tier2_from_tier1_logs.py --apply --tier2-fraud-single
python scripts/suggest_tier2_from_tier1_logs.py --force-recompute --apply
python scripts/export_tier1_logs.py --tier2-columns -o data/tier1_export.csv
python scripts/sort_tier2_queue.py
python scripts/sort_tier2_queue.py --dry-run
python scripts/report_tier2_queue_stale.py --days 7
python scripts/report_tier2_queue_stale.py --count-only
python scripts/investigate_ioc.py "@brrsim_77"
python scripts/investigate_ip.py --batch --service svc_a --limit 5
```
