# IOC 레지스트리 (Indicator of Compromise Registry)

> 피벗 조사를 통해 수집된 모든 IOC를 등록한다.
> 새 IOC 발견 시 이 파일에 추가하고 status를 `UNVERIFIED`로 설정한다.
> 조사 완료 후 `DONE` 또는 `FALSE_POSITIVE`로 업데이트한다.
>
> **피벗 상태 enum:** `UNVERIFIED` | `PARTIAL` | `DONE` | `FALSE_POSITIVE`

---

## 텔레그램 핸들

| 핸들 | 브랜드명 | 최초 발견 IP | 발견 날짜 | 피벗 상태 | 클러스터 | 비고 |
|---|---|---|---|---|---|---|
| @brrsim_77 | 뽀로로통신 | 221.143.197.135/136 | 2026-04-06 | DONE | Cluster#1 | 가장 활발. 기존 피해 사이트 외 bizk.co.kr, higoodday.com, trost.co.kr에서도 반복 게시 확인 |
| @abab1768 | 곰돌이통신 | 221.143.197.136 | 2026-04-06 | PARTIAL | Cluster#1 | 사기꾼 경고글 존재. 2026-04-09 브라우저 직접 확인: matcl.com 자유게시판·팁게시판에 다수 게시. 대표 URL `http://www.matcl.com/freeboard/11429543` (2026-04-08). matcl.com은 작성자 IP 노출 없음 → IP 피벗 불가. 홍보 URL: `abab1768abab1768.isweb.co.kr` (현재 다운). |
| @the_usim | 라부부통신 | 221.143.197.136 | 2026-04-06 | PARTIAL | Cluster#1 | 2026-04-09 공개 색인: `www.matcl.com`에서 라부부통신·`labubu.isweb.co.kr` 홍보 스레드 흔적. 브라우저 확인: 자유게시판에 `the_usim` 스팸 게시 확인. matcl.com 작성자 IP 노출 없음. |
| @krfa8 | - | 221.143.197.136 | 2026-04-06 | UNVERIFIED | - | 약물(엑스터시) 관련 스팸 |
| @Upbitbo | - | 221.143.197.136 | 2026-04-06 | UNVERIFIED | - | 네이버 아이디 매매 관련 |
| @zzzdodo | - | 223.26.145.161 | 2026-04-06 | UNVERIFIED | - | 자동 등록 |
| @idu | - | 218.36.50.230 | 2026-04-06 | UNVERIFIED | - | 자동 등록 |
| @iebc | - | 211.254.20.124 | 2026-04-06 | UNVERIFIED | - | 자동 등록 |
| @SOCKS5 | - | 211.36.152.160 | 2026-04-06 | UNVERIFIED | - | 자동 등록 |
| @awsomesauce27 | - | 141.164.56.216 | 2026-04-06 | UNVERIFIED | - | 자동 등록 |
| @elfin_usim | - | 221.143.197.136 | 2026-04-06 | UNVERIFIED | - | 자동 등록 |
| @TPhantom202 | - | 158.247.202.252 | 2026-04-06 | UNVERIFIED | - | 자동 등록 |
| @adgprentiss | - | 158.247.210.130 | 2026-04-06 | UNVERIFIED | - | 자동 등록 |
| @ezcash | - | 158.247.225.193 | 2026-04-06 | UNVERIFIED | - | 자동 등록 |
| @0450 | - | 121.159.134.27 | 2026-04-06 | FALSE_POSITIVE | - | t.me/0450 → telegram.org 리다이렉트. 존재하지 않는 핸들. |
| @df8d3400wef50681bp68ad6cf7m44c53 | - | 121.159.134.27 | 2026-04-06 | PARTIAL | Cluster#1 추정 | 실존 Telegram 개인 계정. 봇/스팸 가능성. 2026-04-09 브라우저 확인. |
| @pazard | - | 122.99.176.197 | 2026-04-06 | UNVERIFIED | - | DDG 검색 결과에서 발견 |
| @YY77882 | - | 141.164.36.87, 158.247.239.223 | 2026-04-09 | PARTIAL | Cluster#2 후보 | 불법 의약품/독극물 스팸. 졸피뎀·물뽕·펜토바르비탈·시안화칼륨 등. Cluster#1과 무관. |
| @GO174 | - | 118.235.25.44 | 2026-04-13 | DONE | Cluster#3 | 먹튀/도박/통장협박/계좌매입 대규모 스팸. outoftrunk.com 등 다수 카페24 사이트. @Muo52S와 동일 인프라 공유. |
| @Muo52S | - | 118.235.2.186, 118.235.12.181 | 2026-04-29 | DONE | Cluster#3 | 스포츠픽, 파워볼유출, 밸런스작업, 문서위조 광고. @GO174와 동일 인프라 공유. |
| @holysim | holysim | - | 2026-05-11 | PARTIAL | 신규 후보(USIM/loan) | 행위 키워드 신규 발굴. `tvo.kr`와 `dgcaa.or.kr` 최근 게시글에서 선불유심내구제/급전 문구와 함께 직접 확인. 작성자 IP 미노출. |
| @rnfma9 | 구름모바일 | 121.170.203.144 | 2026-05-11 | PARTIAL | 신규 후보(USIM/loan) | 행위 키워드 신규 발굴. `tvo.kr` 2026-05-08 상세글에서 선불유심내구제/급전 문구와 `rnfma9rnfma9.isweb.co.kr` 확인. `m.ebbysory.co.kr`에서 작성자 IP 직접 노출. |
| @sk11400 | 산타모바일 | 168.126.234.232 | 2026-05-11 | PARTIAL | 신규 후보(USIM/loan) | 행위 키워드 신규 발굴. `tvo.kr` 2026-05-11 상세글 및 `m.maribel.co.kr` 작성자 IP 노출 원문에서 확인. |

---

## 도메인/URL

| 도메인 | 유형 | 연결 핸들 | 발견 날짜 | 피벗 상태 | 클러스터 | 비고 |
|---|---|---|---|---|---|---|
| brrsim77.isweb.co.kr | 홍보 사이트 | @brrsim_77 | 2026-04-06 | PARTIAL | Cluster#1 | izanaholdings 직접 게시에서 반복 확인됨 |
| abab1768.isweb.co.kr | 홍보 사이트 | @abab1768 | 2026-04-06 | UNVERIFIED | Cluster#1 | 곰돌이통신 |
| abab1768abab1768.isweb.co.kr | 홍보 사이트 (변형) | @abab1768 | 2026-04-06 | PARTIAL | Cluster#1 | 곰돌이통신. matcl.com 게시글 본문에서 직접 URL로 홍보 확인(`http://www.matcl.com/freeboard/11429543`). 현재 다운(invalid response, 2026-04-09) |
| labubu.isweb.co.kr | 홍보 사이트 | @the_usim | 2026-04-09 | UNVERIFIED | Cluster#1 | 라부부통신. matcl.com 스팸 스레드 스니펫에서 교차 언급 |
| holysim.isweb.co.kr | 홍보 사이트 | @holysim | 2026-05-11 | PARTIAL | 신규 후보(USIM/loan) | `tvo.kr` 및 `dgcaa.or.kr` 최근 게시글에서 직접 URL로 확인. 직접 접근은 403 Forbidden. |
| rnfma9rnfma9.isweb.co.kr | 홍보 사이트 | @rnfma9 | 2026-05-11 | PARTIAL | 신규 후보(USIM/loan) | `tvo.kr` 2026-05-08 상세글에서 직접 URL로 확인. 직접 접근은 403 Forbidden. |
| sk11400.isweb.co.kr | 홍보 사이트 | @sk11400 | 2026-05-11 | PARTIAL | 신규 후보(USIM/loan) | `m.maribel.co.kr` 2026-03-26 작성자 IP 노출 원문에서 직접 URL로 확인. |
| puy24.com | 성인약국/pharma 홍보 URL | - | 2026-05-05 | PARTIAL | 성인약국/pharma spam 후보 | `moonyetimes.com` board1 3건에서 `121.170.203.142` 작성자 IP와 함께 반복 노출 |
| hto78.com | 성인약국/pharma 홍보 URL | - | 2026-05-05 | PARTIAL | 성인약국/pharma spam 후보 | `moonyetimes.com` board1 3건에서 `121.170.203.142` 작성자 IP와 함께 반복 노출 |
| kbb12.com | 성인약국/pharma 홍보 URL | - | 2026-05-05 | PARTIAL | 성인약국/pharma spam 후보 | `moonyetimes.com` board1 3건에서 `121.170.203.142` 작성자 IP와 함께 반복 노출 |

> 💡 isweb.co.kr: 무료 웹호스팅 — 스팸 사이트에 자주 악용됨

---

## 닉네임/계정명

| 닉네임 | 연결 IP | 발견 날짜 | 피벗 상태 | 클러스터 | 비고 |
|---|---|---|---|---|---|
| kimyoojin18 | 221.143.197.135, 221.143.197.136, 220.123.216.40, 218.49.179.79, 125.132.9.140, 125.132.9.136, 14.51.2.179, 121.159.134.27 | 2026-04-06 | PARTIAL | Cluster#1 | izanaholdings 직접 게시 재검증으로 추가 6개 IP 확보. bizk.co.kr에서도 @brrsim_77, brrsim77.isweb.co.kr와 함께 확인 |
| 라부부 | 221.143.197.136 | 2026-04-06 | UNVERIFIED | Cluster#1 | |
| 선불유심내구제 | 221.143.197.135, 221.143.197.136 | 2026-04-06 | - | - | 닉네임으로 사용됨 |

---

## 브랜드명

| 브랜드명 | 연결 핸들 | 피벗 상태 | 클러스터 |
|---|---|---|---|
| 뽀로로통신 | @brrsim_77 | PARTIAL | Cluster#1 |
| 곰돌이통신 | @abab1768 | PARTIAL | Cluster#1 |
| 라부부통신 | @the_usim | PARTIAL | Cluster#1 |
| 달림폰 | - | UNVERIFIED | Cluster#1 추정 |

---

## 추가 IP (피벗으로 발견된 IP)

> seed_ips.md에 없는 IP 중 조사 중 새로 발견된 것

| IP | 발견 경로 | 발견 날짜 | 피벗 상태 | 클러스터 | 비고 |
|---|---|---|---|---|---|
| 220.123.216.40 | izanaholdings.com 작성자 IP (`kimyoojin18`) | 2026-04-07 | DONE | Cluster#1 | idx 248894/248914/248944에서 `@brrsim_77`, `brrsim77.isweb.co.kr` 동시 확인 |
| 218.49.179.79 | izanaholdings.com 작성자 IP (`kimyoojin18`) | 2026-04-07 | DONE | Cluster#1 | idx 249514/249524/249534에서 `@brrsim_77`, `brrsim77.isweb.co.kr` 동시 확인 |
| 125.132.9.140 | izanaholdings.com 작성자 IP (`kimyoojin18`) | 2026-04-07 | DONE | Cluster#1 | idx 249374에서 `@brrsim_77`, `brrsim77.isweb.co.kr` 동시 확인 |
| 125.132.9.136 | izanaholdings.com 작성자 IP (`kimyoojin18`) | 2026-04-07 | DONE | Cluster#1 | idx 248794에서 `@brrsim_77`, `brrsim77.isweb.co.kr` 동시 확인 |
| 14.51.2.179 | izanaholdings.com 작성자 IP (`kimyoojin18`) | 2026-04-07 | DONE | Cluster#1 | idx 249124에서 `@brrsim_77`, `brrsim77.isweb.co.kr` 동시 확인 |
| 121.170.203.144 | Cafe24 모바일 게시판 작성자 IP (`@rnfma9`) | 2026-05-11 | PARTIAL | 신규 후보(USIM/loan) | `m.ebbysory.co.kr` 원문에서 `ip:121.170.203.144` 확인. 기존 seed `121.170.203.142`와 같은 /24 |
| 168.126.234.232 | Cafe24 모바일 게시판 작성자 IP (`@sk11400`) | 2026-03-26 | PARTIAL | 신규 후보(USIM/loan) | `m.maribel.co.kr` 원문에서 `ip:168.126.234.232` 확인 |

---

## IOC 피벗 상태 정의

| 상태 | 설명 |
|---|---|
| `UNVERIFIED` | 수집됐지만 아직 이 IOC로 검색/조사 안 함 |
| `PARTIAL` | 일부 조사했지만 추가 피벗 여지 있음 |
| `DONE` | 이 IOC에 대한 조사 완료 |
| `FALSE_POSITIVE` | 무관한 것으로 판명 |
