# 스팸 피해 사이트 목록 (Spammed Sites)

> 이 프로젝트에서 추적 중인 IP들이 스팸 게시글을 남긴 사이트 목록.
> 이들 사이트 자체는 피해자이며, 역으로 이 사이트의 게시판 IP 로그를 통해 추가 IOC 수집 가능.

---

## 확인된 피해 사이트

| 사이트 | URL | 유형 | 발견 IP | 발견 경로(IOC) | 게시 내용 | 비고 |
|---|---|---|---|---|---|---|
| 이자나홀딩스 | izanaholdings.com | 기업 게시판 | 221.143.197.135/136, 220.123.216.40, 218.49.179.79, 125.132.9.140, 125.132.9.136, 14.51.2.179 | seed IP 직접 + kimyoojin18 피벗 | 선불유심내구제, @brrsim_77, @the_usim | 게시글에 작성 IP 노출됨. 검색 페이지는 false negative가 있어 목록 순회 필요 ⭐ |
| 사랑나누미 | 사랑나누미.com | 봉사/나눔 | 221.143.197.135/136 | seed IP 직접 | @brrsim_77, @abab1768 | |
| 광주광역시사회복지협의회 | gjw.or.kr | 공공기관 | 221.143.197.135/136 | seed IP 직접 | 스팸 다수 | |
| 부산대 채널PNU | channelpnu.pusan.ac.kr | 대학 | 221.143.197.136 | seed IP 직접 | @brrsim_77, 약물스팸(@krfa8) | 약물 스팸도 포함 |
| haccpkoreamall | haccpkoreamall.com | 쇼핑몰 | 221.143.197.136 | seed IP 직접 | @the_usim 라부부통신 | |
| 청소년 공연예술축제 | chunggong.or.kr | 공공기관 | - | @brrsim_77 피벗 | @brrsim_77 | |
| DBpia 커뮤니티 | community.dbpia.co.kr | 학술 | - | @brrsim_77 피벗 | @brrsim_77 | |
| 선도산림경영단지 | sundofm.or.kr | 공공기관 | - | @abab1768 피벗 | @abab1768 | |
| 루마니아 한인회 | homepy.korean.net | 재외동포 | - | @brrsim_77 피벗 | @brrsim_77 | |
| 영월군가족센터 | toy.ywwelfare.org | 공공기관 | - | @brrsim_77/@abab1768 피벗 | @brrsim_77, @abab1768 | |
| 컨피네스 오션 스위트 | chonpinesoceansuites.com | 숙박 | - | @abab1768 피벗 | @abab1768 | |
| 한신대학교 | hs.ac.kr | 대학 | - | @the_usim 피벗 | @the_usim | |
| 봉화뉴스 | bonghwanews.com | 지역언론 | - | @brrsim_77 피벗 | @brrsim_77 | |
| 댄스코드 | dancecode.kr | 커뮤니티 | - | @the_usim 피벗 | @the_usim | |
| 창업코리아 커뮤니티 | bizk.co.kr | 창업 커뮤니티 | - | kimyoojin18 피벗 | kimyoojin18, @brrsim_77, brrsim77.isweb.co.kr | 작성자 닉네임이 공개됨 |
| 한국일보 애틀랜타 | higoodday.com | 한인 커뮤니티 | - | @brrsim_77 피벗 | 김유진, @brrsim_77 | 게시글 인덱스에서 반복 노출 확인 |
| 트로스트 커뮤니티 | trost.co.kr | 커뮤니티 | - | @brrsim_77 피벗 | @brrsim_77, brrsim77.isweb.co.kr | 검색 결과 스니펫으로 게시 흔적 확인 |
| 금산진악신문 | 금산진악신문.com | 지역언론 | 221.143.197.135 | seed IP 직접 | @brrsim_77 | |
| 연안김씨뉴스 | yeonkimnews.or.kr | 종친회 | 221.143.197.135 | seed IP 직접 | @brrsim_77 | 첨부파일 포함 |
| 울진21 | uljin21.com | 지역커뮤니티 | 221.143.197.135 | seed IP 직접 | (삭제됨) | 관리자 삭제 |

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
