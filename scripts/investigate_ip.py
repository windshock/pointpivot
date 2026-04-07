#!/usr/bin/env python3
"""
investigate_ip.py - DuckDuckGo + izanaholdings.com 직접 스크래핑 기반 IP 자동 조사

사용법:
    python scripts/investigate_ip.py 221.143.197.13
    python scripts/investigate_ip.py --batch --limit 5
    python scripts/investigate_ip.py --batch --service ocb --limit 3
"""

import argparse
import re
import subprocess
import sys
import time
import warnings
from datetime import date
from pathlib import Path

warnings.filterwarnings("ignore")  # SSL verify=False 경고 억제

try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        print("필요 패키지 없음: pip install ddgs")
        sys.exit(1)

try:
    from curl_cffi import requests as cffi_req
    CFFI_AVAILABLE = True
except ImportError:
    CFFI_AVAILABLE = False

sys.path.insert(0, str(Path(__file__).parent))
from utils import (ROOT, INVESTIGATIONS, get_unverified_ips, update_index_ip,
                   register_new_telegrams, register_new_domains, infer_cluster)

UNCLASSIFIED = INVESTIGATIONS / "unclassified"

# ── IOC 추출 패턴 ─────────────────────────────────────────────────────────────
TELEGRAM_RE = re.compile(r'@[a-zA-Z0-9_]{3,32}')
ISWEB_RE = re.compile(r'[a-zA-Z0-9_-]+\.isweb\.co\.kr')
IP_RE = re.compile(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b')
NON_TG_TOKENS = {'@naver', '@media'}

FRAUD_KEYWORDS = ['내구제', '선불유심', '유심매입', '기프티콘', '포인트현금화',
                  '소액대출', '급전', '계정구매', '약물', '엑스터시']
# '텔레그램' 제외: 너무 일반적 — 검색 결과 노이즈 유발

# izanaholdings.com 게시판 설정
IZANA_BASE = "https://izanaholdings.com"
IZANA_BOARD = f"{IZANA_BASE}/bbs/board"
IZANA_SEARCH = f"{IZANA_BASE}/bbs/board?search_key=subject_content&key={{ip}}&paged={{page}}"
IZANA_LIST = f"{IZANA_BASE}/bbs_shop/list.htm?board_code=board&page={{page}}"
IZANA_POST = f"{IZANA_BASE}/bbs_shop/read.htm?board_code=board&idx={{idx}}&cate_sub_idx=0"

# ── curl_cffi 세션 (재사용) ───────────────────────────────────────────────────
_session = None

def get_session():
    global _session
    if CFFI_AVAILABLE and _session is None:
        _session = cffi_req.Session(impersonate="chrome", verify=False)
    return _session


def fetch(url: str, timeout: int = 15) -> str | None:
    """shell curl 우선, 실패 시 curl_cffi로 페이지 가져오기."""
    try:
        proc = subprocess.run(
            ['curl', '-k', '-L', '-A', 'Mozilla/5.0', url],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        if proc.returncode == 0 and proc.stdout:
            return proc.stdout
    except Exception as e:
        print(f"  [fetch 오류:curl] {url[:60]}: {e}")

    s = get_session()
    if s is not None:
        try:
            r = s.get(url, timeout=timeout)
            if r.status_code == 200 and r.text:
                return r.text
        except Exception as e:
            print(f"  [fetch 오류:cffi] {url[:60]}: {e}")

    return None


# ── izanaholdings.com 스크래퍼 ────────────────────────────────────────────────

def scrape_izanaholdings(ip: str) -> dict:
    """
    izanaholdings.com 게시판에서 IP 직접 검색.
    반환: {posts: [...], iocs: {...}, author_ips: [...]}
    """
    result = {'posts': [], 'iocs': {'telegram': set(), 'isweb': set(), 'keywords': set()},
              'author_ips': set()}

    if not CFFI_AVAILABLE:
        return result

    print(f"  [izana] 게시판 직접 검색: {ip}")

    seen_idxs: set[str] = set()

    def inspect_listing(url: str) -> bool:
        html = fetch(url)
        if not html:
            return False

        # 검색 결과 페이지에서 게시글 링크만 수집 (IOC 추출은 하지 않음)
        # 사이드바·최근글 위젯에 무관한 IOC가 섞이는 걸 방지
        post_idxs = re.findall(r'idx=(\d+)', html)
        found_any = False

        for idx in post_idxs:
            if idx in seen_idxs or not idx.isdigit():
                continue
            seen_idxs.add(idx)

            post_html = fetch(IZANA_POST.format(idx=idx))
            if not post_html:
                continue

            # 이 게시글 본문에 실제로 IP가 언급되는지 확인
            if ip not in post_html:
                continue

            found_any = True

            # 게시글 제목
            title_m = re.search(r'<title[^>]*>([^<]+)</title>', post_html)
            title = title_m.group(1).strip() if title_m else f'게시글 #{idx}'

            # 작성자 IP는 제목 메타 정보의 마지막 <span>에 노출된다.
            author_ip_m = re.search(
                r'<span>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</span>\s*</dt>',
                post_html,
            )
            if not author_ip_m:
                author_ip_m = re.search(
                    r'<li>\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*</li>',
                    post_html,
                )
            author_ip = author_ip_m.group(1) if author_ip_m else ''
            if author_ip:
                result['author_ips'].add(author_ip)

            # 실제 매칭된 게시글에서만 IOC 추출
            _update_iocs(result['iocs'], post_html)

            result['posts'].append({
                'idx': idx,
                'title': title,
                'url': IZANA_POST.format(idx=idx),
                'author_ip': author_ip,
            })

            time.sleep(0.5)

        return found_any

    # 1) exact 검색 페이지 시도
    for page in range(1, 4):
        url = IZANA_SEARCH.format(ip=ip, page=page)
        found_any = inspect_listing(url)
        if not found_any:
            break
        time.sleep(1)

    # 2) exact 검색 false negative 대비: 최근 목록 직접 순회
    if not result['posts']:
        print("         exact 검색 결과 없음 → 최근 목록 직접 순회")
        for page in range(1, 4):
            inspect_listing(IZANA_LIST.format(page=page))
            time.sleep(1)

    # set → sorted list
    result['iocs'] = {k: sorted(v) for k, v in result['iocs'].items()}
    result['author_ips'] = sorted(result['author_ips'])

    found = len(result['posts'])
    print(f"         게시글 {found}건, TG: {result['iocs']['telegram']}, "
          f"작성자IP: {result['author_ips']}")
    return result


def _update_iocs(iocs: dict, text: str):
    tgs = [t for t in TELEGRAM_RE.findall(text) if t.lower() not in NON_TG_TOKENS]
    iocs['telegram'].update(tgs)
    iocs['isweb'].update(ISWEB_RE.findall(text))
    iocs['keywords'].update(kw for kw in FRAUD_KEYWORDS if kw in text)


# ── DuckDuckGo 검색 ───────────────────────────────────────────────────────────
def build_queries(ip: str) -> list[tuple[str, str]]:
    return [
        (f'"{ip}"', 'exact'),
        (f'"{ip}" 내구제 OR 유심 OR 기프티콘 OR 텔레그램', 'fraud'),
    ]


def search(query: str, max_results: int = 20) -> list[dict]:
    try:
        with DDGS() as ddgs:
            return list(ddgs.text(query, max_results=max_results))
    except Exception as e:
        print(f"  [DDG 오류] {query!r}: {e}")
        return []


def extract_iocs(text: str) -> dict:
    tgs = [t for t in TELEGRAM_RE.findall(text) if t.lower() not in NON_TG_TOKENS]
    return {
        'telegram': sorted(set(tgs)),
        'isweb': sorted(set(ISWEB_RE.findall(text))),
        'keywords': [kw for kw in FRAUD_KEYWORDS if kw in text],
    }


# ── 조사 실행 (DDG + izana 병합) ─────────────────────────────────────────────
def investigate(ip: str) -> dict:
    print(f"\n{'='*60}")
    print(f"  조사 대상: {ip}")
    print(f"{'='*60}")

    all_results = []
    all_iocs = {'telegram': set(), 'isweb': set(), 'keywords': set()}

    # 1. DuckDuckGo
    for query, label in build_queries(ip):
        print(f"  [DDG:{label}] {query}")
        results = search(query)
        print(f"           결과 {len(results)}건")
        all_results.extend(results)
        combined = ' '.join(r.get('title', '') + ' ' + r.get('body', '') for r in results)
        iocs = extract_iocs(combined)
        # DDG 스니펫의 핸들/도메인은 최근글 위젯이나 무관 문서가 섞일 수 있다.
        # 직접 본문에서 확인된 IOC만 등록하고, 검색 결과는 키워드 힌트로만 사용한다.
        all_iocs['keywords'].update(iocs['keywords'])
        time.sleep(1.5)

    # 2. izanaholdings.com 직접 스크래핑
    izana_data = scrape_izanaholdings(ip)
    all_iocs['telegram'].update(izana_data['iocs']['telegram'])
    all_iocs['isweb'].update(izana_data['iocs']['isweb'])
    all_iocs['keywords'].update(izana_data['iocs']['keywords'])

    # 신뢰도 판정
    # izana에서 직접 게시 확인 = 신뢰도 강화
    direct_post = len(izana_data['posts']) > 0
    has_keywords = bool(all_iocs['keywords'])
    has_telegram = bool(all_iocs['telegram'])
    direct_ioc_count = len(izana_data['iocs']['telegram']) + len(izana_data['iocs']['isweb'])

    if direct_post and direct_ioc_count >= 2:
        confidence = 'HIGH'
    elif direct_post:
        confidence = 'MEDIUM'
    elif has_keywords and has_telegram:
        confidence = 'LOW'
    elif has_keywords or has_telegram:
        confidence = 'LOW'
    elif all_results:
        confidence = 'LOW'
    else:
        confidence = 'UNVERIFIED'
    has_spam = has_keywords or has_telegram  # 하위 호환

    return {
        'ip': ip,
        'results': all_results,
        'iocs': {k: sorted(v) for k, v in all_iocs.items()},
        'izana': izana_data,
        'has_spam': has_spam,
        'direct_post': direct_post,
        'confidence': confidence,
    }


# ── 보고서 생성 ───────────────────────────────────────────────────────────────
def generate_report(data: dict) -> str:
    ip = data['ip']
    iocs = data['iocs']
    results = data['results']
    izana = data.get('izana', {})
    today = date.today().isoformat()

    # DDG 검색 결과 테이블
    result_rows = []
    for r in results[:8]:
        title = r.get('title', '').replace('|', '｜')[:55]
        url = r.get('href', '')[:70]
        snippet = r.get('body', '').replace('\n', ' ').replace('|', '｜')[:70]
        result_rows.append(f"| {title} | {url} | {snippet} |")
    results_table = '\n'.join(result_rows) if result_rows else '| (결과 없음) | - | - |'

    # izanaholdings 게시글 테이블
    izana_posts = izana.get('posts', [])
    izana_rows = []
    for p in izana_posts:
        title = p['title'].replace('|', '｜')[:60]
        url = p['url'][:80]
        author_ip = p.get('author_ip', '-')
        izana_rows.append(f"| {title} | {url} | {author_ip} |")
    izana_table = '\n'.join(izana_rows) if izana_rows else '| (게시글 없음) | - | - |'

    # IOC 테이블
    ioc_rows = []
    for tg in iocs['telegram']:
        src = 'izanaholdings.com (직접)' if tg in izana.get('iocs', {}).get('telegram', []) else '간접'
        ioc_rows.append(f"| 텔레그램 | {tg} | {src} | {today} | ❌ |")
    for domain in iocs['isweb']:
        src = 'izanaholdings.com (직접)' if domain in izana.get('iocs', {}).get('isweb', []) else '간접'
        ioc_rows.append(f"| 도메인 | {domain} | {src} | {today} | ❌ |")
    ioc_table = '\n'.join(ioc_rows) if ioc_rows else '| (IOC 없음) | - | - | - | - |'

    author_ips = izana.get('author_ips', [])
    direct_note = (f'✅ izanaholdings.com에서 직접 게시 {len(izana_posts)}건 확인'
                   if izana_posts else '❌ izanaholdings.com 직접 게시 미확인')
    status = 'DONE' if izana_posts else ('PARTIAL' if results else 'UNVERIFIED')

    sources = []
    if results:
        sources.append(f'DuckDuckGo {len(results)}건')
    if izana_posts:
        sources.append(f'izanaholdings 직접 {len(izana_posts)}건')

    report = f"""# 조사 보고서: {ip}

> ⚠️ 자동 생성 초안. IOC 신규 발견 시 `data/ioc_registry.md` 수동 등록 필요.

**조사일:** {today}
**조사자:** auto (investigate_ip.py + curl_cffi)
**상태:** {status}
**클러스터:** {data.get('cluster', '미분류')}
**신뢰도:** {data['confidence']}

---

## IP 기본 정보

| 항목 | 값 |
|---|---|
| IP | {ip} |
| ISP / ASN | (수동 확인 필요) |
| IP 범위 (/24) | {'.'.join(ip.split('.')[:3])}.0/24 |
| AbuseIPDB | (수동 확인 필요) |
| 인프라 유형 | (수동 확인 필요) |

---

## 사용된 검색 방법

- [x] DuckDuckGo: `"{ip}"`
- [x] DuckDuckGo: `"{ip}" 내구제 OR 유심 OR 기프티콘 OR 텔레그램`
- [x] izanaholdings.com 게시판 직접 검색 (curl_cffi)

**수집 결과:** {', '.join(sources) if sources else '결과 없음'}

---

## izanaholdings.com 직접 게시 확인

{direct_note}

| 게시글 제목 | URL | 작성자 IP |
|---|---|---|
{izana_table}

{"**추가 발견 작성자 IP:** " + ', '.join(author_ips) if author_ips else ''}

---

## DuckDuckGo 검색 결과 (상위 8건)

| 제목 | URL | 스니펫 |
|---|---|---|
{results_table}

---

## 추출된 IOC

| IOC 유형 | 값 | 출처 | 발견일 | ioc_registry 등록 |
|---|---|---|---|---|
{ioc_table}

**발견된 사기 키워드:** {', '.join(iocs['keywords']) if iocs['keywords'] else '없음'}

---

## 클러스터 귀속 근거

> 신뢰도 `{data['confidence']}` — {'izana 직접 게시 확인됨' if izana_posts else 'DDG 스니펫 기반, 직접 검증 권장'}

---

## 다음 피벗 대상

{"".join(f"- [ ] {tg} — 텔레그램 핸들 피벗{chr(10)}" for tg in iocs['telegram'])}{"".join(f"- [ ] {d} — 도메인 직접 조회{chr(10)}" for d in iocs['isweb'])}{"".join(f"- [ ] {aip} — 새로 발견된 작성자 IP 조사{chr(10)}" for aip in author_ips if aip != ip)}- [ ] ioc_registry.md에 신규 IOC 등록
"""
    return report




# ── 메인 ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='IP 자동 조사 스크립트')
    parser.add_argument('ip', nargs='?', help='조사할 IP 주소')
    parser.add_argument('--batch', action='store_true', help='INDEX.md에서 UNVERIFIED IP 배치 조사')
    parser.add_argument('--limit', type=int, default=5, help='배치 최대 처리 수 (기본: 5)')
    parser.add_argument('--service', choices=['svc_a', 'gifticon', 'svc_c'], help='특정 서비스만 처리')
    parser.add_argument('--dry-run', action='store_true', help='파일 저장 없이 출력만')
    args = parser.parse_args()

    UNCLASSIFIED.mkdir(parents=True, exist_ok=True)

    if args.batch:
        ips = get_unverified_ips(args.service)
        if not ips:
            print("조사할 UNVERIFIED IP가 없습니다.")
            return
        ips = ips[:args.limit]
        print(f"배치 조사 시작: {len(ips)}개 IP")
        for ip in ips:
            run_single(ip, args.dry_run)
            time.sleep(3)  # IP 간 대기
    elif args.ip:
        run_single(args.ip, args.dry_run)
    else:
        parser.print_help()


def run_single(ip: str, dry_run: bool = False):
    data = investigate(ip)

    iocs = data['iocs']
    today = date.today().isoformat()

    # ── 클러스터 자동 귀속 ───────────────────────────────────────────
    cluster = infer_cluster(iocs['telegram'] + iocs['isweb'])
    data['cluster'] = cluster

    # ── IOC 자동 등록 ────────────────────────────────────────────────
    if not dry_run:
        new_tg = register_new_telegrams(iocs['telegram'], ip, today)
        new_dom = register_new_domains(iocs['isweb'], ip, today)
        if new_tg:
            print(f"  ioc_registry 신규 등록 (텔레그램): {new_tg}")
        if new_dom:
            print(f"  ioc_registry 신규 등록 (도메인): {new_dom}")

    report = generate_report(data)
    out_path = UNCLASSIFIED / f"{ip}.md"

    if dry_run:
        print("\n[dry-run] 보고서 미리보기:")
        print(report[:1200] + "\n...")
    else:
        out_path.write_text(report, encoding='utf-8')
        print(f"\n  보고서 저장: {out_path}")
        rel_path = str(out_path.relative_to(INVESTIGATIONS))
        updated = update_index_ip(ip, 'PARTIAL', rel_path)
        if updated:
            print(f"  INDEX.md 업데이트: {ip} → PARTIAL")

    # 요약 출력
    print(f"\n  결과 요약:")
    print(f"    검색 결과: {len(data['results'])}건 (DDG) + izana {len(data.get('izana',{}).get('posts',[]))}건")
    print(f"    텔레그램:  {iocs['telegram'] or '없음'}")
    print(f"    도메인:    {iocs['isweb'] or '없음'}")
    print(f"    키워드:    {iocs['keywords'] or '없음'}")
    print(f"    클러스터:  {cluster}")
    print(f"    신뢰도:    {data['confidence']}")


if __name__ == '__main__':
    main()
