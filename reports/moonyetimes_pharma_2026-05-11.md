# Moonyetimes pharma spam evidence — 2026-05-11

## 요약

사용자 제공 `moonyetimes.com` board1 원문 3건에서 `121.170.203.142`가 게시글 IP 필드에 직접 노출됨을 확인했다. 본문은 `puy24.com`, `hto78.com`, `kbb12.com`을 반복 홍보하는 성인약국/pharma 스팸이다.

이 증거는 `121.170.203.142`가 스팸 캠페인 작성자 IP임을 보여주지만, 현재까지는 `@rnfma9`/`@sk11400` USIM/loan 후보 또는 Cluster#1 `@brrsim_77`과 공유 IOC가 없다. 따라서 별도 `성인약국/pharma spam 후보`로 분리한다.

## 확인 원문

| idx | URL | 게시일 | 작성자 | 작성자 IP | 핵심 IOC |
|---:|---|---|---|---|---|
| 15434 | `https://www.moonyetimes.com/bbs_shop/read.htm?print_yn=1&board_code=board1&idx=15434` | 2026-05-05 11:52:05 | via | `121.170.203.142` | `puy24.com`, `hto78.com`, `kbb12.com` |
| 15554 | `https://www.moonyetimes.com/bbs_shop/read.htm?print_yn=1&board_code=board1&idx=15554` | 2026-05-05 13:39:20 | asd | `121.170.203.142` | `puy24.com`, `hto78.com`, `kbb12.com` |
| 16554 | `https://www.moonyetimes.com/bbs_shop/read.htm?board_code=board1&idx=16554&poll_idx=0&poll_sel=` | 2026-05-06 15:59:27 | via | `121.170.203.142` | `puy24.com`, `hto78.com`, `kbb12.com` |

## 판정

- `121.170.203.142`는 더 이상 평판 사이트 기반 `LOW` 후보만은 아니다. 원문 직접 증거가 있으므로 `PARTIAL/MEDIUM`으로 상향한다.
- 캠페인 유형은 선불유심/기프티콘/포인트가 아니라 성인약국/pharma 스팸이다.
- 같은 `/24`의 `121.170.203.144`가 `@rnfma9` USIM 후보로 확인됐지만, 현재 두 IP를 동일 행위자로 묶을 공유 IOC는 없다.

## 다음 피벗

- `puy24.com`, `hto78.com`, `kbb12.com` 도메인별 추가 게시글/작성자 IP 검색
- `moonyetimes.com` board1 인접 idx/목록 순회
- `121.170.203.0/24` 내 pharma 스팸과 USIM/loan 스팸 간 공유 URL/문구/닉네임 존재 여부 확인
