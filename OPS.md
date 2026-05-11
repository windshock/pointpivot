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
| **주 1회** | [STATUS.md](STATUS.md) 최우선 3~5건 처리, `.venv/bin/python scripts/generate_reports.py` |
| **월 1회** | `.venv/bin/python scripts/stale_check.py` 로 재검증 후보 검토 (필요 시 `--auto`) |
| **분기** | 블록리스트·클러스터 **lifecycle** 검토, RETIRED 처리, [anonymous-vps](https://github.com/windshock/anonymous-vps) 기여 여부 결정 |

## 3. 자동화 경계

| 자동 OK | 사람 확인 필수 |
|---------|------------------|
| `generate_reports.py` → `summary.md` 생성 | 클러스터 최종 귀속, `campaigns.md` 서술 |
| `investigate_ip.py` 초안 보고서 | DDG 스니펫만 있는 IOC의 **DONE** 판정 |
| `investigate_ioc.py` → `pivot_queue.md` | 무고한 IP·캐시 IP 오탐 제거 |
| izanaholdings **직접 본문**에서 추출한 작성자 IP | 동일 IP의 **법적·운영 차단** 요청 문구 |

DuckDuckGo 스니펫에서 텔레그램 자동 대량 등록은 **끔** — 노이즈 방지 (기존 결정 유지).

POS 제휴사 IP는 오탐 검증용 데이터이며 기본 배치에서 제외한다. 검증이 필요할 때만 `investigate_ip.py --batch --service pos`를 명시한다.

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
.venv/bin/python -m pip install -r scripts/requirements.txt

.venv/bin/python scripts/check_repo.py
.venv/bin/python scripts/generate_reports.py
.venv/bin/python scripts/stale_check.py
.venv/bin/python scripts/investigate_ip.py 1.2.3.4
.venv/bin/python scripts/investigate_ip.py 1.2.3.4 --izana-list-pages 0
.venv/bin/python scripts/investigate_ip.py 1.2.3.4 --tier2-fraud-single --no-tier1-json
# 원스톱: 조사 → tier1_export.csv(--tier2-columns) → suggest (티어2 임계값 공통)
.venv/bin/python scripts/run_investigate_pipeline.py 1.2.3.4
.venv/bin/python scripts/run_investigate_pipeline.py --no-export --no-suggest 1.2.3.4 --dry-run
.venv/bin/python scripts/run_investigate_pipeline.py --suggest-apply --tier2-fraud-single 1.2.3.4
.venv/bin/python scripts/run_investigate_pipeline.py --tier2-force-recompute 1.2.3.4
.venv/bin/python scripts/export_tier1_logs.py --tier2-columns --tier2-force-recompute -o data/tier1_export.csv
.venv/bin/python scripts/export_tier1_logs.py -o data/tier1_export.csv
.venv/bin/python scripts/export_tier1_logs.py --stats -o data/tier1_export.csv
.venv/bin/python scripts/suggest_tier2_from_tier1_logs.py
.venv/bin/python scripts/suggest_tier2_from_tier1_logs.py data/tier1_logs/2026-01-01_1_2_3_4.json
.venv/bin/python scripts/suggest_tier2_from_tier1_logs.py --apply --tier2-fraud-single
.venv/bin/python scripts/suggest_tier2_from_tier1_logs.py --force-recompute --apply
.venv/bin/python scripts/export_tier1_logs.py --tier2-columns -o data/tier1_export.csv
.venv/bin/python scripts/sort_tier2_queue.py
.venv/bin/python scripts/sort_tier2_queue.py --dry-run
.venv/bin/python scripts/report_tier2_queue_stale.py --days 7
.venv/bin/python scripts/report_tier2_queue_stale.py --count-only
.venv/bin/python scripts/recent_window_check.py --today 2026-05-11
.venv/bin/python scripts/investigate_ioc.py "@brrsim_77"
.venv/bin/python scripts/investigate_ip.py --batch --service svc_a --limit 5
```

## 8. 선택 검색 provider (SearXNG)

기본 검색 provider는 `ddg`이며, SearXNG는 선택적 Tier-1 후보 수집원이다. SearXNG/DDG 검색 결과는 모두 `search_snippet_only` 증거로 취급하고, 원문 확인 전에는 DONE/HIGH 판정 근거로 쓰지 않는다.

```bash
# SearXNG 로컬 구동은 공식 설정 문서를 우선한다. 아래는 최소 예시.
docker run -d --name searxng -p 8080:8080 searxng/searxng

export POINTPIVOT_SEARCH_PROVIDER=hybrid   # ddg | searxng | hybrid
export POINTPIVOT_SEARXNG_URL=http://localhost:8080

.venv/bin/python scripts/investigate_ip.py 1.2.3.4 --dry-run
```

`hybrid` 기본 동작은 SearXNG를 먼저 시도하고, 실패하거나 0건이면 DDG로 fallback한다. 최근성 판단은 검색 provider의 "최근 결과"가 아니라 원문 `datePublished`/`작성일`/캡처 시점으로 한다.

## 9. 선택 ProxyGather → SearXNG proxy pool

이 기능은 기본 비활성화다. ProxyGather는 public proxy 후보 공급원일 뿐이며, PointPivot이 로컬에서 다시 검증한 proxy만 SearXNG `outgoing.proxies` YAML 조각으로 export한다. Public proxy는 신뢰할 수 없으므로 저민감 Tier-1 후보 검색에만 쓰고, 로그인·쿠키·토큰·비공개 조사 내용은 보내지 않는다.

```bash
# 예시 설정 확인: config/proxy_sources.yml.example
# 필요하면 복사해서 config/proxy_sources.yml로 수정한다.

.venv/bin/python scripts/proxy_collectors/proxygather.py \
  --output config/proxy_candidates.json \
  --limit 200

.venv/bin/python scripts/proxy_collectors/validator.py \
  --input config/proxy_candidates.json \
  --output config/live_proxies.yml \
  --timeout 5 \
  --concurrency 10

.venv/bin/python scripts/proxy_collectors/export_searxng_proxies.py \
  --input config/live_proxies.yml \
  --output config/searxng_proxies.generated.yml
```

`config/searxng_proxies.generated.yml`은 실제 SearXNG `settings.yml`을 덮어쓰지 않는다. 생성된 `outgoing.proxies` 섹션을 사람이 검토한 뒤 SearXNG 설정에 수동 병합한다.

Proxy metadata를 Tier-1 JSON에 요약만 남기려면 SearXNG를 실제로 해당 proxy pool로 구동한 상태에서 명시적으로 켠다. 전체 proxy URL은 보고서나 Tier-1 JSON에 기록하지 않는다.

```bash
export POINTPIVOT_PROXY_MODE=searxng_outgoing
export POINTPIVOT_PROXY_INVENTORY=config/live_proxies.yml
```

생성 파일은 commit하지 않는다: `config/proxy_candidates.json`, `config/live_proxies.yml`, `config/searxng_proxies.generated.yml`, `data/proxy_validation_logs/*.json`.
