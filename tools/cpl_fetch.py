#!/usr/bin/env python3
"""Fetch CPL Magento suggest API from a GitHub Actions runner (non-CF-blocked egress).

Writes out/cpl_suggest.json. Intended for workflow_dispatch / schedule on
Biggles10-claude/retail-halo-search-au (or any repo with this workflow).
"""
from __future__ import annotations

import json, os, sys, time, urllib.parse, urllib.request
from pathlib import Path

QUERIES = [
    "Ryzen AI Max", "Ryzen AI Max+ 395", "Framework Desktop", "DGX Spark",
    "GMKtec", "Minisforum", "Beelink", "strix halo", "Gorgon", "Corsair WS",
    "ASUS ROG Flow Z13", "HP ZBook Ultra",
]

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


def fetch(url: str, timeout: int = 30) -> tuple[int, str]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "application/json,text/html,*/*",
            "Accept-Language": "en-AU,en;q=0.9",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://cplonline.com.au/",
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


def main() -> int:
    out_dir = Path(os.environ.get("OUT_DIR", "out"))
    out_dir.mkdir(parents=True, exist_ok=True)
    results = {"ok": False, "home_status": None, "queries": {}, "products": [], "error": None}
    code, body = fetch("https://cplonline.com.au/")
    results["home_status"] = code
    results["home_snip"] = body[:200]
    if code == 403 and ("Attention Required" in body or "just a moment" in body.lower()):
        results["error"] = "CF403_on_runner"
        (out_dir / "cpl_suggest.json").write_text(json.dumps(results, indent=2))
        print("CF403 on runner too", file=sys.stderr)
        return 2

    products = []
    for q in QUERIES:
        suggest = "https://cplonline.com.au/search/ajax/suggest/?q=" + urllib.parse.quote_plus(q)
        code, body = fetch(suggest)
        entry = {"query": q, "status": code, "count": 0}
        if code == 200:
            try:
                data = json.loads(body)
            except Exception:
                data = []
            entry["count"] = len(data) if isinstance(data, list) else 0
            if isinstance(data, list):
                for item in data:
                    if item.get("type") != "product":
                        continue
                    url = (item.get("url") or "").replace(r"\/", "/")
                    products.append({
                        "query": q,
                        "title": item.get("title") or item.get("name") or "",
                        "url": url,
                        "raw": {k: item.get(k) for k in ("title", "name", "url", "price", "sku") if k in item},
                        "source": "cpl_suggest_gh",
                    })
        results["queries"][q] = entry
        time.sleep(0.4)

    seen, dedup = set(), []
    for p in products:
        u = p.get("url") or ""
        if not u or u in seen:
            continue
        seen.add(u)
        dedup.append(p)
    results["products"] = dedup
    results["ok"] = results["home_status"] == 200 or any(v.get("status") == 200 for v in results["queries"].values())
    (out_dir / "cpl_suggest.json").write_text(json.dumps(results, indent=2))
    print("ok=", results["ok"], "products=", len(dedup), "home=", results["home_status"])
    return 0 if results["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
