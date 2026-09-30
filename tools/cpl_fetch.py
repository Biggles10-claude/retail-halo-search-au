#!/usr/bin/env python3
"""CPL enrichment for GitHub Actions via StaticICE.

Direct cplonline.com.au is CF hard-blocked on cloud/datacenter IPs.
"""
from __future__ import annotations

import json, os, re, sys, time, urllib.parse, urllib.request
from pathlib import Path

QUERIES = [
    "Ryzen AI Max+ 395", "Ryzen AI Max", "Framework Desktop", "DGX Spark",
    "GMKtec", "Minisforum", "Beelink", "strix halo", "Gorgon", "Corsair WS",
    "ASUS ROG Flow Z13", "HP ZBook Ultra", "ASUS Ascent GX10",
]

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
    results["ok"] = len(dedup) > 0
    (out_dir / "cpl_suggest.json").write_text(json.dumps(results, indent=2))
    print("ok=", results["ok"], "products=", len(dedup), "direct=", results["direct_home_status"])
    return 0 if results["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
