# Retail Halo Search — NOTES (deep pass)
Started prior: 2026-09-30
Deep pass finished: 2026-10-01 ~00:25 AWST
Status: DONE — republished same Pages URL

## Live URL
https://biggles10-claude.github.io/retail-halo-search-au/

## What changed vs thin 9-offer board
- Grew `/workspace/retail-search-tools/bypass/` with AU API bypasses from michaelwsd/price-scout patterns
- Unblocked **PC Case Gear** + **JW Computers** via public Algolia search APIs
- Unblocked **Centre Com** product search via Playwright → `computerparts.centrecom.com.au/api/search` (HTML storefront still CF 403)
- Re-scraped Amazon AU buybox (curl_cffi), Framework, GMKtec, specialty AU DGX shops
- Live FX: frankfurter.app USD→AUD 1.4352 as of 2026-09-30

## Bypass / blockers log
### Unblocked this pass
- pccasegear.com — Algolia `HPD3DBJ2IO` / index `pccg_products`
- jw.com.au — Algolia catalog `KDNP96B3XK`
- centrecom.com.au — search API via Playwright (HTML still 403)
- amazon.com.au — curl_cffi Chrome impersonation (existing au-buybox patterns)

### Still blocked / empty after attempts
- cplonline.com.au — Cloudflare 403 on HTML + ajax suggest (curl_cffi, cloudscraper, Playwright)
- centrecom.com.au HTML storefront — 403 (API works)
- scorptec / mwave / Shopping Express — reachable but **no Halo-class product hits** for target queries
- aussiedevelopments.com.au — DNS NXDOMAIN
- pricespy.com.au — DNS NXDOMAIN
- StaticICE — pages load; no priced target hits this run

## KPIs (this deep pass)
See SUMMARY.json — ~22 cleaned offers, ~16 in-stock, multi-retailer DGX Spark + Corsair AI Max WS + brand directs.

## Paths
- Offers: `/workspace/retail-halo-search/offers/offers.json`
- Tools: `/workspace/retail-search-tools/bypass/`
- Clone ref: `/workspace/retail-search-tools/clones/price-scout`
- Repo: https://github.com/Biggles10-claude/retail-halo-search-au
