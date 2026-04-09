# 스팸 피해 사이트 목록 (Spammed Sites)

> 이 프로젝트에서 추적 중인 IP들이 스팸 게시글을 남긴 사이트 목록.
> 이들 사이트 자체는 피해자이며, 역으로 이 사이트의 게시판 IP 로그를 통해 추가 IOC 수집 가능.

---

**스크래퍼 컬럼:** `izanaholdings` = 전용 HTML 스크래퍼 (`scripts/scrapers/izanaholdings.py`, **깊은 티어**·`METHODOLOGY.md` §2.4). `ddg_site` = `site:도메인 "{IP}"` DDG 검색으로 **키워드·히트 수**만 (본문 직접 파싱 아님, **얕은 티어**). `investigate_ip.py`는 기본적으로 **`ddg_site` 행 전부**를 순회한다 (`--ddg-site-limit`으로만 상한).

## 확인된 피해 사이트

| 사이트 | URL | 유형 | 발견 IP | 발견 경로(IOC) | 게시 내용 | 비고 | 스크래퍼 |
|---|---|---|---|---|---|---|---|
| 이자나홀딩스 | izanaholdings.com | 기업 게시판 | 221.143.197.135/136, 220.123.216.40, 218.49.179.79, 125.132.9.140, 125.132.9.136, 14.51.2.179 | seed IP 직접 + kimyoojin18 피벗 | 선불유심내구제, @brrsim_77, @the_usim | 게시글에 작성 IP 노출됨. 검색 페이지는 false negative가 있어 목록 순회 필요 ⭐. HTML에 `board_code=board` 외 **`board1`** 존재 — 스팸은 주로 `board` | izanaholdings |
| 사랑나누미 | 사랑나누미.com | 봉사/나눔 | 221.143.197.135/136 | seed IP 직접 | @brrsim_77, @abab1768 | | ddg_site |
| 광주광역시사회복지협의회 | gjw.or.kr | 공공기관 | 221.143.197.135/136 | seed IP 직접 | 스팸 다수 | | ddg_site |
| 부산대 채널PNU | channelpnu.pusan.ac.kr | 대학 | 221.143.197.136 | seed IP 직접 | @brrsim_77, 약물스팸(@krfa8) | 약물 스팸도 포함 | ddg_site |
| haccpkoreamall | haccpkoreamall.com | 쇼핑몰 | 221.143.197.136 | seed IP 직접 | @the_usim 라부부통신 | | ddg_site |
| 청소년 공연예술축제 | chunggong.or.kr | 공공기관 | - | @brrsim_77 피벗 | @brrsim_77 | | ddg_site |
| DBpia 커뮤니티 | community.dbpia.co.kr | 학술 | - | @brrsim_77 피벗 | @brrsim_77 | | ddg_site |
| 선도산림경영단지 | sundofm.or.kr | 공공기관 | - | @abab1768 피벗 | @abab1768 | | ddg_site |
| 루마니아 한인회 | homepy.korean.net | 재외동포 | - | @brrsim_77 피벗 | @brrsim_77 | | ddg_site |
| 영월군가족센터 | toy.ywwelfare.org | 공공기관 | - | @brrsim_77/@abab1768 피벗 | @brrsim_77, @abab1768 | | ddg_site |
| 컨피네스 오션 스위트 | chonpinesoceansuites.com | 숙박 | - | @abab1768 피벗 | @abab1768 | | ddg_site |
| 한신대학교 | hs.ac.kr | 대학 | - | @the_usim 피벗 | @the_usim | | ddg_site |
| 봉화뉴스 | bonghwanews.com | 지역언론 | - | @brrsim_77 피벗 | @brrsim_77 | | ddg_site |
| 댄스코드 | dancecode.kr | 커뮤니티 | - | @the_usim 피벗 | @the_usim | | ddg_site |
| 창업코리아 커뮤니티 | bizk.co.kr | 창업 커뮤니티 | - | kimyoojin18 피벗 | kimyoojin18, @brrsim_77, brrsim77.isweb.co.kr | 작성자 닉네임이 공개됨 | ddg_site |
| 한국일보 애틀랜타 | higoodday.com | 한인 커뮤니티 | - | @brrsim_77 피벗 | 김유진, @brrsim_77 | 게시글 인덱스에서 반복 노출 확인 | ddg_site |
| 트로스트 커뮤니티 | trost.co.kr | 커뮤니티 | - | @brrsim_77 피벗 | @brrsim_77, brrsim77.isweb.co.kr | 검색 결과 스니펫으로 게시 흔적 확인 | ddg_site |
| 금산진악신문 | 금산진악신문.com | 지역언론 | 221.143.197.135 | seed IP 직접 | @brrsim_77 | | ddg_site |
| 연안김씨뉴스 | yeonkimnews.or.kr | 종친회 | 221.143.197.135 | seed IP 직접 | @brrsim_77 | 첨부파일 포함 | ddg_site |
| 울진21 | uljin21.com | 지역커뮤니티 | 221.143.197.135 | seed IP 직접 | (삭제됨) | 관리자 삭제 | ddg_site |
| 맛클(유저 포럼·자유게시판 등) | www.matcl.com | IT/커뮤니티 | - | @abab1768, @the_usim 피벗 | 곰돌이통신·라부부통신, `abab1768.isweb.co.kr`, `labubu.isweb.co.kr` 유도 | DDG 색인 다수 스레드(예: `/forum/…`, `/freeboard/…`). 작성자 IP 미확인 | ddg_site |

---

## 주요 패턴 분석

**타겟 사이트 유형 (빈도순):**
1. 공공기관/사회복지 게시판 — 보안이 약하고 관리 소홀
2. 지역 언론/커뮤니티 — 회원가입 없이 게시 가능한 경우 多
3. 대학교 게시판 — 개방적 접근
4. 기업 게시판 — 노출 IP 정보 확인 가능 (izanaholdings.com ⭐)

**izanaholdings.com 특이사항:**
게시글 하단에 **작성자 IP 주소가 직접 노출**됨 → 이 사이트를 체계적으로 모니터링하면 동일 행위자의 다른 IP를 자동으로 수집 가능. 피벗 조사 핵심 소스.

`/bbs/board` exact 검색은 `등록된 게시글이 없습니다`를 반환해도 최근글 위젯만 함께 노출되는 false negative가 발생한다. 새 IP 수집 시에는 `bbs_shop/list.htm?board_code=board&page=N` 목록을 직접 순회한 뒤 개별 `read.htm` 본문을 열어 작성자 IP를 확인해야 한다.

**스크래퍼 주의:** 대상 IP 문자열을 HTML 전체에 `in`으로 찾지 말 것. 예: `221.143.197.13`은 `221.143.197.130`~`136`에 부분 문자열로 포함되므로 **작성자 IP 필드 파싱 후 완전 일치**로만 매칭한다 (`scripts/scrapers/izanaholdings.py`).
