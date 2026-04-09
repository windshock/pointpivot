# PointPivot 현황 요약 (Summary)

> 자동 생성: 2026-04-09

---

## 조사 진행률

| 서비스 | 전체 | DONE | PARTIAL | UNVERIFIED | 진행률 |
|---|---|---|---|---|---|
| 서비스A | 8 | 2 | 6 | 0 | 100% |
| 기프티콘 | 25 | 1 | 24 | 0 | 100% |
| 서비스C | 31 | 0 | 31 | 0 | 100% |
| **합계** | **64** | **3** | **61** | **0** | **100%** |

---

## 식별된 IOC

| 유형 | 개수 | 비고 |
|---|---|---|
| 텔레그램 핸들 | 18 | DONE/PARTIAL: 5 |
| 도메인/URL | 4 | isweb.co.kr 기반 홍보 사이트 |
| 피해 사이트 | 21 | 스팸 게시글 확인된 사이트 수 |

---

## 블록리스트 현황

| 산출물 | 항목 수 | 최소 신뢰도 |
|---|---|---|
| blocklist_ip.txt | 7 | MEDIUM |
| ioc_telegram.txt | 5 | PARTIAL 이상 |

---

## 식별된 클러스터

| 클러스터 | 상태 | IP 수 | 핵심 IOC |
|---|---|---|---|
| Cluster#1 | 활성 | 9 | @brrsim_77, @abab1768, @the_usim |
| Cluster#2 | 미분석 | 0 | (Vultr VPS 대역) |
| 미분류 | - | 60 | - |

---

## 다음 우선 작업 (STATUS.md 참조)

1. `python scripts/investigate_ip.py --batch --service svc_a --limit 5`
2. `python scripts/investigate_ip.py --batch --service svc_c --limit 5`
3. `python scripts/investigate_ip.py --batch --service gifticon --limit 10`
4. `python scripts/generate_reports.py` (재실행하면 자동 업데이트)
