"""
E2E: verify each page loads internal CSS/JS assets successfully (HTTP 200).
External CDNs (e.g., Vue on unpkg) are intentionally ignored.
"""

import re
from urllib.parse import urljoin

import pytest
import requests
from bs4 import BeautifulSoup

PAGES = [
    "/",  # homepage
    "/connect-plus-plus",
    "/connect-display",
    "/connect-manager",
    "/fleet-data-manager",
    "/fleet-config-manager",
    "/fleet-software-manager",
    "/fleet-workshop-manager",
    "/fsm-modular",
]


def _extract_internal_assets(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    assets: list[str] = []

    # Stylesheets
    for link in soup.find_all("link", rel=lambda v: v and "stylesheet" in v):
        href = link.get("href")
        if not href:
            continue
        # skip data URLs and external CDNs
        if href.startswith("data:") or href.startswith("http://") or href.startswith("https://"):
            continue
        if href.startswith("/"):
            assets.append(href)

    # Scripts
    for script in soup.find_all("script"):
        src = script.get("src")
        if not src:
            continue
        if src.startswith("data:") or src.startswith("http://") or src.startswith("https://"):
            continue
        if src.startswith("/"):
            assets.append(src)

    # Deduplicate
    return sorted(set(assets))


@pytest.mark.parametrize("path", PAGES)
def test_internal_assets_return_200(base_url: str, path: str):
    resp = requests.get(urljoin(base_url, path), timeout=10)
    assert resp.status_code == 200, f"Page {path} did not load (status {resp.status_code})"

    assets = _extract_internal_assets(resp.text)
    # The page may be minimal, but if it declares internal assets, they must load
    for asset in assets:
        url = urljoin(base_url, asset)
        r = requests.get(url, timeout=10)
        assert r.status_code == 200, f"Asset failed: {asset} on page {path} (status {r.status_code})"
        ctype = r.headers.get("content-type", "").lower()
        # Accept common content types for CSS/JS
        assert any(k in ctype for k in ("css", "javascript", "ecmascript")), (
            f"Unexpected content-type for {asset}: {ctype}"
        )


@pytest.mark.parametrize("path", PAGES)
def test_no_vue_dev_build_in_pages(base_url: str, path: str):
    resp = requests.get(urljoin(base_url, path), timeout=10)
    assert resp.status_code == 200
    html = resp.text
    # Ensure we don't reference the dev build anywhere
    assert "vue.global.js" not in html, f"Dev Vue build referenced on {path}"
