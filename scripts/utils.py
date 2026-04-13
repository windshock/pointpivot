"""
utils.py - PointPivot 마크다운 파싱 공통 유틸리티
"""

import json
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from dataclasses import dataclass, field
from typing import Literal

ROOT = Path(__file__).parent.parent
INDEX_MD = ROOT / "investigations" / "INDEX.md"
IOC_REGISTRY = ROOT / "data" / "ioc_registry.md"
SEED_IPS = ROOT / "data" / "seed_ips.md"
CAMPAIGNS_MD = ROOT / "data" / "campaigns.md"
SPAMMED_SITES = ROOT / "data" / "spammed_sites.md"
INVESTIGATIONS = ROOT / "investigations"


# ── 데이터 클래스 ─────────────────────────────────────────────────────────────

@dataclass
class IPEntry:
    ip: str
    status: str          # UNVERIFIED | PARTIAL | DONE
    cluster: str         # Cluster#1 | 미분류 | -
    infra: str           # KR_RESIDENTIAL | VPS_GLOBAL | ...
    report_path: str     # 상대 경로 or "-"
    service: str = ""    # svc_a | gifticon | svc_c
    confidence: str = "" # HIGH | MEDIUM | LOW | UNVERIFIED (보고서에서 읽음)


@dataclass
class TelegramIOC:
    handle: str
    brand: str
    source_ip: str
    found_date: str
    pivot_status: str    # UNVERIFIED | PARTIAL | DONE | FALSE_POSITIVE
    cluster: str
    note: str


@dataclass
class DomainIOC:
    domain: str
    ioc_type: str
    linked_handle: str
    found_date: str
    pivot_status: str
    cluster: str
    note: str = ""


# ── 마크다운 테이블 파싱 헬퍼 ──────────────────────────────────────────────────

def parse_md_table_rows(text: str, section_header: str) -> list[list[str]]:
    """
    마크다운 텍스트에서 특정 섹션의 테이블 행들을 파싱.
    헤더 행과 구분선 행은 건너뜀.
    """
    # 섹션 시작 찾기
    start = text.find(section_header)
    if start == -1:
        return []

    # 다음 ## 섹션까지만 추출
    next_section = text.find('\n## ', start + 1)
    section_text = text[start:next_section] if next_section != -1 else text[start:]

    rows = []
    for line in section_text.splitlines():
        line = line.strip()
        if not line.startswith('|'):
            continue
        # 구분선 행 (`|---|---|`) 건너뜀
        if re.match(r'^\|[-| :]+\|$', line):
            continue
        # 헤더 행 (IP, 상태, 핸들 등으로 시작) 건너뜀
        cells = [c.strip() for c in line.strip('|').split('|')]
        if cells and cells[0].lower() in ('ip', '핸들', '도메인', '닉네임', '브랜드명',
                                           '사이트', '서비스', '클러스터', '항목'):
            continue
        if cells:
            rows.append(cells)
    return rows


def extract_link_text(cell: str) -> str:
    """마크다운 링크 `[텍스트](url)` 에서 url 반환. 링크 없으면 cell 그대로."""
    m = re.search(r'\[.*?\]\((.*?)\)', cell)
    return m.group(1) if m else cell.strip()


def normalize_status(raw: str) -> str:
    """상태값 정규화 (대소문자, 앞뒤 공백)"""
    s = raw.strip().upper()
    valid = {'UNVERIFIED', 'PARTIAL', 'DONE', 'FALSE_POSITIVE'}
    return s if s in valid else 'UNVERIFIED'


# ── INDEX.md 파싱 ─────────────────────────────────────────────────────────────

def parse_index() -> list[IPEntry]:
    """INDEX.md에서 모든 IP 항목 파싱"""
    if not INDEX_MD.exists():
        return []

    text = INDEX_MD.read_text(encoding='utf-8')
    entries: list[IPEntry] = []
    service_map = {
        '## 서비스A IP 목록': 'svc_a',
        '## 기프티콘 IP 목록': 'gifticon',
        '## 서비스C IP 목록': 'svc_c',
        '## 피벗으로 추가 확보한 IP': 'pivot',
        '## @GO174 역피벗으로 추가 확보한 IP': 'pivot',
    }

    for section_header, service in service_map.items():
        rows = parse_md_table_rows(text, section_header)
        for cells in rows:
            if len(cells) < 2:
                continue
            ip = cells[0].strip()
            # 유효한 IP 형식인지 간단 체크
            if not re.match(r'^\d+\.\d+\.\d+\.\d+$', ip):
                continue

            # 컬럼 수가 달라도 유연하게 처리
            status = normalize_status(cells[1]) if len(cells) > 1 else 'UNVERIFIED'
            cluster = cells[2].strip() if len(cells) > 2 else '-'
            infra = cells[3].strip() if len(cells) > 3 else '-'
            # 조사 파일 링크는 항상 마지막 컬럼 (lifecycle 컬럼 추가 시에도 동작)
            report_raw = cells[-1].strip() if len(cells) > 4 else '-'
            report_path = extract_link_text(report_raw) if report_raw != '-' else '-'

            # 중복 IP (동일 IP가 여러 서비스에 있는 경우) — 이미 있으면 서비스만 추가
            existing = next((e for e in entries if e.ip == ip), None)
            if existing:
                if service not in existing.service:
                    existing.service += f',{service}'
                continue

            entries.append(IPEntry(
                ip=ip, status=status, cluster=cluster,
                infra=infra, report_path=report_path, service=service
            ))

    return entries


def parse_seed_ips() -> list[IPEntry]:
    """seed_ips.md에서 seed IP 항목만 파싱"""
    if not SEED_IPS.exists():
        return []

    text = SEED_IPS.read_text(encoding='utf-8')
    entries: list[IPEntry] = []
    service_map = {
        '## 서비스A IP 차단요청 내역': 'svc_a',
        '## 서비스C IP 차단 내역': 'svc_c',
        '## 기프티콘 유입 IP': 'gifticon',
    }

    for section_header, service in service_map.items():
        rows = parse_md_table_rows(text, section_header)
        for cells in rows:
            if len(cells) < 2:
                continue
            ip = cells[0].strip()
            if not re.match(r'^\d+\.\d+\.\d+\.\d+$', ip):
                continue

            status = normalize_status(cells[1]) if len(cells) > 1 else 'UNVERIFIED'
            infra = cells[2].strip() if len(cells) > 2 else '-'
            cluster = cells[3].strip() if len(cells) > 3 else '-'
            report_raw = cells[4].strip() if len(cells) > 4 else '-'
            report_path = extract_link_text(report_raw) if report_raw != '-' else '-'

            existing = next((e for e in entries if e.ip == ip), None)
            if existing:
                if service not in existing.service:
                    existing.service += f',{service}'
                if existing.status == 'UNVERIFIED' and status != 'UNVERIFIED':
                    existing.status = status
                continue

            entries.append(IPEntry(
                ip=ip, status=status, cluster=cluster,
                infra=infra, report_path=report_path, service=service
            ))

    return entries


def get_ips_by_status(status: str) -> list[IPEntry]:
    return [e for e in parse_index() if e.status == status]


def get_unverified_ips(service: str | None = None) -> list[str]:
    entries = parse_seed_ips()
    result = []
    seen = set()
    for e in entries:
        if e.status == 'UNVERIFIED' and e.ip not in seen:
            if service is None or service in e.service:
                result.append(e.ip)
                seen.add(e.ip)
    return result


# ── 보고서 파일에서 신뢰도/클러스터 읽기 ──────────────────────────────────────

def read_report_confidence(report_rel_path: str) -> tuple[str, str]:
    """
    investigation 보고서 파일에서 신뢰도·클러스터 읽기.
    반환: (confidence, cluster)
    """
    if not report_rel_path or report_rel_path == '-':
        return 'UNVERIFIED', '-'

    abs_path = INVESTIGATIONS / report_rel_path
    if not abs_path.exists():
        return 'UNVERIFIED', '-'

    text = abs_path.read_text(encoding='utf-8')
    conf_m = re.search(r'\*\*신뢰도:\*\*\s*(HIGH|MEDIUM|LOW|UNVERIFIED)', text)
    clus_m = re.search(r'\*\*클러스터:\*\*\s*(Cluster#\d+[^\n]*|미분류)', text)
    confidence = conf_m.group(1) if conf_m else 'UNVERIFIED'
    cluster = clus_m.group(1).strip() if clus_m else '-'
    return confidence, cluster


def read_report_lifecycle(report_rel_path: str) -> dict:
    """
    조사 보고서에서 수명 관리 필드 파싱.
    반환 키: last_seen (date|None), first_seen (date|None), last_verified (date|None),
            ttl_days (int|None), lifecycle_state (str|None)
    """
    empty = {
        'last_seen': None, 'first_seen': None, 'last_verified': None,
        'ttl_days': None, 'lifecycle_state': None,
    }
    if not report_rel_path or report_rel_path == '-':
        return empty

    abs_path = INVESTIGATIONS / report_rel_path
    if not abs_path.exists():
        return empty

    text = abs_path.read_text(encoding='utf-8')

    def parse_date(label: str):
        m = re.search(rf'\*\*{label}:\*\*\s*(\d{{4}}-\d{{2}}-\d{{2}})', text)
        if not m:
            return None
        try:
            return datetime.strptime(m.group(1), '%Y-%m-%d').date()
        except ValueError:
            return None

    ttl_m = re.search(r'\*\*ttl_days:\*\*\s*(\d+)', text)
    ttl = int(ttl_m.group(1)) if ttl_m else None

    state_m = re.search(
        r'\*\*lifecycle_state:\*\*\s*(ACTIVE|STALE|RETIRED|UNVERIFIED)',
        text,
    )
    state = state_m.group(1) if state_m else None

    return {
        'first_seen': parse_date('first_seen'),
        'last_seen': parse_date('last_seen'),
        'last_verified': parse_date('last_verified'),
        'ttl_days': ttl,
        'lifecycle_state': state,
    }


def default_ttl_days_for_infra(infra: str) -> int:
    """인프라 유형 문자열에서 기본 TTL(일)."""
    u = (infra or '').upper()
    if 'VPS' in u or 'VULTR' in u or 'DATACENTER' in u:
        return 30
    if 'MOBILE' in u or 'KR_MOBILE' in u:
        return 60
    return 90


def blocklist_entry_expired(
    last_seen: date | None,
    ttl_days: int,
    today: date,
) -> bool:
    """last_seen + ttl < today 이면 블록리스트에서 제외."""
    if last_seen is None or ttl_days <= 0:
        return False
    return last_seen + timedelta(days=ttl_days) < today


PIVOT_QUEUE = ROOT / 'data' / 'pivot_queue.md'


def append_pivot_queue(ips: list[str], source: str, note: str = '') -> list[str]:
    """
    pivot_queue.md에 아직 없는 IP만 추가. 반환: 실제 추가된 IP.
    """
    if not ips:
        return []
    PIVOT_QUEUE.parent.mkdir(parents=True, exist_ok=True)
    existing: set[str] = set()
    if PIVOT_QUEUE.exists():
        for m in re.finditer(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b', PIVOT_QUEUE.read_text()):
            existing.add(m.group(1))

    for e in parse_index():
        existing.add(e.ip)

    new_ips = [ip for ip in ips if ip not in existing]
    if not new_ips:
        return []

    if not PIVOT_QUEUE.exists():
        header = (
            '# 피벗 대기열 (Pivot queue)\n\n'
            '> 자동 조사·스크래핑에서 발견했으나 INDEX seed에 없는 IP. '
            '`investigations/TEMPLATE.md`로 보고서 작성 후 INDEX 반영.\n\n'
            '| IP | 출처 | 추가일 | 비고 |\n'
            '|---|---|---|---|\n'
        )
        PIVOT_QUEUE.write_text(header, encoding='utf-8')

    today = date.today().isoformat()
    lines = []
    for ip in new_ips:
        lines.append(f'| {ip} | {source} | {today} | {note} |\n')

    with PIVOT_QUEUE.open('a', encoding='utf-8') as f:
        f.writelines(lines)
    return new_ips


TIER1_LOG_DIR = ROOT / 'data' / 'tier1_logs'
TIER2_QUEUE = ROOT / 'data' / 'tier2_queue.md'


def write_tier1_scan_json(ip: str, payload: dict) -> Path:
    """
    티어 1(DDG site: 피해 도메인) 스캔 결과를 JSON으로 저장.
    파일명: YYYY-MM-DD_{ip_underscores}.json (같은 날·같은 IP는 덮어씀)
    """
    TIER1_LOG_DIR.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    safe = ip.replace('.', '_')
    path = TIER1_LOG_DIR / f'{today}_{safe}.json'
    out = {'saved_at': datetime.now(timezone.utc).isoformat(), **payload}
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    return path


def _tier2_sanitize_cell(s: str) -> str:
    return (s or '').replace('|', '｜').replace('\n', ' ').strip()


TIER2_QUEUE_HEADER = (
    '# 티어 2 후속 조사 큐 (Tier-2 follow-up)\n\n'
    '> 티어 1 (`site:피해사이트 "{IP}"`)에서 신호가 나온 뒤 **브라우저·본문 확인**용. '
    '`METHODOLOGY.md` §2.4. 처리 후 행 삭제 또는 완료 표시.\n\n'
    '| IP | 우선순위 | 트리거 | 히트 도메인(DDG n) | 스니펫 키워드 | 권장 조치 | 추가일 | 비고 |\n'
    '|---|---|---|---|---|---|---|---|\n'
)


def _tier2_queue_row_exists_today(text: str, ip: str, today: str) -> bool:
    """추가일 열: 신규 8열 테이블에서 인덱스 6, 구형 6열은 인덱스 4."""
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith('|') or line.startswith('|---'):
            continue
        parts = [p.strip() for p in line.strip('|').split('|')]
        if len(parts) < 5 or parts[0] == 'IP':
            continue
        if parts[0] != ip:
            continue
        row_date = parts[6] if len(parts) >= 8 else parts[4]
        if row_date == today:
            return True
    return False


def _tier2_priority_and_recommendation(
    with_hits: list[tuple[str, int]],
    ddg_site_kw: dict,
) -> tuple[int, str]:
    """
    우선순위 1–10 (높을수록 먼저 볼 것): 히트 도메인 수·스니펫 키워드 가중.
    권장 조치: 상위 히트 도메인의 sample_href 또는 DDG 재검색 힌트.
    """
    keywords = ddg_site_kw.get('keywords') or []
    fraud_in_snippet = any(
        p.get('n_results', 0) > 0 and p.get('fraud_keywords')
        for p in (ddg_site_kw.get('per_domain') or [])
    )
    n = len(with_hits)
    score = min(10, n * 2 + (2 if keywords else 0) + (1 if fraud_in_snippet else 0))
    score = max(1, score)

    pmap = {p.get('domain'): p for p in (ddg_site_kw.get('per_domain') or [])}
    rec_parts: list[str] = []
    ip_for_hint = _tier2_sanitize_cell(ddg_site_kw.get('_pivot_ip', ''))
    for dom, _cnt in with_hits[:4]:
        p = pmap.get(dom) or {}
        hrefs = p.get('sample_hrefs') or []
        u = (hrefs[0] or '').strip() if hrefs else ''
        if u:
            rec_parts.append(f'{dom}: {u[:100]}')
        elif ip_for_hint:
            rec_parts.append(f'{dom}: DDG `site:{dom} "{ip_for_hint}"`')
        else:
            rec_parts.append(f'{dom}: DDG site: 재검색')
    rec = ' / '.join(rec_parts) if rec_parts else '브라우저로 피해 사이트 게시판 검색'
    return score, rec


def compute_tier2_followup_row(
    ip: str,
    ddg_site_kw: dict,
    *,
    min_hit_domains: int = 2,
    also_single_domain_fraud_snippet: bool = False,
    today: str | None = None,
    note: str = 'investigate_ip.py 자동',
) -> tuple[str, str, dict] | None:
    """
    트리거 시 (마크다운 행, 요약, meta) 반환. meta: priority, trigger, recommend, dom_summary, …
    미트리거면 None. ddg_site_kw에 `_pivot_ip`를 넣으면 권장 조치에 DDG 쿼리 힌트에 사용.
    """
    kw = dict(ddg_site_kw)
    if '_pivot_ip' not in kw:
        kw['_pivot_ip'] = ip

    hits = kw.get('hits') or {}
    checked = kw.get('domains_checked') or []
    with_hits = [(d, hits[d]) for d in checked if hits.get(d, 0) > 0]

    fraud_in_snippet = any(
        p.get('n_results', 0) > 0 and p.get('fraud_keywords')
        for p in (kw.get('per_domain') or [])
    )

    if len(with_hits) >= min_hit_domains:
        trigger = f'히트도메인≥{min_hit_domains}'
    elif also_single_domain_fraud_snippet and fraud_in_snippet and len(with_hits) >= 1:
        trigger = '단일도메인+스니펫사기키워드'
    else:
        return None

    today = today or date.today().isoformat()
    dom_part = ', '.join(f'{d}({n})' for d, n in with_hits[:12])
    if len(with_hits) > 12:
        dom_part += ' …'
    kws = ', '.join(kw.get('keywords') or []) or '-'
    priority, recommend = _tier2_priority_and_recommendation(with_hits, kw)

    row = (
        f'| {_tier2_sanitize_cell(ip)} | {priority} | {_tier2_sanitize_cell(trigger)} | '
        f'{_tier2_sanitize_cell(dom_part)} | {_tier2_sanitize_cell(kws)} | '
        f'{_tier2_sanitize_cell(recommend)} | {today} | {_tier2_sanitize_cell(note)} |\n'
    )
    short = dom_part if len(dom_part) <= 80 else dom_part[:77] + '...'
    summary = f'{ip}: P{priority} {trigger} ({short})'
    meta = {
        'priority': priority,
        'trigger': trigger,
        'recommend': recommend,
        'dom_summary': dom_part,
        'snippet_keywords': kws,
        'n_hit_domains': len(with_hits),
    }
    return row, summary, meta


def _tier2_tuple_from_embedded(
    ip: str,
    t2: dict,
    *,
    today: str | None = None,
    note: str = 'tier1_logs tier2_default',
) -> tuple[str, str, dict] | None:
    """tier1 JSON의 tier2_default(eligible=True)로 (row, summary, meta) 재구성. 필수 필드 없으면 None."""
    if not t2.get('eligible'):
        return None
    trigger = (t2.get('trigger') or '').strip()
    if not trigger:
        return None
    if t2.get('priority') is None:
        return None
    priority = t2['priority']
    today = today or date.today().isoformat()
    dom_part = (t2.get('dom_summary') or '-').strip() or '-'
    kws = (t2.get('snippet_keywords') or '-').strip() or '-'
    recommend = (t2.get('recommend') or '').strip() or '-'
    row = (
        f'| {_tier2_sanitize_cell(ip)} | {priority} | {_tier2_sanitize_cell(trigger)} | '
        f'{_tier2_sanitize_cell(dom_part)} | {_tier2_sanitize_cell(kws)} | '
        f'{_tier2_sanitize_cell(recommend)} | {today} | {_tier2_sanitize_cell(note)} |\n'
    )
    summary = (t2.get('summary') or '').strip()
    if not summary:
        short = dom_part if len(dom_part) <= 80 else dom_part[:77] + '...'
        summary = f'{ip}: P{priority} {trigger} ({short})'
    meta = {
        'priority': priority,
        'trigger': trigger,
        'recommend': recommend,
        'dom_summary': dom_part,
        'snippet_keywords': kws,
        'n_hit_domains': t2.get('n_hit_domains'),
    }
    return row, summary, meta


def tier2_followup_for_tier1_record_with_source(
    rec: dict,
    ip: str,
    ddg_site_kw: dict,
    *,
    min_hit_domains: int = 2,
    also_single_domain_fraud_snippet: bool = False,
) -> tuple[tuple[str, str, dict], Literal['embed', 'compute']] | None:
    """
    tier1_logs JSON 한 건: ((row, summary, meta), 출처).
    eligible=False 는 즉시 None. eligible=True 이면 임베드 우선, 부족 시 compute.
    """
    t2 = rec.get('tier2_default')
    if isinstance(t2, dict) and 'eligible' in t2:
        if not t2.get('eligible'):
            return None
        emb = _tier2_tuple_from_embedded(ip, t2)
        if emb is not None:
            return emb, 'embed'
    comp = compute_tier2_followup_row(
        ip,
        ddg_site_kw,
        min_hit_domains=min_hit_domains,
        also_single_domain_fraud_snippet=also_single_domain_fraud_snippet,
    )
    if not comp:
        return None
    return comp, 'compute'


def tier2_followup_for_tier1_record(
    rec: dict,
    ip: str,
    ddg_site_kw: dict,
    *,
    min_hit_domains: int = 2,
    also_single_domain_fraud_snippet: bool = False,
) -> tuple[str, str, dict] | None:
    """
    tier1_logs JSON 한 건에 대해 (row, summary, meta).
    tier2_default가 있으면 eligible=False 는 즉시 None(재계산 안 함).
    eligible=True 이면 임베드 필드로 행 구성(compute 생략); 필드 부족 시 compute 폴백.
    tier2_default 없으면 compute만 사용.
    """
    r = tier2_followup_for_tier1_record_with_source(
        rec,
        ip,
        ddg_site_kw,
        min_hit_domains=min_hit_domains,
        also_single_domain_fraud_snippet=also_single_domain_fraud_snippet,
    )
    return r[0] if r else None


def tier2_csv_sidecar_for_record(
    rec: dict,
    *,
    min_hit_domains: int = 2,
    also_single_domain_fraud_snippet: bool = False,
    ignore_embedded: bool = False,
) -> tuple[str, str, str, str, str]:
    """
    export_tier1_logs 티어2 열 5튜플 (eligible, priority, trigger, recommend, summary).
    tier2_default와 suggest/export_compute 경로를 맞춤: eligible False 즉시 no; eligible True
    인데 임베드 필드 부족 시 compute 폴백. ignore_embedded True면 항상 compute.
    """
    ip = (rec.get('ip') or '').strip()
    if not ignore_embedded:
        t2 = rec.get('tier2_default')
        if isinstance(t2, dict) and 'eligible' in t2:
            if not t2.get('eligible'):
                return ('no', '', '', '', '')
            emb = _tier2_tuple_from_embedded(ip, t2)
            if emb is not None:
                _row, summary, meta = emb
                rec_text = (meta.get('recommend') or '')[:400]
                return (
                    'yes',
                    str(meta.get('priority', '')),
                    meta.get('trigger', '') or '',
                    rec_text,
                    summary,
                )
    if not ip:
        return ('', '', '', '', '')
    ddg = dict(rec.get('ddg_site') or {})
    ddg['_pivot_ip'] = ip
    comp = compute_tier2_followup_row(
        ip,
        ddg,
        min_hit_domains=min_hit_domains,
        also_single_domain_fraud_snippet=also_single_domain_fraud_snippet,
    )
    if not comp:
        return ('no', '', '', '', '')
    _row, summary, meta = comp
    rec_text = (meta.get('recommend') or '')[:400]
    return (
        'yes',
        str(meta.get('priority', '')),
        meta.get('trigger', '') or '',
        rec_text,
        summary,
    )


def append_tier2_followup_queue(
    ip: str,
    ddg_site_kw: dict,
    *,
    min_hit_domains: int = 2,
    also_single_domain_fraud_snippet: bool = False,
    precomputed: tuple[str, str, dict] | None = None,
    assume_ineligible: bool = False,
) -> str | None:
    """
    METHODOLOGY §2.4: 티어 1 신호가 나면 티어 2(본문·브라우저) 후속 큐에 한 줄 추가.

    트리거:
      - DDG 검색결과>0 인 피해 도메인 개수 >= min_hit_domains (기본 2)
      - 또는 also_single_domain_fraud_snippet 이고, 결과>0 인 도메인 중 하나라도
        스니펫에 사기 키워드가 잡힌 경우

    precomputed가 있으면 compute_tier2_followup_row를 호출하지 않고 해당 (row, summary, meta) 사용.
    assume_ineligible True면 큐를 읽지도·계산하지도 않고 None (investigate_ip에서 이미 판정한 경우).

    같은 IP·같은 날짜 행이 이미 있으면 생략. 반환: 추가 요약 문자열 또는 None.
    """
    if assume_ineligible:
        return None
    today = date.today().isoformat()
    TIER2_QUEUE.parent.mkdir(parents=True, exist_ok=True)
    existing = TIER2_QUEUE.read_text(encoding='utf-8') if TIER2_QUEUE.exists() else ''
    if _tier2_queue_row_exists_today(existing, ip, today):
        return None

    if precomputed is not None:
        row, summary, _meta = precomputed
        if not row.endswith('\n'):
            row = row + '\n'
    else:
        computed = compute_tier2_followup_row(
            ip,
            ddg_site_kw,
            min_hit_domains=min_hit_domains,
            also_single_domain_fraud_snippet=also_single_domain_fraud_snippet,
            today=today,
        )
        if not computed:
            return None
        row, summary, _meta = computed

    if not TIER2_QUEUE.exists():
        TIER2_QUEUE.write_text(TIER2_QUEUE_HEADER, encoding='utf-8')

    with TIER2_QUEUE.open('a', encoding='utf-8') as f:
        f.write(row)

    return summary


# ── ioc_registry.md 파싱 ─────────────────────────────────────────────────────

def parse_telegram_iocs() -> list[TelegramIOC]:
    if not IOC_REGISTRY.exists():
        return []

    text = IOC_REGISTRY.read_text(encoding='utf-8')
    rows = parse_md_table_rows(text, '## 텔레그램 핸들')
    iocs = []
    for cells in rows:
        if len(cells) < 6:
            continue
        handle = cells[0].strip()
        if not handle.startswith('@'):
            continue
        iocs.append(TelegramIOC(
            handle=handle,
            brand=cells[1].strip(),
            source_ip=cells[2].strip(),
            found_date=cells[3].strip(),
            pivot_status=normalize_status(cells[4]),
            cluster=cells[5].strip(),
            note=cells[6].strip() if len(cells) > 6 else '',
        ))
    return iocs


def parse_domain_iocs() -> list[DomainIOC]:
    if not IOC_REGISTRY.exists():
        return []

    text = IOC_REGISTRY.read_text(encoding='utf-8')
    rows = parse_md_table_rows(text, '## 도메인/URL')
    iocs = []
    for cells in rows:
        if len(cells) < 5:
            continue
        domain = cells[0].strip()
        if not domain or domain == '-':
            continue
        iocs.append(DomainIOC(
            domain=domain,
            ioc_type=cells[1].strip(),
            linked_handle=cells[2].strip(),
            found_date=cells[3].strip(),
            pivot_status=normalize_status(cells[4]),
            cluster=cells[5].strip() if len(cells) > 5 else '-',
            note=cells[6].strip() if len(cells) > 6 else '',
        ))
    return iocs


def parse_brand_names() -> list[str]:
    """브랜드명 목록 반환"""
    if not IOC_REGISTRY.exists():
        return []

    text = IOC_REGISTRY.read_text(encoding='utf-8')
    rows = parse_md_table_rows(text, '## 브랜드명')
    return [cells[0].strip() for cells in rows if cells and cells[0].strip() not in ('-', '')]


# ── spammed_sites.md 파싱 ─────────────────────────────────────────────────────

def parse_spammed_sites() -> list[dict]:
    if not SPAMMED_SITES.exists():
        return []

    text = SPAMMED_SITES.read_text(encoding='utf-8')
    rows = parse_md_table_rows(text, '## 확인된 피해 사이트')
    sites = []
    for cells in rows:
        if len(cells) < 2:
            continue
        scraper = cells[7].strip() if len(cells) > 7 else ''
        sites.append({
            'name': cells[0].strip(),
            'url': cells[1].strip() if len(cells) > 1 else '',
            'type': cells[2].strip() if len(cells) > 2 else '',
            'found_ip': cells[3].strip() if len(cells) > 3 else '',
            'ioc_path': cells[4].strip() if len(cells) > 4 else '',
            'scraper_type': scraper,
        })
    return sites


# ── ioc_registry.md 자동 등록 ────────────────────────────────────────────────

def get_known_telegram_handles() -> dict[str, str]:
    """등록된 텔레그램 핸들 → 클러스터 매핑 반환"""
    return {t.handle: t.cluster for t in parse_telegram_iocs()}


def get_known_domains() -> set[str]:
    return {d.domain for d in parse_domain_iocs()}


def register_new_telegrams(handles: list[str], source_ip: str, found_date: str) -> list[str]:
    """
    ioc_registry.md에 없는 새 텔레그램 핸들을 UNVERIFIED로 자동 등록.
    반환: 실제로 추가된 핸들 목록
    """
    if not IOC_REGISTRY.exists() or not handles:
        return []

    known = get_known_telegram_handles()
    new_handles = [h for h in handles if h not in known]
    if not new_handles:
        return []

    text = IOC_REGISTRY.read_text(encoding='utf-8')
    # 텔레그램 핸들 섹션의 마지막 행 뒤에 삽입
    section_end = text.find('\n---', text.find('## 텔레그램 핸들'))
    if section_end == -1:
        return []

    new_rows = ''
    for h in new_handles:
        new_rows += f'| {h} | - | {source_ip} | {found_date} | UNVERIFIED | - | 자동 등록 |\n'

    text = text[:section_end] + '\n' + new_rows + text[section_end:]
    IOC_REGISTRY.write_text(text, encoding='utf-8')
    return new_handles


def register_new_domains(domains: list[str], source_ip: str, found_date: str) -> list[str]:
    """ioc_registry.md에 없는 새 도메인을 UNVERIFIED로 자동 등록."""
    if not IOC_REGISTRY.exists() or not domains:
        return []

    known = get_known_domains()
    new_domains = [d for d in domains if d not in known]
    if not new_domains:
        return []

    text = IOC_REGISTRY.read_text(encoding='utf-8')
    section_end = text.find('\n---', text.find('## 도메인/URL'))
    if section_end == -1:
        return []

    new_rows = ''
    for d in new_domains:
        itype = '홍보 사이트' if 'isweb' in d else '기타'
        new_rows += f'| {d} | {itype} | - | {found_date} | UNVERIFIED | - | 자동 등록 ({source_ip}) |\n'

    text = text[:section_end] + '\n' + new_rows + text[section_end:]
    IOC_REGISTRY.write_text(text, encoding='utf-8')
    return new_domains


# ── 클러스터 자동 귀속 ────────────────────────────────────────────────────────

def infer_cluster(found_iocs: list[str]) -> str:
    """
    발견된 IOC 목록으로 클러스터 추정.
    반환: 'Cluster#N 추정' 또는 '미분류'
    """
    known_tg = get_known_telegram_handles()
    known_domains = {d.domain: d.cluster for d in parse_domain_iocs()}
    cluster_votes: dict[str, int] = {}
    for ioc in found_iocs:
        cluster = known_tg.get(ioc, '') or known_domains.get(ioc, '')
        if cluster and cluster not in ('-', '미분류', ''):
            # "Cluster#1 추정" → "Cluster#1" 정규화
            base = re.sub(r'\s*추정.*', '', cluster).strip()
            cluster_votes[base] = cluster_votes.get(base, 0) + 1

    if not cluster_votes:
        return '미분류'
    best = max(cluster_votes, key=lambda k: cluster_votes[k])
    if cluster_votes[best] >= 2:
        return best
    return f'{best} 추정'


# ── INDEX.md 업데이트 ─────────────────────────────────────────────────────────

def update_index_ip(ip: str, status: str, report_rel_path: str = ''):
    """INDEX.md에서 특정 IP의 상태·보고서 경로 업데이트 (안전한 행 단위 처리)"""
    if not INDEX_MD.exists():
        return False

    lines = INDEX_MD.read_text(encoding='utf-8').splitlines(keepends=True)
    updated = False

    for i, line in enumerate(lines):
        if not line.strip().startswith('|'):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if not cells or cells[0] != ip:
            continue

        # 상태 업데이트 (2번째 컬럼)
        if len(cells) >= 2:
            cells[1] = status

        # 보고서 경로 업데이트 (마지막 컬럼)
        if report_rel_path and len(cells) >= 5:
            cells[-1] = f'[보고서]({report_rel_path})'

        # 원래 줄 너비 맞춰서 재구성 (간단히 파이프 구분)
        lines[i] = '| ' + ' | '.join(cells) + ' |\n'
        updated = True
        break

    if updated:
        INDEX_MD.write_text(''.join(lines), encoding='utf-8')

    return updated
