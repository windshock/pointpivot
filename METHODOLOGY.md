# 조사 방법론 (Methodology)

---

## 1. 핵심 원칙

### 글로벌 평판 서비스의 한계

AbuseIPDB, Spamhaus, VirusTotal 등 글로벌 서비스는 **참고 자료**일 뿐이다.
국내 게시판 스팸, 내구제, 유심, 포인트 탈취 등 **로컬형 행위는 이들 서비스에 거의 등록되지 않는다.**

**"AbuseIPDB 미등록 = 깨끗한 IP"라는 판단은 이 프로젝트에서 금지한다.**

### 주요 조사 방법

글로벌 reputation lookup 중심이 아니라,  
**국내 웹 검색 + 피벗 확장 + 행위망 클러스터링** 중심으로 한다.

---

## 2. 피벗 반복 절차 (Pivot Loop) — Seed → 캠페인 발견

### 2.1 한눈에 보기

- **목표:** seed IP에서 출발해 **IOC**를 모으고, 역피벗으로 **새 IP**를 찾아 **캠페인(클러스터)** 으로 묶는다.
- **종료 조건(권장):** 연속 **N라운드**(예: 2~3) 동안 **신규 IP/IOC가 0건**이거나, `STATUS.md` 큐가 비었을 때.

### 2.2 단계별 [자동] / [수동]

| 단계 | 내용 | 자동/수동 |
|------|------|-----------|
| 1 | Seed IP 후보 확정 (`data/seed_ips.md`, `data/pivot_queue.md`) | [수동] 인입 시 기록 |
| 2 | DDG `"{IP}"` 검색 + **`spammed_sites.md`의 모든 `ddg_site` 도메인**에 대해 `site:도메인 "{IP}"` (티어 1·얕음) | [자동] `investigate_ip.py` |
| 3 | izanaholdings: DDG exact 검색 + (옵션) 목록 순회·`read.htm` (티어 3·깊음) | [자동] `izanaholdings.py`, 깊이는 `METHODOLOGY` §2.4·CLI 플래그로 조절 |
| 4 | Google/Naver·브라우저로 게시글 **본문** 확인, Cloudflare 뒤 페이지 | [수동] 브라우저/skill |
| 5 | IOC 추출 → `data/ioc_registry.md` | [자동] 일부 등록 가능 / [수동] 검증·정리 |
| 6 | IOC 역피벗 → 새 IP → `pivot_queue.md` | [자동] `investigate_ioc.py` + [수동] 오탐 제거 |
| 7 | 클러스터 귀속·서술 → `data/campaigns.md`, `investigations/INDEX.md` | [수동] |
| 8 | 방어 산출물 → `reports/*` | [자동] `generate_reports.py` |

### 2.3 데이터 환류 경로

```
seed_ips.md / pivot_queue.md
        → investigate_ip.py (DDG + 다중 사이트 스크래퍼)
        → investigations/{cluster1,unclassified}/*.md
        → investigate_ioc.py → pivot_queue.md (신규 IP)
        → ioc_registry.md / campaigns.md / INDEX.md
        → generate_reports.py → reports/blocklist_ip.txt
```

### 2.4 피해 사이트 스크래핑: 전부 얕게, 깊게는 신호(데이터)로

**원칙:** `data/spammed_sites.md`에 적힌 피해 사이트는 **가능한 한 모두** 자동 조사 루프에 넣되, 처음부터 전 사이트에 **이자나 수준의 목록·본문 파싱**을 적용하지는 않는다. 깊이는 **1차로 모인 지표**를 보고 단계적으로 올린다.

#### 티어 정의 (권장)

| 티어 | 대상 | 자동화 수단 | 산출(데이터) |
|------|------|-------------|----------------|
| **1 · 얕음** | 표에 등록된 **모든** `ddg_site` 도메인 (+ 필요 시 이자나에 대해서도 동일한 DDG `site:`) | `site:도메인 "{IP}"` DDG 검색 | 도메인별 **검색 건수**, 스니펫 내 **사기 키워드** 여부, URL 후보 |
| **2 · 중간** | 티어 1에서 **검색결과>0** 이거나 스니펫에 `FRAUD_KEYWORDS`가 잡힌 도메인 | 브라우저로 상위 URL 열람, 또는 향후 “첫 결과 URL만 GET” 같은 **경량 페치** (사이트별 모듈 추가 시) | 본문·메타에 IOC/닉네임/연락처, (노출 시) 작성자 정보 |
| **3 · 깊음** | (a) 티어 2에서 악성 스팸 확정, (b) **작성자 IP가 HTML에 구조적으로 박힌** 사이트로 문서화된 경우 | 전용 스크래퍼: 목록 페이지 순회 + 글 단위 `read` URL (현재 구현 예: `izanaholdings.py`) | 작성자 IP·동일 행위자 피벗용 IOC |

**심화(티어 2→3) 트리거 예시 — 표로 쌓인 뒤 사람이 판단해도 되고, 나중에 규칙으로 자동화해도 된다.**

- 같은 IP에 대해 **서로 다른 피해 도메인에서 티어 1 히트가 2개 이상**이다.
- 티어 1 스니펫에 **선불유심·내구제·급전** 등이 같이 보인다.
- `STATUS.md` / 수동 큐에서 해당 IP·도메인 쌍을 **우선 조사**로 표시했다.
- 해당 사이트 행에 **전용 스크래퍼 유형**이 추가됐다 (`spammed_sites.md` 스크래퍼 컬럼).

**역설계 금지:** “이자나만 깊게 했으니 다른 곳은 없다”가 아니라, **티어 1이 전 도메인을 돌았는지**를 먼저 본다. 깊은 결론(DONE/직접 게시)은 티어 3까지 갔을 때만 단정한다.

#### 구현 매핑 (현재 저장소)

- **티어 1:** `investigate_ip.py` → `scrape_spam_sites_keywords_via_ddg` — 기본값으로 **`ddg_site` 도메인 전부** 순회 (상한은 `--ddg-site-limit N`으로만).
- **티어 1 산출물:** 매 실행마다 `data/tier1_logs/YYYY-MM-DD_{IP}.json`에 도메인별 히트 수·스니펫 키워드·샘플 URL·**`tier2_default`**(당시 기본 트리거 기준 티어2 후보 여부·메타)를 저장 (`schema_version` 필드, `--no-tier1-json`으로 끔). `*.json`은 `.gitignore`, `data/tier1_logs/.gitkeep`으로 디렉터리만 추적.
- **집계:** `python scripts/export_tier1_logs.py -o 원하는.csv` 로 JSON 전부를 도메인 단위 CSV로 합침(`source_json` 열). `--stats` 로 도메인별 “히트가 난 고유 IP 수” 요약(stderr). `--tier2-columns` 로 티어2 열 추가: JSON의 `tier2_default`와 `suggest_tier2_from_tier1_logs`가 같은 규칙으로 임베드 우선·불충분 시 재계산; `--tier2-force-recompute` 로 임베드 무시. `--tier2-min-hit-domains` / `--tier2-fraud-single` 는 재계산 시에만 적용. `per_domain`이 비어 있어도 스캔 단위로 **`domain=_scan_` 행 한 줄**을 넣어 티어2 열만이라도 남김 (`--no-scan-summary-row`로 끔).
- **큐 유지보수:** `python scripts/report_tier2_queue_stale.py [--days N]` 로 `tier2_queue.md`에서 추가일이 오래된 행을 목록화.
- **큐 정렬:** `python scripts/sort_tier2_queue.py` 로 `tier2_queue.md` 데이터 행을 **우선순위 내림차순**으로 재배치.
- **티어 2 큐:** DDG 히트 도메인 수 ≥ `--tier2-min-hit-domains`(기본 2)이거나, `--tier2-fraud-single` 사용 시 **단일 도메인+스니펫 사기 키워드**면 `data/tier2_queue.md`에 후속 조사 한 줄 자동 추가 (`--no-tier2-queue`로 끔). 같은 IP·같은 날 중복 행은 생략. 표에 **우선순위**(1–10)·**권장 조치**(샘플 URL 또는 DDG 힌트)가 채워진다.
- **소급 적용:** `python scripts/suggest_tier2_from_tier1_logs.py` 로 기존 `tier1_logs/*.json`만으로 후보를 stdout에 나열하고, `--apply`로 큐에 반영. JSON 경로를 인자로 주면 해당 파일만 처리(`export_tier1_logs`와 동일 패턴).
- **티어 3 (이자나만):** `scrape_izanaholdings` — DDG 게시판 검색 후, 기본 **목록 최대 15페이지**까지 순회. 목록을 끄려면 `--izana-list-pages 0`(검색만).
- **티어 2** 본문 확인은 대부분 **수동(브라우저)**. 자동 페치를 넣을 때는 사이트마다 파서·로봇 정책을 따른다.

### 2.5 왜 izanaholdings에 전용(깊은) 스크래퍼가 있는가

- **작성자 IP가 게시글 메타에 노출**되는 것이 확인되어, 티어 3 자동화의 **대표 사례**로 두었다 (`data/spammed_sites.md`).
- 다른 행은 구조가 제각각이라 **전부 티어 3 전용 모듈**을 두지 않고, 우선 **티어 1 DDG**로 동일하게 커버한다. 텔레그램 등은 스니펫에서 자동 추출하지 않는다 (노이즈 방지).
- 새 사이트에서도 HTML에 작성자 IP가 안정적으로 잡히면 `scripts/scrapers/`에 모듈을 추가하고, 표 스크래퍼 컬럼에 유형을 적는다.

### 2.6 전체 루프 (개념도)

```
[Seed IP]
    │
    ▼
[1] 검색: "IP주소"  [자동: investigate_ip.py / 수동: Google]
    │
    ▼
[2] 게시글·스니펫에서 IOC 추출
    │
    ├──────────────────┐
    ▼                  ▼
[3a] ioc_registry     [3b] pivot_queue (새 IP)
    │                  │
    └────────┬─────────┘
             ▼
[4] IOC 재검색 → [2]로 (역피벗)
             │
             ▼
[5] campaigns.md 클러스터 등록  [수동]
```

---

## 3. 검색 쿼리 패턴

### IP 주소 검색
```
"[IP주소]"
"[IP주소]" 내구제 OR 유심 OR 기프티콘 OR 텔레그램
```

### 텔레그램 핸들 검색
```
"@[핸들명]"
"@[핸들명]" 선불유심 OR 내구제 OR 급전
```

### 닉네임 검색
```
"[닉네임]" 선불유심 OR 내구제
site:izanaholdings.com "[닉네임]"
```

### 브랜드명 검색
```
"[브랜드명]" 텔레그램 OR 선불유심
```

---

## 4. 게시글 유형 분류 체계 (Taxonomy)

| 코드 | 유형 | 설명 | 키워드 예시 |
|---|---|---|---|
| `USIM` | 선불유심내구제 | 선불 유심을 이용한 내구제 대출 | 선불유심, 내구제, 유심내구제 |
| `LOAN` | 소액대출/급전 | 소액 긴급 자금 대출 유도 | 급전, 소액대출, 비상금, 당일지급 |
| `BUY_USIM` | 유심매입 | 개통된 선불유심 매입 | 유심매입, 유심삽니다, 유심팝니다 |
| `ACCOUNT` | 계정매매 | SNS/포털 계정 매매 | 네이버아이디, 카카오아이디, 계정구매 |
| `POINT` | 포인트현금화 | 포인트/기프티콘 현금화 | 포인트현금화, 기프티콘현금화 |
| `GIFT` | 기프티콘거래 | 기프티콘 매입/매매 | 기프티콘, 상품권, 쿠폰 |
| `TG_LEAD` | 텔레그램유도 | 텔레그램으로 연결 유도 | 텔레그램, 탬, 텔 |
| `DRUG` | 약물/마약 | 마약류 거래 유도 | 엑스터시, 필로폰, 대마 |
| `SPAM_OTHER` | 기타 스팸 | 위 분류에 속하지 않는 스팸 | - |

---

## 5. IP 인프라 유형 분류

| 유형 | 특징 | 대표 대역 | 의미 |
|---|---|---|---|
| **KR_RESIDENTIAL** | 국내 ISP 고정회선 | 221.143.x.x (SK Broadband) | 실제 사람 직접 사용 또는 감염 단말 |
| **KR_MOBILE** | 국내 모바일 | 39.x.x.x, 223.x.x.x 등 | 모바일 기기에서 직접 접근 |
| **VPS_GLOBAL** | 해외 VPS/클라우드 | 141.164.x.x, 158.247.x.x (Vultr) | 자동화 공격 인프라 가능성 높음 |
| **PROXY** | 프록시/VPN | 다양 | 실제 위치 은닉 |

---

## 6. 신뢰도 등급 (Confidence)

| 등급 | 기준 |
|---|---|
| `HIGH` | 해당 IP로 직접 게시된 스팸 게시글 확인 + IOC 2개 이상 연결 |
| `MEDIUM` | 해당 IP로 직접 게시된 스팸 게시글 확인 (IOC 연결 1개 이하) |
| `LOW` | 다른 IOC를 통한 간접 연결만 확인됨 |
| `UNVERIFIED` | 아직 조사 전 |

---

## 7. 작업 레이어 구분 (Browser/Skill vs Python)

이 프로젝트는 조사 행위와 자동화 행위를 분리해서 운영한다.

### 브라우저/skill로 해야 하는 일

- Google/Naver 검색 결과 확인
- Cloudflare 등 방어 뒤에 있는 페이지 열람
- 게시글 본문, 작성자, 날짜, 링크, 첨부파일 직접 확인
- 스크린샷/PDF/본문 캡처 확보
- 검색엔진 스니펫과 실제 본문 차이 검증

### Python으로 해야 하는 일

- `data/`와 `investigations/` 문서의 통계 자동 집계
- IOC 중복 제거, 정규화, 정렬
- 링크 무결성 검사
- `reports/` 산출물 생성
- 반복 쿼리 결과를 후처리하는 보조 스크립트 작성

### 원칙

- **조사 자체는 브라우저 중심**
- **Python은 보조 자동화**
- **최종 판단은 Markdown 문서에 남긴다**

Python crawler를 먼저 만드는 것보다, 브라우저로 몇 건의 수동 조사 패턴을 굳힌 뒤 공통 반복 작업만 스크립트화하는 것이 우선이다.

---

## 8. Cloudflare / 차단 대응 원칙

### 기본 순서

```
[1] 일반 검색엔진 결과 확인
    ↓
[2] 직접 HTTP 조회(curl/fetch) 시도
    ↓
[3] 차단되면 브라우저 세션으로 전환
    ↓
[4] 본문/스크린샷 확보
    ↓
[5] 그래도 실패하면 간접 증거만 기록하고 신뢰도 하향
```

### 운영 규칙

- `curl`이나 단순 fetch가 막혔다고 조사를 중단하지 않는다
- Cloudflare challenge가 걸리면 **브라우저 세션**으로 확인하는 것이 1순위다
- challenge를 통과한 뒤에는 가능한 한 같은 세션으로 관련 페이지를 연속 확인한다
- 직접 본문 확인이 안 되면 `직접 확인 실패`를 보고서에 명시한다
- 직접 본문 없이 검색 스니펫/메타데이터만 있는 경우, `LOW` 또는 `PARTIAL`에 머무는 것이 기본이다

### 증거 우선순위

1. **직접 본문 확인**: 게시글 원문, 작성자, 날짜, 노출 IP, 첨부파일
2. **검색엔진 스니펫**: 제목, 일부 본문, 캐시된 노출 흔적
3. **인프라 메타데이터**: whois, ASN, ipinfo, 도시/대역 일치
4. **간접 문서 참조**: 기존 보고서, 클러스터 문서, 타 IOC 연계

> 상위 증거가 없으면 하위 증거만으로는 귀속 신뢰도를 보수적으로 유지한다.

---

## 9. 보고서 작성 시 방어 우회/차단 상태 기록 규칙

- 본문을 직접 열람했으면 `게시판 스팸 활동` 표에 기록한다
- 본문을 못 열고 검색 스니펫만 확인했으면 `특이사항` 또는 표 비고에 그렇게 쓴다
- Cloudflare challenge로 실패했으면 `IP 기본 정보` 또는 `특이사항`에 적는다
- exact IP 검색 결과가 없으면 `직접 게시 미확인`이라고 명시한다
- 잠정 귀속이면 `Cluster#N 추정`, 정식 귀속이면 `Cluster#N`으로 쓴다

---

## 10. 공식 스키마 정의 (Data Schema)

> 모든 파일에서 아래 enum을 동일하게 사용한다. 임의 값 추가 금지.

### IP 조사 상태 (seed_ips.md, investigations/INDEX.md)

| 값 | 의미 |
|---|---|
| `UNVERIFIED` | 아직 조사 전 |
| `PARTIAL` | 일부 조사했으나 직접 게시 미확인 또는 추가 피벗 여지 있음 |
| `DONE` | 조사 완료 (직접 게시 확인 또는 FALSE_LINK 판정 완료) |

### IOC 피벗 상태 (ioc_registry.md)

| 값 | 의미 |
|---|---|
| `UNVERIFIED` | 수집됐지만 아직 이 IOC로 검색/조사 안 함 |
| `PARTIAL` | 일부 조사했지만 추가 피벗 여지 있음 |
| `DONE` | 이 IOC에 대한 조사 완료 |
| `FALSE_POSITIVE` | 무관한 것으로 판명 |

### 신뢰도 (investigations/*.md)

| 값 | 기준 |
|---|---|
| `HIGH` | 직접 게시 스팸 확인 + IOC 2개 이상 연결 |
| `MEDIUM` | 직접 게시 스팸 확인 (IOC 연결 1개 이하) |
| `LOW` | 간접 연결만 확인 (인프라 메타데이터, 서브넷 근접) |
| `UNVERIFIED` | 아직 조사 전 |

### 인프라 유형 (seed_ips.md, investigations/*.md)

| 값 | 대표 대역 | 의미 |
|---|---|---|
| `KR_RESIDENTIAL` | 221.143.x.x (SK Broadband 등) | 국내 고정회선 |
| `KR_MOBILE` | 39.x.x.x, 223.x.x.x 등 | 국내 모바일 |
| `VPS_GLOBAL` | 141.164.x.x, 158.247.x.x (Vultr 등) | 해외 VPS/클라우드 |
| `PROXY` | 다양 | 프록시/VPN |

### 클러스터 귀속 기준

- **정식 귀속** (`Cluster#N`): IOC 2개 이상 공유 OR 동일 /24 서브넷 + IOC 1개 이상 공유
- **추정 귀속** (`Cluster#N 추정`): 동일 /24 서브넷이지만 직접 IOC 연결 미확인
- **보수적 블록 원칙**: IP 범위 블록은 동일 서브넷 내 2개 이상 직접 확인 후 적용

---

## 11. 서브넷 배치 조사 원칙

대량 IP를 효율적으로 조사하기 위해 /24 서브넷 단위로 묶어서 접근한다.

### 절차

1. 동일 /24 서브넷에 속한 IP를 묶는다
2. 대표 IP 1~2개를 먼저 조사한다 (활동 흔적이 가장 많을 것으로 추정되는 것 우선)
3. 대표 IP 조사에서 클러스터 귀속이 확인되면, 같은 /24의 나머지 IP는 인프라 메타데이터만 확인 후 `Cluster#N 추정`으로 잠정 귀속
4. 직접 게시 흔적이 없는 IP는 `PARTIAL` 상태로 유지
5. 이후 여력이 되면 개별 IP 조사로 상태를 `DONE`으로 승격

### 서비스C VPS 적용 예시

141.164.x.x 대역 31개 IP의 경우:
- 각 /24 서브넷 별로 대표 IP 1개 선택 → 6~7회 조사로 전체 커버 가능
- VPS_GLOBAL 특성상 개별 IP보다 **공유 ASN/운영자** 파악이 더 중요

---

## 12. 블록리스트 출력 규칙

`reports/` 폴더에 아래 포맷으로 산출물을 생성한다.

### 포함 기준

| 산출물 | 포함 조건 |
|---|---|
| `blocklist_ip.txt` | 조사 상태 `DONE` + 신뢰도 `HIGH` 또는 `MEDIUM` |
| `ioc_telegram.txt` | 피벗 상태 `DONE` 또는 `PARTIAL` (+ 클러스터 귀속 확인) |
| `detection_keywords.txt` | 브랜드명, 핸들명, 서비스 키워드 (Cluster#1 이상 확인된 것) |

### 파일 포맷

```
# blocklist_ip.txt
# Generated: YYYY-MM-DD | Cluster#1 confirmed IPs
221.143.197.135
221.143.197.136
```

```
# ioc_telegram.txt
# Generated: YYYY-MM-DD
@brrsim_77    # 뽀로로통신 | Cluster#1 | DONE
@abab1768     # 곰돌이통신 | Cluster#1 | PARTIAL
```

---

## 14. 최종 산출물 목표

| 산출물 | 위치 | 설명 |
|---|---|---|
| IP 블록리스트 | `reports/blocklist_ip.txt` | 확인된 악성 IP 목록 |
| 텔레그램 IOC | `reports/ioc_telegram.txt` | 확인된 텔레그램 핸들 |
| 캠페인 클러스터 | `data/campaigns.md` | 연결된 IOC 묶음 |
| 피해 사이트 목록 | `data/spammed_sites.md` | 스팸 피해 사이트 |
| 탐지 키워드 | `reports/detection_keywords.txt` | 차단 룰용 키워드 |
| 서비스별 분석 | `reports/` | 서비스A/기프티콘/서비스C별 |
