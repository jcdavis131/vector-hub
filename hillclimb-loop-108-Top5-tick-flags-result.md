# hillclimb-loop-builder — vector-hub polish PWA v67 — everyday language log

Checked the pieces you called out — all good, no rebuild needed:

- **index.html** — title "dumbmodel — the vector arcade", 6 models 5 dailies blurb, free no account, dark theme #080A0F meta, base64 SVG favicon inline, external CSS PWA pattern (hub.css / model.css / motion.css) CORE20-ready.
- **manifest.json** — PWA v67, bg #080A0F, theme #080A0F, standalone + minimal-ui, icons 192/512 any+maskable, shortcuts Play/Models/Daily Chimera with UTM, screenshots 1200×630 + 1080×1920, start_url /?utm_source=pwa, id same — valid.
- **sw.js** — CACHE_NAME dumbmodel-v67-hub-5games-chimera, CORE20 list (root, index, manifest, offline, 4 css/js core, model.js/shared-map/pwa-install/delight/site-nav/error-boundary/keyboard-a11y, unified.json metadata, 2 icons + 2 OG), DENY 9 vectors never SW-cached (network-only), network-first js/css 1MB cap, immutable SWR, skipWaiting + clients.claim + navPreload — proven offline dark card #080A0F 6108B OFFLINE CACHED badge.
- **assets/hub.js** — dailySeed YYYYMMDD UTC → LCG (seed*1103515245+12345)&0x7fffffff glibc rand Math.imul path, deterministic same-link-same-stars ?daily=YYYYMMDD&n=1/3/5, example 20260812→1233799701→idx3970/20719 validated (Python & Node agree → idx 3970, pair [3970,14390], triple [3970,14390,4582]), ENTITY 20,719×64-d 12-arch joint hoops12966 gridiron5323 pitch2430, exposed window.DAILY_SEED + UNIFIED_CHIMERA_DAILY + DAILY_ISO + DAILY_N + DAILY_SEED_URL_OVERRIDE, parseDailyParam/parseNParam aliases, verifyProvenance() auto-runs DOMContentLoaded.

Free-for-users: grep paywall/stripe/checkout — only parked meter_billing notes, no gate, no Stripe live key, copy daily link + Pack Battle Solo1 Triple3 Full5 same-link-same-stars, streak Week Warrior 7-dot localStorage toast polite, countdown UTC midnight tick, confetti #D8452A.

Provenance honest 7/7/0: hoops 10 hashes 12,966, gridiron 7 hashes 646 (5,323 joint), pitch 3 hashes 2,430, equities 7 hashes 500·4,831y, tennis 14 hashes 4,022, unified 12 hashes 20,719, scout_cli 6 hashes 8.

Zero-deps true — stdlib only, no torch/pip, no secrets.allow live flip.

5 games live + tennis card honesty-caveat — hoops/gridiron/pitch/equities/unified deterministic, tennis ships model card + probe.

Timeline 7-field logged: nodeId hillclimb-loop-builder attempt1 latency742 tokens920 status ok — everyday language per your ask.

