# 현재 진행 상태 (Status)

> **이 파일은 다음 LLM 에이전트가 작업을 이어받기 위한 인수인계 문서다.**  
> 작업 시작 전 반드시 이 파일부터 읽어라.

---

## 마지막 업데이트

- **날짜:** 2026-04-09 (추가 업데이트)
- **작업자:** Cursor Agent (Browser Automation 포함), 이전 라운드 이어받음
- **도구 환경:** Browser Automation MCP + 로컬 스크립트 + 파일 편집

---

## 현재까지 완료된 작업

### ✅ 프로젝트 기반 구조 수립
- README.md, METHODOLOGY.md, STATUS.md 작성
- 디렉토리 구조 생성 (data/, investigations/, reports/)
- seed IP 목록 정규화 → `data/seed_ips.md`
- IOC 레지스트리 초기화 → `data/ioc_registry.md`

### ✅ 221.143.197.136 조사 완료
- AbuseIPDB 조회: SK Broadband 대구 고정회선, 미등록
- Google 검색으로 게시판 스팸 흔적 17개 이상 확인
- 인접 IP 221.143.197.135 동일 행위자 확인
- 상세 보고서: `investigations/cluster1/221.143.197.136.md`

### ✅ 221.143.197.13 1차 조사 완료
- exact IP 검색, `내구제` 결합 검색, `site:izanaholdings.com` 검색 수행
- 공개 인덱스 기준 직접 게시 흔적은 미확인
- APNIC whois + ipinfo 기준 `221.143.197.136`과 동일 ASN/도시/`221.143.197.0/24` 확인
- 잠정 보고서: `investigations/cluster1/221.143.197.13.md`

### ✅ kimyoojin18 / @brrsim_77 외부 게시 흔적 추가 확보
- `bizk.co.kr`에서 `kimyoojin18` 작성자명, `@brrsim_77`, `brrsim77.isweb.co.kr` 동시 확인
- `higoodday.com`, `trost.co.kr`에서도 `@brrsim_77` 반복 게시 흔적 확인

### ✅ izanaholdings 직접 재검증으로 추가 IP 5개 확보
- 목록 페이지 직접 순회 후 `read.htm?board_code=board&idx=...` 본문 열람으로 작성자 IP 재수집
- 새로 확인된 IP: `220.123.216.40`, `218.49.179.79`, `125.132.9.140`, `125.132.9.136`, `14.51.2.179`
- 공통 근거: `kimyoojin18`, `@brrsim_77`, `brrsim77.isweb.co.kr` 동시 확인
- 보고서 생성: `investigations/cluster1/` 아래 5건 추가

### ✅ 2026-04-09 OSINT 라운드 (최우선 큐 소화)
- `221.143.197.13`: `curl -k` exact 검색 재확인 + **`list.htm` 35페이지·`read.htm` 작성자 IP 완전 일치** 순회 → **게시 0건** → **PARTIAL 유지.** `izanaholdings` 스크래퍼는 IP 부분문자열 오탐(`.13` ⊂ `.130` 등) 제거
- `@abab1768` / `@the_usim`: 공개 색인에서 `www.matcl.com`(맛클) 스팸 스레드 다수·`labubu.isweb.co.kr` 교차 언급 → `data/spammed_sites.md`, `data/ioc_registry.md`, `data/campaigns.md` 반영
- **5차(동일일):** `221.143.197.13` — izana `board` 목록 **36–59p** 추가 순회 0건; **60p·`board1`**은 타임아웃으로 미확정. `izanaholdings` 스크래퍼에 `board_code`·`list_page_range`·`idx>=1`·`fetch` 타임아웃 30s. `@abab1768` `investigate_ioc.py` → DDG에서 IPv4 후보 0건
- 5개 피벗 IP: DDG 샘플(`220.123.216.40` 등) 기준 **izanaholdings 외 즉시 인용 가능한 히트 없음** → `campaigns.md` 미확인 항목에 기록

### ✅ 티어 1 로그·티어 2 큐·CSV 집계 (2026-04-09)
- `investigate_ip.py`가 `data/tier1_logs/*.json` 저장(`schema_version`, `tier2_default` 포함), 조건 충족 시 `data/tier2_queue.md` 자동 한 줄 추가; 티어2 판정은 `compute_tier2_followup_row` **1회** 결과를 JSON·큐에 공유 (`METHODOLOGY.md` §2.4, CLI 플래그 참고)
- `data/tier2_queue.md`: **우선순위·권장 조치** 열 추가, `utils.compute_tier2_followup_row`로 행 생성
- `scripts/export_tier1_logs.py`: 로그 JSON → 도메인 단위 CSV, `--stats`로 도메인별 고유 IP 히트 요약
- `scripts/suggest_tier2_from_tier1_logs.py`: 과거 tier1 JSON만으로 티어2 후보 나열 / `--apply`로 큐 반영; stderr에 임베드·재계산 건수 요약
- `export_tier1_logs.py --tier2-columns`: CSV에 티어2 후보·우선순위·권장 요약 열 병합; `per_domain` 없을 때 `_scan_` 요약 행. `sort_tier2_queue.py`: 큐 우선순위 정렬. `report_tier2_queue_stale.py`: 오래된 큐 행 나열

### ✅ 전체 64개 IP 1차 배치 조사 완료 (다른 에이전트)
- **기프티콘 25개 IP** 전부 DDG 조사 완료 → `investigations/unclassified/` 아래 PARTIAL 보고서 생성
- **서비스C 31개 IP** (Vultr 141.164.x.x / 158.247.x.x / 64.176.x.x) 전부 DDG 조사 → PARTIAL 보고서 생성, IOC 없음 (자동화 인프라로 추정)
- **서비스A 나머지 5개** (218.236.231.x, 121.170.203.142, 125.141.26.12) 조사 → PARTIAL
- **121.159.134.27** 조사: `kimyoojin18` + `@brrsim_77` 동시 확인 → **Cluster#1 추정**, 신규 IOC @0450 · @df8d3400wef50681bp68ad6cf7m44c53 발견 (검증 필요)
- INDEX.md 전수 업데이트 완료, 진행률 수치는 DONE 기준 유지

### ✅ 불확실 항목 재검증 및 자동화 보수화
- `221.143.197.13`은 2026-04-07 재검증에서도 직접 게시 미확인 → `PARTIAL` 유지
- 다른 에이전트가 제시한 `121.159.134.27`은 exact 검색 기준 직접 게시 재현 실패 → 현재 저장소 반영 보류
- `scripts/investigate_ip.py`를 실제 `board_code=board` 구조에 맞게 수정
- DuckDuckGo 스니펫의 텔레그램/도메인 자동 IOC 등록을 중단해 노이즈 유입 방지

---

## 조사 진행률

| 서비스 | 전체 | DONE | PARTIAL | UNVERIFIED | 진행률(1차 조사) |
|---|---|---|---|---|---|
| 서비스A | 8 | 2 | 6 | 0 | 100% |
| 기프티콘 | 25 | 1 | 24 | 0 | 100% |
| 서비스C | 31 | 0 | 31 | 0 | 100% |
| **합계** | **64** | **3** | **61** | **0** | **100%** |

> UNVERIFIED → 0: 64개 전수 1차 조사 완료(보고서 PARTIAL). DONE = izanaholdings 본문 직접 확인 또는 복수 공신뢰 출처.
> ISP/인프라 정보 일괄 반영 완료(2026-04-09): KR_RESIDENTIAL(SK/KT/LG/abcle/HyosungITX), VPS_GLOBAL(Vultr AS20473).

→ 전체 인덱스: `investigations/INDEX.md`

---

## 현재 식별된 클러스터

### Cluster #1 — 뽀로로/곰돌이/라부부 통신 네트워크
- **상태:** 활성 (2025-12 ~ 2026-04)
- **핵심 인프라:** `221.143.197.x` seed 대역 + KT/SK Broadband residential 추가 IP 5개
- **핵심 IOC:** @brrsim_77, @abab1768, @the_usim, kimyoojin18
- **상세:** `data/campaigns.md` 참조

---

## 다음에 해야 할 작업 (Priority Queue)

### 🔴 최우선 (즉시 실행)

1. **abab1768.isweb.co.kr / brrsim77.isweb.co.kr 직접 조회** ✅ *2026-04-09 확인*
   - 결과: **두 사이트 모두 현재 다운** (invalid response). 접근 불가.
   - `abab1768abab1768.isweb.co.kr` 도 동일 다운 상태.

2. **matcl.com 스레드 본문 확인** ✅ *2026-04-09 브라우저 직접 확인 완료*
   - 결과: `@abab1768` 자유·팁 게시판 다수 게시 확인. `http://www.matcl.com/freeboard/11429543` (2026-04-08)
   - **matcl.com 작성자 IP 미노출** → IP 피벗 불가. 홍보 URL `abab1768abab1768.isweb.co.kr` 현재 다운.
   - `@the_usim` 자유게시판 스팸 게시 확인. IP 노출 없음.
   - ioc_registry.md 반영 완료.

3. **121.159.134.27 신규 IOC 검증** ✅ *2026-04-09 브라우저 확인 완료*
   - `@0450`: t.me → telegram.org 리다이렉트 → **FALSE_POSITIVE**
   - `@df8d3400wef50681bp68ad6cf7m44c53`: **실존하는 Telegram 개인 계정** (DM형, 봇 가능성)
   - `investigations/cluster1/121.159.134.27.md` 업데이트 완료

4. **221.143.197.13 직접 게시 증거** ✅ *2026-04-09 브라우저 전수 완료*
   - **board(공지사항) 1~79p 전수 + board1(보도자료) → 0건 확정**
   - board는 2026-01-10~현재, 79페이지 전부 pp/aa/카지노 스패머. kimyoojin18 없음.
   - board1은 2018년 관리자 글 3건(보도자료). 해당 없음.
   - **결론: 221.143.197.13은 izanaholdings에서 활동 이력 없음. PARTIAL 유지** (동일 /24 서브넷·서비스A seed 근거로 Cluster#1 추정이나 직접 게시 증거 없음).

### 🟡 중요 (이후 실행)

5. **서비스C Vultr IP 클러스터 성격 파악** ✅ *2026-04-09 브라우저 확인 완료*
   - `141.164.36.87` Google 검색: hanyaksale.com(한약판매) 게시글에 이 IP가 **작성자 IP로 노출**
   - 게시 내용: **불법 의약품 스팸** (졸피뎀/물뽕/핀페시아/리시노프릴), 연관 핸들 `@YY77882`
   - **Cluster#1(내구제/유심)과 완전히 다른 행위자** → Cluster#2 후보 (불법 의약품 자동화 인프라)
   - hanyaksale.com 현재 중단(카페24). ioc_registry에 @YY77882 등록.
   - ✅ `158.247.239.223` 확인: **동일 패턴 확정** (tokiya.com, kimchischool.com, delishop2018.co.kr, hoyaondol.com 등에서 @YY77882 불법 의약품/독극물 스팸). 두 대역 모두 Cluster#2 = @YY77882 인프라.

6. **기프티콘 IP 후속 처리** ✅ *2026-04-09 완료*
   - Google/DDG 재확인: 대부분 의미 있는 IOC 없음. 모두 KR_RESIDENTIAL(SK/KT/LG/abcle/HyosungITX)
   - `abcle(AS38661)` 6개 · `HyosungITX(AS38690)` 5개 IP 집중 — 동일 ISP군 주목
   - ioc_registry의 @zzzdodo 등 '자동 등록' 핸들은 연관 약함 → UNVERIFIED 유지

### 🟢 배치 작업

7. **PARTIAL 보고서 ISP/인프라 정보** ✅ *2026-04-09 완료*
   - 28개 KR 거주형 보고서 + 29개 Vultr VPS 보고서 일괄 업데이트
   - seed_ips.md UNVERIFIED→PARTIAL 59개 반영

8. **generate_reports.py 재실행** ✅ *2026-04-09 완료*
   - blocklist 7개 IP, ioc_telegram 5개, summary.md 갱신
   - 전수 진행률 **100%(1차 조사)** 반영

---

## 작업 방법 (다음 에이전트용)

**공통:** 로컬에서는 `python scripts/investigate_ip.py <IP>` 또는 `python scripts/run_investigate_pipeline.py <IP>`(조사→CSV→suggest)로 티어1·초안 보고서·티어2 큐까지 돌릴 수 있다. `ddgs` 패키지는 venv 권장([OPS.md](OPS.md) 명령 참고). 아래 Chrome MCP는 **해당 MCP가 연결된 에이전트/환경에서만** 적용된다.

### Google 검색 방법 (Chrome MCP 사용 가능할 때)
Claude in Chrome 확장이 연결된 상태에서:
```
1. mcp__Claude_in_Chrome__tabs_context_mcp 으로 탭 확인
2. mcp__Claude_in_Chrome__navigate 로 Google 검색 URL 이동
3. mcp__Claude_in_Chrome__get_page_text 로 결과 텍스트 추출
4. 텍스트에서 IOC 파싱
```

### izanaholdings 직접 검증 방법
```
1. /bbs_shop/list.htm?board_code=board&page=N 에서 최근 게시글 idx 수집
2. /bbs_shop/read.htm?board_code=board&idx=...&cate_sub_idx=0 본문 열람
3. 작성자 줄의 마지막 <span> 값을 실제 작성자 IP로 기록
4. /bbs/board exact 검색 결과는 false negative가 있을 수 있으므로 단독 근거로 쓰지 않음
```

### 결과 저장 방법
```
1. 개별 IP 조사 보고서
   - 클러스터 확인된 경우: investigations/cluster[N]/[IP주소].md
   - 미분류: investigations/unclassified/[IP주소].md
   - 템플릿: investigations/TEMPLATE.md 복사 후 작성
2. 새 IOC 발견 → data/ioc_registry.md 업데이트
3. 클러스터 연결 확인 → data/campaigns.md 업데이트
4. 조사 인덱스 → investigations/INDEX.md 상태/링크 업데이트
5. seed_ips.md → 조사 파일 컬럼 링크 추가
6. 이 파일(STATUS.md) 진행률 표 업데이트
```

---

## 주의사항

- Chrome 확장이 연결되어 있어야 Google 검색 가능 (WebFetch는 대부분 차단됨)
- 검색 시 항목당 20개 결과 (`&num=20`) 사용
- 서비스C IP(141.164.x.x, 158.247.x.x, 64.176.x.x)는 **Vultr VPS** 대역 — 성격이 다름
- izanaholdings.com은 스팸이 가장 많이 집중된 사이트 — IP 정보가 게시글 하단에 노출됨
- izanaholdings.com `/bbs/board` 검색 페이지는 false negative가 있으니 목록 순회가 우선
- AbuseIPDB와 일부 홍보 사이트(isweb)는 Cloudflare challenge가 걸려 직접 본문 확보가 제한될 수 있음

---

## 2026-04-09 저장소 보강 (에이전트)

- **문서:** [OPS.md](OPS.md), [RELATIONSHIPS.md](RELATIONSHIPS.md), [METHODOLOGY.md](METHODOLOGY.md) §2.4(티어1 로그·티어2 큐·CSV·소급 suggest), README 트리·빠른 시작.
- **스크립트:** `scripts/scrapers/` (izanaholdings + DDG `site:`), `investigate_ip.py`, **`run_investigate_pipeline.py`**, `export_tier1_logs.py`, `suggest_tier2_from_tier1_logs.py`, `sort_tier2_queue.py`, `report_tier2_queue_stale.py`, `investigate_ioc.py`, `stale_check.py`, `data/pivot_queue.md`, `generate_reports.py` 블록리스트 TTL·만료 주석.
- **INDEX:** `last_seen` / `last_verified` 컬럼, cluster#1 보고서에 lifecycle 필드 초기값.
- **제한적 OSINT:** [investigations/PHASE6_OSINT_NOTE_2026-04-09.md](investigations/PHASE6_OSINT_NOTE_2026-04-09.md) — 이번 라운드에서 `.13` curl 재확인·matcl·피벗 IP 샘플 반영. 브라우저·목록 순회는 여전히 최우선.
