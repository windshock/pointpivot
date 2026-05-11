"""Shared helpers for optional proxy collection and SearXNG export."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ProxyRecord = dict[str, Any]

SCRIPTS = Path(__file__).resolve().parents[1]
ROOT = SCRIPTS.parent
CONFIG_DIR = ROOT / 'config'
DATA_DIR = ROOT / 'data'

DEFAULT_PROXY_CANDIDATES_PATH = CONFIG_DIR / 'proxy_candidates.json'
DEFAULT_LIVE_PROXY_PATH = CONFIG_DIR / 'live_proxies.yml'
DEFAULT_SEARXNG_PROXY_EXPORT_PATH = CONFIG_DIR / 'searxng_proxies.generated.yml'
DEFAULT_PROXY_SOURCES_PATH = CONFIG_DIR / 'proxy_sources.yml'
DEFAULT_PROXY_VALIDATION_LOG_DIR = DATA_DIR / 'proxy_validation_logs'

ALLOWED_PROTOCOLS = {'http', 'https', 'socks4', 'socks5'}
PROXY_MODE_ENV = 'POINTPIVOT_PROXY_MODE'
PROXY_INVENTORY_ENV = 'POINTPIVOT_PROXY_INVENTORY'


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def require_yaml():
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError(
            'PyYAML is required for proxy YAML files; run '
            '.venv/bin/python -m pip install -r scripts/requirements.txt'
        ) from exc
    return yaml


def _strip_proxy_token(raw: str) -> str:
    stripped = raw.strip()
    if not stripped or stripped.startswith('#'):
        return ''
    return stripped.split()[0]


def normalize_proxy_url(
    raw: str,
    *,
    default_protocol: str | None = 'http',
) -> tuple[str, str]:
    """Normalize a proxy URL or host:port token and return (url, protocol)."""

    token = _strip_proxy_token(raw)
    if not token:
        raise ValueError('empty proxy entry')

    candidate = token
    if '://' not in candidate:
        protocol = (default_protocol or 'http').strip().lower()
        candidate = f'{protocol}://{candidate}'

    parsed = urlparse(candidate)
    protocol = parsed.scheme.lower()
    if protocol not in ALLOWED_PROTOCOLS:
        raise ValueError(f'unsupported proxy protocol: {protocol or "(missing)"}')
    if parsed.username or parsed.password:
        raise ValueError('proxy credentials are not allowed')

    host = parsed.hostname
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError('invalid proxy port') from exc

    if not host or port is None:
        raise ValueError('proxy must include host and port')
    if port < 1 or port > 65535:
        raise ValueError('proxy port out of range')

    return f'{protocol}://{host.lower()}:{port}', protocol


def normalize_proxy_record(
    raw: str,
    *,
    source: str,
    source_url: str,
    default_protocol: str | None = 'http',
    collected_at: str | None = None,
) -> ProxyRecord:
    url, protocol = normalize_proxy_url(raw, default_protocol=default_protocol)
    return {
        'url': url,
        'protocol': protocol,
        'source': source,
        'source_url': source_url,
        'collected_at': collected_at or utc_now_iso(),
    }


def dedupe_proxy_records(records: list[ProxyRecord]) -> list[ProxyRecord]:
    seen: set[str] = set()
    deduped: list[ProxyRecord] = []
    for record in records:
        url = str(record.get('url') or '').strip()
        if not url or url in seen:
            continue
        seen.add(url)
        deduped.append(record)
    return deduped


def read_candidate_records(path: Path) -> list[ProxyRecord]:
    payload = json.loads(path.read_text(encoding='utf-8'))
    if isinstance(payload, list):
        return [r for r in payload if isinstance(r, dict)]
    if isinstance(payload, dict):
        proxies = payload.get('proxies') or payload.get('records') or []
        if isinstance(proxies, list):
            return [r for r in proxies if isinstance(r, dict)]
    raise ValueError(f'{path} does not contain proxy records')


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )


def read_yaml(path: Path) -> Any:
    yaml = require_yaml()
    return yaml.safe_load(path.read_text(encoding='utf-8'))


def write_yaml(path: Path, payload: Any) -> None:
    yaml = require_yaml()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
        encoding='utf-8',
    )


def read_live_inventory(path: Path) -> dict:
    payload = read_yaml(path)
    if isinstance(payload, list):
        return {'proxies': payload}
    if isinstance(payload, dict):
        return payload
    raise ValueError(f'{path} does not contain a proxy inventory')


def live_proxy_records(path: Path) -> list[ProxyRecord]:
    inventory = read_live_inventory(path)
    proxies = inventory.get('proxies') or []
    if not isinstance(proxies, list):
        raise ValueError(f'{path} inventory proxies field must be a list')
    return [p for p in proxies if isinstance(p, dict)]


def proxy_inventory_summary(path: Path) -> dict:
    inventory = read_live_inventory(path)
    proxies = [
        p
        for p in inventory.get('proxies', [])
        if isinstance(p, dict) and p.get('validated') is True
    ]
    sources = sorted({str(p.get('source') or 'unknown') for p in proxies})
    return {
        'proxy_source': ','.join(sources) if sources else '',
        'proxy_inventory_generated_at': inventory.get('generated_at', ''),
        'proxy_count': len(proxies),
    }


def proxy_provenance_from_env(stderr=sys.stderr) -> dict:
    """Return non-sensitive proxy inventory metadata when explicitly enabled."""

    mode = os.environ.get(PROXY_MODE_ENV, '').strip()
    if not mode:
        return {}
    if mode != 'searxng_outgoing':
        print(
            f'[proxy] unsupported {PROXY_MODE_ENV}={mode!r}; '
            'expected searxng_outgoing',
            file=stderr,
        )
        return {}

    inventory_path = Path(
        os.environ.get(PROXY_INVENTORY_ENV, str(DEFAULT_LIVE_PROXY_PATH))
    )
    try:
        summary = proxy_inventory_summary(inventory_path)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f'[proxy] cannot read proxy inventory metadata: {exc}', file=stderr)
        return {}

    if not summary.get('proxy_count'):
        print(f'[proxy] proxy inventory has no validated proxies: {inventory_path}', file=stderr)
        return {}

    return {'proxy_mode': mode, **summary}
