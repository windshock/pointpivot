# PointPivot

**국내 서비스 대상 유출 계정 기반 ATO 및 포인트/기프티콘 탈취 행위망 추적 프로젝트**

---

## 프로젝트 개요

이 프로젝트는 단순 IP 조회 도구가 아니다.

국내 서비스(서비스A, 기프티콘, 서비스C 등)를 대상으로 한 **Credential Stuffing 기반 ATO(Account Takeover)** 및 **포인트/기프티콘 탈취 행위**를 추적한다. seed IP에서 시작해 반복 피벗(pivot)으로 행위망을 확장하고 클러스터링하는 **OSINT 기반 fraud infrastructure mapping** 프로젝트다.

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
├── README.md                       # 이 파일 — 프로젝트 전체 개요
├── METHODOLOGY.md                  # 조사 방법론, 피벗 절차, 분류 체계
├── STATUS.md                       # 현재 진행 상태 (LLM 인수인계용)
│
├── data/
│   ├── seed_ips.md                 # 서비스별 seed IP 목록 (서비스A/서비스C/기프티콘)
│   ├── ioc_registry.md             # 수집된 IOC 목록 (텔레그램/닉네임/도메인 등)
│   ├── campaigns.md                # 식별된 캠페인/클러스터 정의
│   └── spammed_sites.md            # 스팸 피해 사이트 목록
│
├── investigations/
│   └── 221.143.197.136.md          # IP별 개별 조사 보고서
│
└── reports/
    └── (생성된 종합 보고서)
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

→ `investigations/221.143.197.136.md` 참조

---

## 다음 에이전트를 위한 빠른 시작

1. `STATUS.md` 먼저 읽어라 — 현재 어디까지 했고 다음에 뭘 해야 하는지 명시됨
2. `METHODOLOGY.md` 읽어라 — 피벗 절차와 분류 체계 확인
3. `data/ioc_registry.md`에서 미조사 IOC 확인
4. 해당 IOC를 Google 검색으로 피벗 → 결과를 `investigations/`에 저장 → `data/ioc_registry.md` 업데이트

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
