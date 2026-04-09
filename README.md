# PointPivot

**국내 기프티콘·포인트 서비스를 노리는 사기 조직의 IP·텔레그램·사이트를 추적하는 공개 OSINT 인텔리전스 데이터베이스**

> 📺 배경 이해: [내 기프티콘이 사이버 무기로 쓰이는 이유](https://youtu.be/EyRPDV0QFZs) — 어떤 범죄인지 5분 영상으로 설명

---

## 무슨 프로젝트인가요?

카카오 기프티콘, 각종 포인트 서비스에서 **계정을 탈취해 현금화하는 조직**들이 있습니다.  
이 조직들은 한국 커뮤니티 게시판에 텔레그램 홍보 스팸을 도배하고, 선불 유심 거래로 자금을 세탁합니다.  
문제는 이 IP들이 **AbuseIPDB 같은 글로벌 차단 목록에 전혀 등록되어 있지 않다는 것**입니다.

PointPivot은 이 조직들의 흔적(IP 주소, 텔레그램 핸들, 스팸 사이트)을 직접 추적·정리하는 오픈소스 인텔리전스 데이터베이스입니다.

---

## 용도에 따라 바로 가기

| 저는 이런 사람입니다 | 여기로 가세요 |
|---------------------|---------------|
| 서비스 보안 담당자 — 차단 IP가 필요합니다 | **[`reports/blocklist_ip.txt`](reports/blocklist_ip.txt)** |
| 어떤 조직을 발견했는지 보고 싶습니다 | **[`data/campaigns.md`](data/campaigns.md)** |
| 현재 조사 진행 상황이 궁금합니다 | **[`reports/summary.md`](reports/summary.md)** |
| 특정 IP를 조회하고 싶습니다 | **[`investigations/INDEX.md`](investigations/INDEX.md)** |
| 텔레그램·도메인 IOC 목록이 필요합니다 | **[`data/ioc_registry.md`](data/ioc_registry.md)** |
| 조사에 기여하거나 이어서 진행하고 싶습니다 | **[`STATUS.md`](STATUS.md)** → [`OPS.md`](OPS.md) |

---

## 지금까지 발견한 것

### 🔴 Cluster #1 — "뽀로로통신/곰돌이통신/라부부통신" 네트워크

> 기프티콘·포인트 서비스를 해킹하고, 선불 유심 거래로 돈을 버는 국내 범죄 조직

**이 조직이 하는 일:**
- 유출된 계정 정보로 기프티콘·포인트 서비스에 자동 로그인 시도 (Credential Stuffing)
- 탈취한 포인트·기프티콘을 현금으로 전환
- 선불 유심을 사고팔아 추적 회피용 통신 수단 제공
- 20개 이상 한국 커뮤니티 게시판에 텔레그램 광고 스팸 도배

**확인된 흔적:**

| 항목 | 내용 |
|------|------|
| IP (확인 완료) | `221.143.197.135`, `221.143.197.136` (대구, SK Broadband) |
| IP (관련 의심) | `221.143.197.13`, `220.123.216.40`, `218.49.179.79` 등 6개 추가 |
| 텔레그램 | `@brrsim_77` (뽀로로통신), `@abab1768` (곰돌이통신), `@the_usim` (라부부통신) |
| 닉네임 | `kimyoojin18` |
| 활동 기간 | 2025년 12월 ~ 현재 |
| AbuseIPDB | **미등록** — 글로벌 차단 목록에 없음 |

→ 상세 보고서: [`data/campaigns.md`](data/campaigns.md) · [`investigations/cluster1/`](investigations/cluster1/)

---

### 🟡 Cluster #2 — 불법 의약품·독극물 판매 조직 (@YY77882)

> 한국 커뮤니티 사이트를 스팸으로 도배해 텔레그램으로 불법 약물을 판매하는 조직

**이 조직이 하는 일:**
- 해외 클라우드 서버(Vultr VPS)에서 자동화 봇을 돌려 한국 커뮤니티 게시판에 스팸 게시
- 졸피뎀, 물뽕(GHB), **펜토바르비탈(안락사 약물)**, **시안화칼륨(독극물)** 등 불법 판매

| 항목 | 내용 |
|------|------|
| IP 대역 | `141.164.x.x`, `158.247.x.x`, `64.176.x.x` (Vultr 해외 서버) 29개 |
| 텔레그램 | `@YY77882` |
| Cluster#1과의 관계 | **완전히 다른 조직** |

→ 상세: [`data/campaigns.md`](data/campaigns.md)

---

## 현재 조사 현황

| 항목 | 현황 |
|------|------|
| 추적 중인 IP | 64개 (전수 1차 조사 완료) |
| 차단 권고 IP | **7개** → [`reports/blocklist_ip.txt`](reports/blocklist_ip.txt) |
| 확인된 텔레그램 | 18개 → [`data/ioc_registry.md`](data/ioc_registry.md) |
| 피해 확인 사이트 | 21개 → [`data/spammed_sites.md`](data/spammed_sites.md) |

→ 자동 집계 전체: [`reports/summary.md`](reports/summary.md)

---

## 왜 글로벌 차단 목록만으로는 부족한가

AbuseIPDB, Spamhaus 같은 서비스는 **국내 게시판 스팸, 선불유심 거래, 포인트 탈취** 같은 한국 특화 범죄를 포착하지 못합니다. 위 조직들의 IP는 모두 글로벌 차단 목록에 **미등록** 상태입니다.

이 프로젝트는 한국 웹 검색 + 현장 게시글 확인 + 연쇄 피벗으로 글로벌 서비스가 놓치는 범죄 인프라를 직접 추적합니다.

---

## 관련 프로젝트

- **[anonymous-vps](https://github.com/windshock/anonymous-vps)** — 익명·크립토 친화 VPS 인벤토리. Cluster#2(Vultr VPS)와 교차 분석 가능.

---

<details>
<summary>📂 저장소 구조 (기여자·자동화 에이전트용)</summary>

```
pointpivot/
├── data/
│   ├── campaigns.md        ← 발견된 조직 상세
│   ├── ioc_registry.md     ← IOC (텔레그램·도메인) 목록
│   ├── seed_ips.md         ← 조사 대상 IP 원본
│   └── spammed_sites.md    ← 피해 사이트 목록
├── investigations/
│   ├── INDEX.md            ← IP 전체 조사 인덱스
│   ├── cluster1/           ← Cluster#1 확정 IP 보고서
│   └── unclassified/       ← 미분류 IP 초안 보고서
├── reports/
│   ├── blocklist_ip.txt    ← 차단 IP 목록 (자동 생성)
│   └── summary.md          ← 현황 요약 (자동 생성)
├── scripts/                ← 조사 자동화 스크립트
├── STATUS.md               ← 에이전트 인수인계 문서
├── METHODOLOGY.md          ← 조사 방법론
└── OPS.md                  ← 운영 플레이북
```

에이전트·기여자 진입점: [`STATUS.md`](STATUS.md) → [`OPS.md`](OPS.md) → [`METHODOLOGY.md`](METHODOLOGY.md)

</details>
