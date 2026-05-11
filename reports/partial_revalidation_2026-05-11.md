# PARTIAL IP 재검증 노트 — 2026-05-11

## 요약

- `investigations/INDEX.md` 기준 `PARTIAL` IP 75개를 exact-IP 검색으로 재점검했다.
- `121.170.203.142`는 최근 스팸 평판(CleanTalk `last activity=2026-05-08`)과 같은 `/24`의 `121.170.203.144` 직접 IOC 때문에 follow-up 가치가 높다고 봤고, 이후 사용자 제공 `moonyetimes.com` 원문 3건에서 이 IP의 직접 게시 증거를 확인했다.
- 다만 확인된 직접 캠페인은 `@rnfma9`/USIM이 아니라 `puy24.com`, `hto78.com`, `kbb12.com`을 반복하는 성인약국/pharma 스팸이다.
- 직접 원문 후보로 의미 있었던 것은 `218.236.231.231`의 `dongponews.net` 검색 스니펫뿐이었으나, 원문은 삭제되어 `search_snippet_only`로 유지한다.
- 나머지 후보는 대부분 IP 평판/디렉터리/범위 조회 페이지였고, 작성자 IP 또는 본문 IOC 직접 증거로 승격할 수 없었다.

## 방법

| 항목 | 내용 |
|---|---|
| 대상 | `PARTIAL` IP 75개 |
| 검색 | DDG exact query `"IP"` with recent window (`timelimit='y'`), 상위 8건 |
| 직접 확인 | `121.170.203.142` dry-run, CleanTalk 원문, 사용자 제공 `moonyetimes.com` 원문 3건, `dongponews.net` 후보 원문, `121.170.203.144` 관련 XE 원문 grep |
| 배제 기준 | IP 평판/디렉터리, IP range 목록, CDN/페이지 자산 IP, 삭제되어 본문 확인 불가한 스니펫 |

## 집계

| 서비스 | PARTIAL 수 | exact 검색 결과 있음 | 원문 후보 있음 | 주의 |
|---|---:|---:|---:|---|
| svc_a | 6 | 3 | 1 | `218.236.231.231`은 삭제된 `dongponews` 스니펫만 확인 |
| gifticon | 24 | 11 | 0 | 직접 작성자 IP 후보 없음 |
| svc_c | 31 | 25 | 2 | `whoer.com`, `2ip.io` 등 generic IP/도메인 조회 오탐 |
| pivot | 14 | 12 | 3 | `121.170.203.144`는 이미 별도 직접 IOC, `speedguide.net`은 range 조회 오탐 |
| 합계 | 75 | 51 | 6 | 자동 exact 스캔만으로는 신규 승격 0. 사용자 제공 `moonyetimes.com` 보강으로 `121.170.203.142` 직접 pharma-spam 증거 확인 |

## 핵심 IP별 결과

| IP | 결과 | 판정 |
|---|---|---|
| `121.170.203.142` | DDG exact 결과는 AbuseIPDB/CleanTalk/CriminalIP/IP 디렉터리 중심. 사용자 제공 `moonyetimes.com` board1 `idx=15434`, `15554`, `16554` 원문에서 작성자 IP `121.170.203.142`와 `puy24.com`, `hto78.com`, `kbb12.com` 성인약국/pharma 스팸 직접 확인 | `PARTIAL/MEDIUM`으로 상향. 단, USIM/loan 후보와 동일 행위자 귀속은 보류 |
| `121.170.203.144` | 이미 `m.ebbysory.co.kr`에서 `@rnfma9` 작성자 IP 직접 확인. 추가로 `skmc.kr`, `hansung-tech.kr` XE 원문에서 2026년 일반 스팸성 작성 IP 흔적이 보이나 PointPivot 캠페인 직접 증거는 아님 | 별도 신규 USIM 후보 `PARTIAL/MEDIUM` 유지 |
| `218.236.231.231` | DDG recent exact 검색에서 `dongponews.net/bbs/view.html?idxno=75694`가 `가전제품내구제 텔레그램@brrsim_77 ... 선불유심내구...` 제목으로 노출. 직접 fetch는 `존재하지 않는 게시물입니다.`만 반환 | 삭제 스니펫 후보. `PARTIAL/LOW` 유지 |
| `141.164.48.3`, `141.164.60.85` | `whoer.com`, `2ip.io` 조회 페이지 | generic 오탐 |
| `118.235.6.158`, `118.235.15.248` | `speedguide.net/ip/118.235.x` range 조회 | generic 오탐 |

## 결론

`PARTIAL` 전수 재검증은 필요하다. 특히 Google/검색엔진 스니펫에는 삭제된 게시글의 핸들·작성자 IP가 남을 수 있어 `PARTIAL` 큐를 주기적으로 재확인해야 한다. 이번 보강으로 `121.170.203.142`는 직접 스팸 게시 증거가 확인됐지만, 증거 유형은 성인약국/pharma 스팸이다. `121.170.203.144`의 USIM/loan 후보와 동일 행위자로 귀속하지 않는다.
