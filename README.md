# PointPivot

**국내 서비스 대상 유출 계정 기반 ATO 및 포인트/기프티콘 탈취 행위망 추적 프로젝트**

---

## 프로젝트 개요

이 프로젝트는 단순 IP 조회 도구가 아니다.

국내 서비스(서비스A, 기프티콘, 서비스C 등)를 대상으로 한 **Credential Stuffing 기반 ATO(Account Takeover)** 및 **포인트/기프티콘 탈취 행위**를 추적한다. seed IP에서 시작해 반복 피벗(pivot)으로 행위망을 확장하고 클러스터링하는 **OSINT 기반 fraud infrastructure mapping** 프로젝트다.

### 해설 영상 (맥락 이해용)

- **YouTube:** [내 기프티콘이 사이버 무기로 쓰이는 이유](https://youtu.be/EyRPDV0QFZs) — 포인트·기프티콘·범죄 수익 구조에 대한 해설
- **로컬 원본 (저장소 `docs/`):** `내_기프티콘이_사이버_무기로_쓰이는_이유.mp4`, 자막 `.srt`, 오디오 `.m4a`

### 공격 유형 정의

- Credential Stuffing 기반 ATO (Account Takeover)
- 유출 계정 기반 포인트/기프티콘 탈취형 ATO
- Stored-value fraud (서비스A 포인트, 기프티콘, 서비스C)
- Loyalty / reward / gifticon fraud

### 핵심 인식

> "AbuseIPDB에 안 나온다 = 깨끗하다"로 보면 안 된다.

글로벌 평판 서비스(AbuseIPDB, Spamhaus 등)는 국내 게시판 스팸, 내구제, 유심, 포인트 탈취 같은 **로컬형 행위를 포착하지 못한다.** 국내 웹 검색 + 피벗 확장 + 행위망 클러스터링이 핵심 방법론이다.

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

## 핵심 발견사항 요약 (2026-04-06 기준)

### Cluster #1 — 뽀로로/곰돌이/라부부 통신 네트워크 (대구, SK Broadband)

| 항목 | 값 |
|---|---|
| IP 대역 | 221.143.197.x (대구, SK Broadband 고정회선) |
| 확인된 IP | 221.143.197.135, 221.143.197.136, 221.143.197.13 |
| 텔레그램 | @brrsim_77, @abab1768, @the_usim |
| 브랜드명 | 뽀로로통신, 곰돌이통신, 라부부통신 |
| 공통 닉네임 | kimyoojin18 |
| 활동 기간 | 2025-12 ~ 2026-04 (현재 활성) |
| 주요 활동 | 선불유심내구제, 소액대출, 게시판 스팸 |
| AbuseIPDB | 미등록 (신고 이력 없음) — 글로벌 탐지 불가 |

→ `investigations/cluster1/221.143.197.136.md` 참조

---

## 관련 프로젝트

- **[anonymous-vps](https://github.com/windshock/anonymous-vps)** — 익명·크립토 친화 VPS/호스팅 인벤토리, 사건 IOC(`/32`), 보수적 CIDR 승격, 탐지용 쿼리 생성. PointPivot은 **국내 행위망·캠페인** 중심이고, 서비스C(Vultr 등) seed는 anonymous-vps 산출물과 **풍부화·승격** 관점에서 맞닿는다. 상세: [RELATIONSHIPS.md](RELATIONSHIPS.md).

---

## 다음 에이전트를 위한 빠른 시작

1. `STATUS.md` 먼저 읽어라 — 현재 어디까지 했고 다음에 뭘 해야 하는지 명시됨
2. `OPS.md` — 운영 주기·TTL·자동화 경계
3. `METHODOLOGY.md` 읽어라 — 피벗 루프(자동/수동), 분류 체계
4. `data/ioc_registry.md`에서 미조사 IOC 확인
5. IP 조사: `python scripts/investigate_ip.py <IP>` (원스톱·CSV·티어2 후보까지: `python scripts/run_investigate_pipeline.py <IP>`) — IOC 역피벗: `python scripts/investigate_ioc.py "@핸들"`
6. 브라우저로 Google 검색·본문 확인 → `investigations/` 저장 → `data/ioc_registry.md` 업데이트
7. `python scripts/generate_reports.py` — `python scripts/stale_check.py` (월간 권장)

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
