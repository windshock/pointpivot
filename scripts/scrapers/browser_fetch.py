"""Headless 브라우저 fetch: Playwright 기반, egress MITM 인증서 환경 대응."""

from __future__ import annotations

import argparse
import os
import sys

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

DEFAULT_UA = (
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36'
)


def available() -> bool:
    return PLAYWRIGHT_AVAILABLE


def fetch(
    url: str,
    timeout: int = 25,
    wait_until: str = 'domcontentloaded',
    user_agent: str = DEFAULT_UA,
) -> tuple[int | None, str | None]:
    """URL을 headless 크로미움으로 열고 (status, html)을 돌려준다.

    egress gateway MITM CA를 신뢰하지 않는 Chromium NSS store 우회를 위해
    `ignore_https_errors=True`를 강제한다. PointPivot은 인증서 검증 자체를
    위협 지표로 쓰지 않으므로 안전한 트레이드오프.
    """
    if not PLAYWRIGHT_AVAILABLE:
        print('  [browser_fetch] playwright 미설치 — pip install playwright && playwright install chromium-headless-shell',
              file=sys.stderr)
        return None, None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            ctx = browser.new_context(
                ignore_https_errors=True,
                user_agent=user_agent,
                locale='ko-KR',
            )
            page = ctx.new_page()
            response = page.goto(url, timeout=timeout * 1000, wait_until=wait_until)
            html = page.content()
            status = response.status if response is not None else None
            return status, html
        finally:
            browser.close()


def main() -> int:
    parser = argparse.ArgumentParser(description='Playwright 기반 URL fetch.')
    parser.add_argument('url')
    parser.add_argument('--timeout', type=int, default=25)
    parser.add_argument('--wait-until', default='domcontentloaded',
                        choices=['load', 'domcontentloaded', 'networkidle', 'commit'])
    parser.add_argument('--status-only', action='store_true')
    parser.add_argument('--browsers-path', default=os.environ.get('PLAYWRIGHT_BROWSERS_PATH'),
                        help='기본은 환경변수 PLAYWRIGHT_BROWSERS_PATH. 예: /opt/pw-browsers')
    args = parser.parse_args()

    if args.browsers_path:
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = args.browsers_path

    status, html = fetch(args.url, timeout=args.timeout, wait_until=args.wait_until)
    if status is None:
        return 2
    print(f'status={status}', file=sys.stderr)
    if args.status_only:
        return 0 if 200 <= status < 400 else 1
    sys.stdout.write(html or '')
    return 0 if 200 <= status < 400 else 1


if __name__ == '__main__':
    raise SystemExit(main())
