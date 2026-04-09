# 캠페인/클러스터 정의 (Campaigns)

> 연결된 IOC 묶음을 캠페인 단위로 정의한다.
> 하나의 캠페인 = 동일 조직 또는 동일 인프라가 운영하는 것으로 추정되는 IOC 집합.

---

## Cluster #1 — 뽀로로/곰돌이/라부부 통신 네트워크

**상태:** 🔴 활성 (Active)  
**신뢰도:** HIGH  
**최초 발견:** 2026-04-06  
**마지막 업데이트:** 2026-04-09  

### 개요
서비스A/기프티콘 차단 요청에서 처음 드러난 선불유심내구제/소액대출 스팸 + ATO 네트워크.
초기 seed는 대구 SK Broadband `221.143.197.x` 대역이었고, 2026-04-07 izanaholdings 직접 재검증으로
`kimyoojin18`, `@brrsim_77`, `brrsim77.isweb.co.kr`를 공유하는 KT/SK Broadband 주거용 IP 5개가 추가 확인됐다.

### 연결된 IP

| IP | ISP | 유형 | 발견 맥락 |
|---|---|---|---|
| 221.143.197.136 | SK Broadband (대구) | KR_RESIDENTIAL | 서비스A seed |
| 221.143.197.135 | SK Broadband (대구) | KR_RESIDENTIAL | 서비스A, 기프티콘 seed |
| 221.143.197.13 | SK Broadband (대구) | KR_RESIDENTIAL (추정) | 서비스A seed, 직접 게시 미확인 |
| 220.123.216.40 | Korea Telecom (대전) | KR_RESIDENTIAL | izanaholdings 직접 피벗 |
| 218.49.179.79 | SK Broadband (서울) | KR_RESIDENTIAL | izanaholdings 직접 피벗 |
| 125.132.9.140 | Korea Telecom (서울) | KR_RESIDENTIAL | izanaholdings 직접 피벗 |
| 125.132.9.136 | Korea Telecom (서울) | KR_RESIDENTIAL | izanaholdings 직접 피벗 |
| 14.51.2.179 | Korea Telecom (대전) | KR_RESIDENTIAL | izanaholdings 직접 피벗 |

### 연결된 텔레그램

> 상세 피벗 상태 → [`data/ioc_registry.md` 텔레그램 섹션](ioc_registry.md)

| 핸들 | 브랜드 | 피벗 상태 | 활동 상태 |
|---|---|---|---|
| @brrsim_77 | 뽀로로통신 | DONE | 활성 |
| @abab1768 | 곰돌이통신 | PARTIAL | 활성 (사기 경고글 존재) |
| @the_usim | 라부부통신 | PARTIAL | 활성 |
| @krfa8 | - | UNVERIFIED | 약물 스팸 연관, 별도 클러스터 가능성 |
| @Upbitbo | - | UNVERIFIED | 계정매매 연관, 별도 클러스터 가능성 |

### 연결된 도메인

> 상세 피벗 상태 → [`data/ioc_registry.md` 도메인 섹션](ioc_registry.md)

| 도메인 | 용도 | 피벗 상태 |
|---|---|---|
| brrsim77.isweb.co.kr | 뽀로로통신 홍보 | PARTIAL |
| abab1768.isweb.co.kr | 곰돌이통신 홍보 | UNVERIFIED |
| abab1768abab1768.isweb.co.kr | 곰돌이통신 홍보 (변형) | UNVERIFIED |
| labubu.isweb.co.kr | 라부부통신 홍보 | UNVERIFIED |

### 연결된 닉네임

> 상세 피벗 상태 → [`data/ioc_registry.md` 닉네임 섹션](ioc_registry.md)

| 닉네임 | 사용 IP | 피벗 상태 |
|---|---|---|
| kimyoojin18 | 221.143.197.135, 221.143.197.136, 220.123.216.40, 218.49.179.79, 125.132.9.140, 125.132.9.136, 14.51.2.179 | PARTIAL |
| 라부부 | 221.143.197.136 | UNVERIFIED |

### 주요 활동 유형

- 선불유심내구제 (USIM) ★★★★★
- 소액대출/급전 (LOAN) ★★★★☆
- 유심매입/매매 (BUY_USIM) ★★★☆☆
- 텔레그램 유도 (TG_LEAD) ★★★★★
- 게시판 스팸 (20개 이상 사이트 확인)

### 피해 사이트 (일부)

izanaholdings.com, gjw.or.kr, channelpnu.pusan.ac.kr, 사랑나누미.com,  
haccpkoreamall.com, hs.ac.kr, bonghwanews.com, dancecode.kr, www.matcl.com 외 다수

→ 전체 목록: `data/spammed_sites.md`

### 추정 운영 모델

```
[유출 계정 확보] → credential stuffing → 서비스A/기프티콘 계정 탈취
        ↓
[탈취 자산 현금화] → 포인트/기프티콘 → 현금
        ↓
[선불유심 내구제] → 현금 필요한 사람 대상 스팸 광고
        ↓
[대포 통신] → 유심 매매 → 추적 회피용 통신 수단 제공
```

### 미확인 사항 (추가 조사 필요)

- [ ] 221.143.197.13 직접 게시 증거 확보 (2026-04-09: exact + **공지 보드 list 35p·read 작성자 IP 완전 일치**까지 0건; 과거/타 보드는 미점검)
- [x] @abab1768 / @the_usim 교차 피해 사이트: **2026-04-09** 공개 색인 기준 `www.matcl.com` 다수 스팸 스레드 확인 — **추가 작성자 IP 피벗은 미수**
- [ ] kimyoojin18 / @brrsim_77의 추가 residential IP가 다른 피해 사이트에도 반복 등장하는지 교차 확인 (2026-04-09 DDG 샘플: `220.123.216.40` 단독, `218.49.179.79`·`125.132.9.140`·`14.51.2.179` 결합 검색에서도 **색인 스니펫에 해당 IPv4 미등장** — 교차 게시 **미발견**으로 기록, 스크립트 `ddg_site` 일괄은 여전히 권장)
- [ ] 달림폰 브랜드와의 연결 확인

---

## Cluster #2 — 서비스C VPS 네트워크 (미분석)

**상태:** 🟡 조사 필요  
**신뢰도:** UNVERIFIED  
**최초 발견:** 2026-04-06 (seed 데이터에서 확인)

### 개요
서비스C 차단 요청 IP가 대부분 Vultr 클라우드 VPS 대역(141.164.x.x, 158.247.x.x, 64.176.x.x)으로 구성.
Cluster#1(국내 고정회선)과 성격이 완전히 다름 → 자동화 공격 인프라 추정.

### IP 대역 (미조사)
- 141.164.x.x — Vultr (13개 IP)
- 158.247.x.x — Vultr (14개 IP)
- 64.176.x.x — Vultr (2개 IP)
- 211.255.155.246 — 미확인 (1개)

→ 전체 목록: `data/seed_ips.md` 서비스C 섹션
