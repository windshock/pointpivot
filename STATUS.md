# 현재 진행 상태 (Status)

> **이 파일은 다음 LLM 에이전트가 작업을 이어받기 위한 인수인계 문서다.**  
> 작업 시작 전 반드시 이 파일부터 읽어라.

---

## 마지막 업데이트

- **날짜:** 2026-04-07
- **작업자:** Codex (GPT-5), 이전 Claude 작업 이어받음
- **도구 환경:** 공개 HTTP 조회(curl) + ipinfo + 로컬 문서/스크립트 갱신

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

### ✅ 불확실 항목 재검증 및 자동화 보수화
- `221.143.197.13`은 2026-04-07 재검증에서도 직접 게시 미확인 → `PARTIAL` 유지
- 다른 에이전트가 제시한 `121.159.134.27`은 exact 검색 기준 직접 게시 재현 실패 → 현재 저장소 반영 보류
- `scripts/investigate_ip.py`를 실제 `board_code=board` 구조에 맞게 수정
- DuckDuckGo 스니펫의 텔레그램/도메인 자동 IOC 등록을 중단해 노이즈 유입 방지

---

## 조사 진행률

| 서비스 | 전체 | DONE | PARTIAL | UNVERIFIED | 진행률 |
|---|---|---|---|---|---|
| 서비스A | 8 | 2 | 1 | 5 | 38% |
| 서비스C | 31 | 0 | 0 | 31 | 0% |
| 기프티콘 | 25 | 1 | 0 | 24 | 4% |
| **합계** | **64** | **3** | **1** | **60** | **6%** |

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

1. **221.143.197.13 직접 게시 증거 확보**
   - exact IP 검색으로는 결과 없음
   - `site:izanaholdings.com "221.143.197.13"` 및 목록 페이지 수동 순회 재검증
   - 잠정 보고서를 직접 게시 증거 기반으로 `DONE` 또는 현 상태 유지 방향 정리

2. **@abab1768 / @the_usim 추가 IP 수집**
   - Cluster#1의 다른 브랜드에서 동일한 residential 확장 패턴이 있는지 확인
   - `izanaholdings.com`, `사랑나누미.com`, `haccpkoreamall.com` 중심으로 재탐색

3. **새로 확보한 5개 IP의 교차 피해 사이트 등장 여부 확인**
   - `220.123.216.40`, `218.49.179.79`, `125.132.9.140`, `125.132.9.136`, `14.51.2.179`
   - izanaholdings 외 다른 게시판에도 반복 등장하는지 확인

### 🟡 중요 (이후 실행)

4. **121.159.134.27 주장 재현 여부 확인**
   - 현재 저장소에는 반영하지 않았음
   - 다른 에이전트 산출물의 직접 게시 주장 재현 여부만 별도 확인

5. **141.164.x.x 대역 분석 (서비스C VPS)**
   - 이 대역은 Vultr 클라우드 IP → 자동화 공격 인프라 추정
   - 대표 IP 몇 개 샘플링해서 특성 파악
   - Google 검색: `"141.164.36.87"`, `"141.164.37.225"` 등

6. **abab1768.isweb.co.kr 사이트 직접 조회**
   - 곰돌이통신 홍보 사이트 내용 확인
   - 추가 연락처, 서비스 설명 등 IOC 수집

7. **brrsim77.isweb.co.kr 사이트 직접 조회**
   - 뽀로로통신 홍보 사이트 내용 확인

### 🟢 배치 작업 (자동화 필요)

8. **기프티콘 IP 25개 전체 순차 조사**
   - `data/seed_ips.md`의 기프티콘 섹션 참조
   - 각 IP를 Google 검색 → IOC 추출 → `data/ioc_registry.md` 업데이트

9. **서비스A IP 8개 중 미조사/부분조사 6개 + 1개 재검증**
   - `221.143.197.136` 제외 나머지 IP 조사
   - `221.143.197.13`은 직접 게시 여부 재검증 필요

---

## 작업 방법 (다음 에이전트용)

### Google 검색 방법
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
