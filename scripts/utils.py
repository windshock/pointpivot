"""
utils.py - PointPivot 마크다운 파싱 공통 유틸리티
"""

import re
from pathlib import Path
from dataclasses import dataclass, field

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
            report_raw = cells[4].strip() if len(cells) > 4 else '-'
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
        sites.append({
            'name': cells[0].strip(),
            'url': cells[1].strip() if len(cells) > 1 else '',
            'type': cells[2].strip() if len(cells) > 2 else '',
            'found_ip': cells[3].strip() if len(cells) > 3 else '',
            'ioc_path': cells[4].strip() if len(cells) > 4 else '',
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
            cells[4] = f'[보고서]({report_rel_path})'

        # 원래 줄 너비 맞춰서 재구성 (간단히 파이프 구분)
        lines[i] = '| ' + ' | '.join(cells) + ' |\n'
        updated = True
        break

    if updated:
        INDEX_MD.write_text(''.join(lines), encoding='utf-8')

    return updated
