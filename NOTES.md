<<<<<<< HEAD
# Retail Halo Search — Deep pass notes (in-stock only)

- Board policy (Biggles 2026-10-01): **in-stock only** — OOS rows dropped entirely (no OOS section).
- Live URL: https://biggles10-claude.github.io/retail-halo-search-au/
- VERIFY fix applied: **wisp.net.au** DGX Spark → live **AUD 8791.97 in_stock** (was 8645 oos on prior board).
- Dropped 5 OOS rows: Amazon AU GMKtec Evo-X2, Framework 128GB mainboard, three GMKtec.com SKUs marked oos on prior deep board.
- PCCG / JW prices re-checked via Algolia (HTML storefronts still Cloudflare 403).
- Direct HTTP verify PASS: igamingcomputer, wisp, prology, ple (prices matched).
- FX: frankfurter USD→AUD **1.4352** (2026-09-30).

## Still blocked / empty
- CPL Online: Cloudflare 403 (methods exhausted)
- Centre Com HTML storefront 403 (search API OK)
- Scorptec / Mwave / Shopping Express: no Halo-class listings
- aussiedevelopments.com.au: DNS NXDOMAIN
=======
# Retail Halo Search — in-stock only (Coverage FAIL fix)

- Live: https://biggles10-claude.github.io/retail-halo-search-au/
- Board policy: **in-stock only**
- Added Amazon AU **B0H5C72276** WEELIAO ONEXStation AI Max+ 395 128GB — buybox zip 3000: **AUD 4812.98**, availability **Only 3 left in stock.**, seller Weeliao-AU (2026-10-01T00:33:42+08:00)
- Published in-stock offers: **18**
- Cheapest exact in stock: amazon.com.au AUD 4812.98
- Amazon AU keyword expand: many search pages 503; GMKtec EVO-X2 search returned accessories/handbooks (not added). Honest blocker: Amazon search rate-limit 503 during expand.

## Still blocked
- CPL Online Cloudflare 403
- Centre Com HTML 403 (API OK)
- Amazon AU search expand intermittent 503
>>>>>>> 20bf3cd (Coverage FAIL fix: Amazon AU B0H5C72276 WEELIAO ONEXStation in-stock AUD 4812.98)
