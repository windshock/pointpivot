# Phase 6 OSINT 메모 (2026-04-09)

> 자동화 에이전트가 공개 웹 검색·HTTP 조회로 수행한 **제한적** 점검. 브라우저 본문 확인·게시글 IP 추출은 대체하지 않는다.

## 221.143.197.13

- 공개 색인·`site:izanaholdings.com` 결합: 이전과 같이 **직접 인용 가능한 결과 없음**.
- **2026-04-09:** `curl -k -sL`로 `https://izanaholdings.com/bbs/board?search_key=subject_content&key=221.143.197.13&paged=1` 수신 시 HTML에 `<li class="empty">등록된 게시글이 없습니다.</li>` 확인.
- **2026-04-09 (추가):** `list.htm` **page 1–35** + 각 `read.htm`에서 **작성자 IP 필드와 대상 IP 완전 일치**로만 판정 → **게시 0건.** (부분 문자열 매칭 오탐은 스크래퍼에서 제거함.)

## @abab1768 / @the_usim

- **2026-04-09 공개 색인:** `www.matcl.com`(맛클) 유저 포럼·자유게시판 등에서 `@abab1768`+곰돌이통신+`abab1768.isweb.co.kr`, `@the_usim`+라부부통신+`labubu.isweb.co.kr` 스팸 스레드 **다수** (스니펫·URL 제목 수준).
- 저장소 반영: `data/spammed_sites.md`, `data/ioc_registry.md`, `data/campaigns.md`.
- **미완료:** 스레드 본문·작성자 IP 확보, `investigate_ioc.py` 역피벗으로 **새 residential IP** 자동 등록.

## 5개 피벗 IP 교차 사이트

- 자동 스크립트 경로: `investigate_ip.py`가 `spammed_sites.md`의 `ddg_site` 도메인에 대해 `site:도메인 "{IP}"` 검색을 수행함. **키워드 힌트**이며 DONE 판정은 수동.
- **2026-04-09 샘플:** `220.123.216.40` 단독, `218.49.179.79`·`125.132.9.140`·`14.51.2.179`를 스팸 키워드와 결합한 공개 검색에서 **스니펫에 해당 IPv4 미등장** — 교차 게시 **미발견**으로 기록. `ddg_site` 일괄은 계속 권장.

## izanaholdings `board1` · 고번호 목록

- 메인 페이지에 `board_code=board1` 노출. **2026-04-09** 자동화 연속 요청 시 목록 URL이 **타임아웃** 다발(원격 지연·레이트리밋 추정) → `221.143.197.13`에 대한 **board1 본문·작성자 IP는 미확정**. `board`는 page **36–59** 추가 순회에서도 `.13` 작성자 일치 **0건**; page **60** 단일 요청도 타임아웃.

## 다음 조치 (사람/브라우저·venv)

1. izanaholdings 목록 순회로 `221.143.197.13` 작성자 IP 일치 여부 ([`STATUS.md`](../STATUS.md) 최우선 잔여).
2. `www.matcl.com` 스팸 스레드 본문 열람·스크린샷·작성자 메타(있으면) 보관.
3. Homebrew Python 3.14 등 PEP 668 환경에서는 프로젝트 루트 **venv** 생성 후 `pip install -r scripts/requirements.txt` → `investigate_ioc.py` / `investigate_ip.py` 재실행.
