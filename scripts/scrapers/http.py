"""HTTP fetch: curl 우선, curl_cffi 폴백."""

from __future__ import annotations

import subprocess
import warnings

warnings.filterwarnings('ignore')

try:
    from curl_cffi import requests as cffi_req
    CFFI_AVAILABLE = True
except ImportError:
    CFFI_AVAILABLE = False

_session = None


def cffi_enabled() -> bool:
    return CFFI_AVAILABLE


def get_session():
    global _session
    if CFFI_AVAILABLE and _session is None:
        _session = cffi_req.Session(impersonate='chrome', verify=False)
    return _session


def fetch(url: str, timeout: int = 30) -> str | None:
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
        print(f'  [fetch 오류:curl] {url[:60]}: {e}')

    s = get_session()
    if s is not None:
        try:
            r = s.get(url, timeout=timeout)
            if r.status_code == 200 and r.text:
                return r.text
        except Exception as e:
            print(f'  [fetch 오류:cffi] {url[:60]}: {e}')

    return None
