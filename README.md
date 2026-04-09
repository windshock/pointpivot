# PointPivot

**국내 서비스 대상 유출 계정 기반 ATO 및 포인트/기프티콘 탈취 행위망 추적 프로젝트**

> **YouTube 해설:** [내 기프티콘이 사이버 무기로 쓰이는 이유](https://youtu.be/EyRPDV0QFZs)

---

## 발견된 행위망 (2026-04-09 기준)

> 상세: **[`data/campaigns.md`](data/campaigns.md)** | 최신 집계: **[`reports/summary.md`](reports/summary.md)** | IP 전체: **[`investigations/INDEX.md`](investigations/INDEX.md)**

### Cluster #1 — 뽀로로/곰돌이/라부부 통신 네트워크 🔴 활성

국내 포인트·기프티콘 서비스를 노린 **Credential Stuffing + 선불유심내구제 스팸** 행위망.

| 항목 | 내용 |
|------|------|
| IP 대역 | `221.143.197.x` (대구, SK Broadband 고정회선) + 피벗 5개 |
| 텔레그램 | `@brrsim_77` (뽀로로통신), `@abab1768` (곰돌이통신), `@the_usim` (라부부통신) |
| 공통 닉네임 | `kimyoojin18` |
| 확인 IP 수 | 8개 (DONE 2, PARTIAL 6) |
| 활동 기간 | 2025-12 ~ 현재 활성 |
| AbuseIPDB | **미등록** — 글로벌 탐지 불가, 국내 게시판 스팸 패턴 |
| 피해 사이트 | izanaholdings.com, matcl.com 외 20개 이상 |

→ 보고서: [`investigations/cluster1/`](investigations/cluster1/)

### Cluster #2 — 불법 의약품·독극물 판매 자동화 인프라 (@YY77882) 🟡 부분 확인

서비스C 차단 요청 IP가 **Vultr VPS** 기반 자동화 스팸봇으로 확인. Cluster#1과 **완전히 다른 행위자**.

| 항목 | 내용 |
|------|------|
| IP 대역 | `141.164.x.x`, `158.247.x.x`, `64.176.x.x` (Vultr AS20473) — 29개 |
| 텔레그램 | `@YY77882` (불법 의약품·독극물 판매 채널) |
| 스팸 내용 | 졸피뎀, 물뽕, 펜토바르비탈(안락사), 시안화칼륨(독극물) 등 |
| 스팸 사이트 | hanyaksale.com, tokiya.com 등 한국 커뮤니티 (작성자 IP 노출 확인) |
| 조사 상태 | PARTIAL — @YY77882 채널 내용·규모 추가 확인 필요 |

→ 상세: [`data/campaigns.md#cluster-2`](data/campaigns.md)

### 미분류 기프티콘 IP (한국 거주형)

기프티콘 서비스 공격 IP 25개. 전부 KR_RESIDENTIAL (SK/KT/LG/abcle/HyosungITX). DDG 결과 IOC 없음 → Credential Stuffing 자동화 추정.

---

## 현재 조사 현황

| 항목 | 값 |
|------|-----|
| 전체 seed IP | 64개 |
| 1차 조사 완료 | 64개 (100%) |
| DONE | 3개 |
| PARTIAL | 61개 |
| 블록리스트 IP | 7개 (`reports/blocklist_ip.txt`) |
| 확인된 텔레그램 | 18개 (`data/ioc_registry.md`) |

→ 최신 자동 집계: [`reports/summary.md`](reports/summary.md)  
→ 전체 IP 인덱스: [`investigations/INDEX.md`](investigations/INDEX.md)

---

## 왜 이게 중요한가

> "AbuseIPDB에 안 나온다 = 깨끗하다"는 틀렸다.

글로벌 평판 서비스(AbuseIPDB, Spamhaus 등)는 국내 게시판 스팸·내구제·유심 탈취 같은 **로컬형 행위를 포착하지 못한다.** 이 프로젝트는 국내 웹 검색 + 피벗 확장 + 행위망 클러스터링으로 글로벌 서비스가 놓치는 한국 특화 fraud IP를 추적한다.

---

## 디렉토리 구조

```
pointpivot/
├── README.md
├── METHODOLOGY.md                  # 조사 방법론, 피벗 루프(자동/수동), 분류 체계
├── STATUS.md                       # 진행 상태·우선순위 큐 (인수인계)
├── OPS.md                          # 지속 운영 플레이북 (시드 인입, 주기, TTL)
├── RELATIONSHIPS.md                # 관련 레포(anonymous-vps 등)와 데이터 흐름
├── INTERNAL_REPORT.md              # → docs/INTERNAL_REPORT.md 안내
│
├── data/
│   ├── seed_ips.md
│   ├── ioc_registry.md
│   ├── campaigns.md
│   ├── spammed_sites.md            # 피해 사이트 + 스크래퍼 유형 컬럼
│   ├── pivot_queue.md              # 피벗으로 발견된 미조사 IP 대기열
│   ├── tier2_queue.md              # 티어1 신호 후 브라우저·본문 확인용 큐
│   └── tier1_logs/                 # investigate_ip DDG 스캔 JSON (저장소는 *.json 무시)
│
├── investigations/
│   ├── INDEX.md                    # 전 seed 조사 인덱스 (lifecycle 컬럼)
│   ├── TEMPLATE.md
│   ├── cluster1/                   # Cluster #1 확정 IP 보고서
│   └── unclassified/               # 미분류·자동 초안
│
├── scripts/
│   ├── investigate_ip.py
│   ├── investigate_ioc.py          # IOC → IP 역방향 피벗
│   ├── pivot_loop.py               # investigate_ip 다건 순차 실행
│   ├── run_investigate_pipeline.py # 조사 → tier1_export.csv → suggest (원스톱)
│   ├── export_tier1_logs.py        # tier1_logs → 도메인 단위 CSV
│   ├── suggest_tier2_from_tier1_logs.py  # JSON 소급 → 티어2 후보 / --apply
│   ├── sort_tier2_queue.py
│   ├── report_tier2_queue_stale.py
│   ├── generate_reports.py
│   ├── stale_check.py              # 재검증·STALE 큐
│   └── scrapers/                   # 사이트별 스크래퍼 플러그인
│
├── docs/                           # 내부 보고서·영상·자료
└── reports/                        # blocklist, summary 등 자동 생성물
```

---

## 분석 대상 서비스

| 서비스 | 설명 |
|---|---|
| **서비스A** | 국내 포인트 서비스 |
| **기프티콘** | 국내 모바일 상품권 서비스 |
| **서비스C** | 국내 기업용 모바일 상품권 서비스 |

---

## 현재 확보한 Seed 데이터

→ `data/seed_ips.md` 참조

---

## 관련 프로젝트

- **[anonymous-vps](https://github.com/windshock/anonymous-vps)** — 익명·크립토 친화 VPS/호스팅 인벤토리, 사건 IOC(`/32`), 보수적 CIDR 승격, 탐지용 쿼리 생성. PointPivot은 **국내 행위망·캠페인** 중심이고, 서비스C(Vultr 등) seed는 anonymous-vps 산출물과 **풍부화·승격** 관점에서 맞닿는다. 상세: [RELATIONSHIPS.md](RELATIONSHIPS.md).

---

## 이 레포를 처음 보는 사람을 위한 읽기 경로

| 목적 | 읽을 파일 |
|------|-----------|
| **"뭘 발견했냐" 요약** | [`data/campaigns.md`](data/campaigns.md) |
| **현재 숫자/통계** | [`reports/summary.md`](reports/summary.md) (자동 생성) |
| **IP 전체 목록·상태** | [`investigations/INDEX.md`](investigations/INDEX.md) |
| **특정 IP 상세** | `investigations/cluster1/<IP>.md` 또는 `investigations/unclassified/<IP>.md` |
| **텔레그램·도메인 IOC** | [`data/ioc_registry.md`](data/ioc_registry.md) |
| **차단 목록 바로 쓰기** | [`reports/blocklist_ip.txt`](reports/blocklist_ip.txt) |

## 에이전트·기여자를 위한 빠른 시작

1. [`STATUS.md`](STATUS.md) 먼저 — 지금 어디까지, 다음 뭐 해야 하는지
2. [`OPS.md`](OPS.md) — 운영 주기·TTL·자동화 경계
3. [`METHODOLOGY.md`](METHODOLOGY.md) — 피벗 루프(자동/수동), 티어1/2 분류
4. [`data/ioc_registry.md`](data/ioc_registry.md) — 미조사 IOC 확인
5. IP 조사: `python scripts/investigate_ip.py <IP>` (원스톱: `python scripts/run_investigate_pipeline.py <IP>`)
6. 브라우저로 Google 검색·본문 확인 → `investigations/` 저장 → `data/ioc_registry.md` 업데이트
7. `python scripts/generate_reports.py` (리포트 재생성) | `python scripts/stale_check.py` (월간)

---

## 작업 방식 원칙

이 프로젝트는 **Python만으로 하는 프로젝트도 아니고, 브라우저 자동화만으로 하는 프로젝트도 아니다.**

- **브라우저/skill**: Google 검색, Cloudflare 뒤 페이지 열람, 게시글 본문 확인, 스크린샷/증거 확보
- **Python**: 반복 집계, IOC 중복 제거, 링크 검증, 보고서/export 생성
- **Markdown 문서**: 최종 판단, 신뢰도, 클러스터 귀속 근거, TODO 관리

즉, **조사는 브라우저 중심**, **정리는 Python 보조 자동화**, **최종 결론은 문서화**가 기본 운영 모델이다.

### Cloudflare 대응 원칙

- `curl`/단순 fetch가 막히면 브라우저 세션으로 전환한다
- challenge를 통과한 세션에서 본문/스크린샷을 확보한다
- 직접 본문 확인이 안 되면 검색 스니펫, whois, ipinfo 같은 **간접 증거**로만 기록하고 신뢰도를 낮춘다
- 무리한 우회보다 **"직접 확인 실패"를 문서화하고 다음 피벗으로 넘어가는 것**이 우선이다
