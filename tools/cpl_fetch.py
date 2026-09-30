#!/usr/bin/env python3
"""CPL enrichment for GitHub Actions via StaticICE (Halo query pack).

Direct cplonline.com.au is CF hard-blocked on cloud/datacenter IPs.
stock=unknown → board_eligible False (NOTES only).
"""
from __future__ import annotations

import json, os, re, sys, time, urllib.parse, urllib.request
from pathlib import Path

QUERIES = [
    "GMKtec Evo-X2 128GB",
    "GMKtec EVO-X2",
    "GMKtec Gorgon",
    "Framework Desktop 128GB",
    "Framework Desktop AI Max",
    "Minisforum MS-S1 Max",
    "Minisforum AI Max",
    "Beelink GTi AI",
    "Beelink Strix Halo",
    "Ryzen AI Max+ 395",
    "Ryzen AI Max 395 128GB",
    "Strix Halo 128GB",
    "NVIDIA DGX Spark",
    "DGX Spark",
    "Gorgon Halo 192GB",
    "Gorgon Halo",
    "Corsair WS300",
    "ASUS Ascent GX10",
]

HALO_KEEP = re.compile(
    r"DGX\s*Spark|Gorgon\s*Halo|Strix\s*Halo|Evo-?X[0-9]|Framework\s*Desktop|"
    r"MS-?S1|MS-?A2|AI\s*Max\+?\s*(PRO\s*)?395|AI\s*Max\+?\s*(PRO\s*)?495|"
    r"WS300|Ascent\s*GX10|mini\s*PC|mini-?pc|workstation",
    re.I,
)
HALO_DROP = re.compile(
    r"\b(laptop|zbook|notebook|ultrabook|Flow\s*Z13|cable|DAC|QSFP|cooler|monitor|"
    r"headphones|PSU|power\s*supply)\b",
    re.I,
)

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


def fetch(url: str, timeout: int = 35) -> tuple[int, str]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "text/html,application/json,*/*",
            "Accept-Language": "en-AU,en;q=0.9",
            "Referer": "https://www.staticice.com.au/",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace") if e.fp else ""
        return e.code, body
    except Exception as e:
        return 0, f"{type(e).__name__}: {e}"


def _attr(attrs: str, name: str) -> str:
    m = re.search(rf'{name}=([\'"])(.*?)\1', attrs, re.I | re.S)
    if not m:
        return ""
    return m.group(2).replace("&amp;", "&").replace("&quot;", '"')


def _halo_ok(title: str) -> bool:
    if not title or HALO_DROP.search(title):
        return False
    return bool(HALO_KEEP.search(title))


def parse_staticice_cpl(html: str, query: str) -> list[dict]:
    out = []
    for m in re.finditer(r"<a\b([^>]+)>(.*?)</a>", html, re.I | re.S):
        attrs, inner = m.group(1), m.group(2)
        href = _attr(attrs, "href")
        if "redirect.cgi" not in href:
            continue
        if href.startswith("/"):
            href = "https://www.staticice.com.au" + href
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
        name = (qs.get("name") or [""])[0]
        newurl = urllib.parse.unquote((qs.get("newurl") or [""])[0])
        if "cplonline" not in newurl.lower() and "parts land" not in name.lower():
            continue
        path = urllib.parse.urlparse(newurl).path or "/"
        if path in ("/", ""):
            continue
        alt = _attr(attrs, "alt") or _attr(attrs, "title")
        title_m = re.search(r"latest price for\s+(.+?)(?:\.\.\.|$)", alt, re.I)
        title = (title_m.group(1).strip().rstrip(".") if title_m else "")[:240]
        if not _halo_ok(title or name):
            continue
        pm = re.search(r"\$\s*([0-9][0-9,]*(?:\.[0-9]{2})?)", inner)
        if not pm:
            continue
        price = float(pm.group(1).replace(",", ""))
        out.append({
            "retailer": "cplonline.com.au",
            "title": title or name,
            "price_aud": price,
            "url": newurl.split("?")[0],
            "stock": "unknown",
            "source": "cpl_staticice_gh",
            "query": query,
            "board_eligible": False,
        })
    seen, dedup = set(), []
    for o in out:
        if o["url"] in seen:
            continue
        seen.add(o["url"])
        dedup.append(o)
    return dedup


def main() -> int:
    out_dir = Path(os.environ.get("OUT_DIR", "out"))
    out_dir.mkdir(parents=True, exist_ok=True)
    results = {
        "ok": False,
        "direct_home_status": None,
        "direct_note": "cloud IPs typically CF403 Attention Required",
        "board_policy": "stock=unknown → NOTES only, never Artifacts board",
        "queries": {},
        "products": [],
        "error": None,
    }
    code, body = fetch("https://cplonline.com.au/")
    results["direct_home_status"] = code
    results["direct_home_snip"] = body[:180]

    products = []
    for q in QUERIES:
        url = (
            "https://www.staticice.com.au/cgi-bin/search.cgi?searcher=on&q="
            + urllib.parse.quote_plus(q)
        )
        code, html = fetch(url)
        rows = parse_staticice_cpl(html, q) if code == 200 else []
        results["queries"][q] = {"status": code, "cpl_hits": len(rows)}
        products.extend(rows)
        time.sleep(0.5)

    seen, dedup = set(), []
    for p in products:
        if p["url"] in seen:
            continue
        seen.add(p["url"])
        dedup.append(p)
    results["products"] = dedup
    results["ok"] = True  # successful StaticICE pass even if 0 halo hits
    results["halo_hits"] = len(dedup)
    (out_dir / "cpl_suggest.json").write_text(json.dumps(results, indent=2))
    print("ok=", results["ok"], "halo_products=", len(dedup), "direct=", results["direct_home_status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
