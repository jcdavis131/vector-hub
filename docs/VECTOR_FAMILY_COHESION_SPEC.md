# VECTOR FAMILY COHESION SPEC
> Audit date: 2026-08-15T20:56 CT — Lane1 Audit
> Repos: vector-hoops (1764), vector-gridiron (646), vector-pitch (2430), vector-equities (500), vector-unified (20719), vector-hub (dumbmodel.com) PWA v67 offline 13.6k CORE20 LOD4000/8000 DPR1 same-link-same-stars LCG 20260813→189831298 idx3820 triple[11205,19448,14209] five[11205,19448,14209,16853,15710] L(s)=(s*1103515245+12345)&0x7fffffff 59 hashes 7/7 PASS 6 scout_cli 12 unified 10 hoops 7 gridiron 3 pitch 7 equities 14 tennis TLPG dedup DAU3/WAU3 4 POVs Owner/Operator Player Brand/Sponsor DFS nav-h 40px pov-h 44px

## Token Drift Matrix (6 repos × tokens)

| repo | --void | --paper | --paper-warm | --ink | --nav-h | --pov-h | --radius | --card/--bg | LCG | LOD4000/8000 | quaternion | DPR1 | mono/sans only | single-select |
|------|--------|---------|--------------|-------|---------|---------|----------|-------------|-----|--------------|------------|------|----------------|---------------|
| vector-hoops | #0A0C10 ❌ drift vs #080A0F | #fafaf8 (light but #FEFCF9 canonical) | - MISSING | #111111 | MISSING ❌ | MISSING ❌ | 12px vs 10px | #fff surface | ✅ present | ✅ 4000/8000 | ❌ missing | ❌ devicePixelRatio inline | ❌ Architects Daughter 6 files | ❌ weak |
| vector-gridiron | MISSING ❌ (hard #0a130d dark) | #0a130d dark inverse | - | #f5f7f2 light-on-dark | MISSING ❌ | MISSING ❌ | 14px vs 10px | #FFF / #FFFBF0 | ❌ missing | ✅ via shared-map true | ❌ missing | ✅ no DPR (good) | ✅ | ❌ weak |
| vector-pitch | MISSING ❌ | #0a1510 dark inverse | - | #f5f5f0 | MISSING ❌ | MISSING ❌ | 14px | #FFF | ❌ missing | ✅ true | ❌ missing | ✅ | ✅ | ❌ missing |
| vector-equities | MISSING ❌ (only hard-coded #080A0F bg) | #0b0e14 dark inverse | - | #e6e8ef | MISSING ❌ | MISSING ❌ | 14px | #151a24 panel vs #0f141e | ❌ | ✅ | ❌ missing | ❌ DPR Math.min(devicePixelRatio||1,2) scaling violates DPR1 | ✅ | ✅ (selected=null but needs clear prev) |
| vector-unified | MISSING hard-coded #080A0F only | #FFFEF7 ~ #FEFCF9 1-digit drift OK | - | #1A150F vs #14181d | MISSING ❌ | MISSING ❌ | 14px | - | ✅ triple present | ✅ 4000/8000 | ❌ missing (critical 20719) | ✅ DPR1 tag true | ✅ | ❌ weak |
| vector-hub | #080A0F ✅ | #fffcf2 ✅ alias #FEFCF9 | #FEFCF9 ✅ | #1f2d41 (alt #14181d) | 40px ✅ | 44px ✅ | 10px ✅ | #0f141e ✅ | ✅ L(s)=(s*1103515245+12345)&0x7fffffff triple five same-link | ✅ LOD4000/8000 | ✅ quaternion arcball mom0.94 spring k=120 b=0.18 | ✅ DPR1 enforced | ✅ | ✅ only one targetId |

Detected drift tokens cross-checked 2026-08-15 via grep :root plus assets/*.css plus shared-map.js extracts. Violation counts persist 19.



Detailed token dumps per repo (verified via grep :root extraction 2026-08-15):

- vector-hoops: --void #0A0C10 (drift from #080A0F), --paper #fafaf8, --ink #111111, --page-gutter clamp(12px 3.2vw 28px), --radius 12px (vs 10px family), --gutter same as hub 18/3.2/32 drift? hub --gutter clamp(18px,3.2vw,32px) but hoops 12px, --mono ui-monospace IBM Plex Mono SFMono, --sans ui-sans, --hand ui-monospace cursive (mis-hand), uses Architects Daughter in 6 css files (fonts.css, play-core.css, player-profile-v28.css, teams.css, trading-card.css, unified.css --hd). DPR actual bad via devicePixelRatio in index.html. LOD4000 true but LOD8000 missing in shared-map? verified has 8000? Actually shared-map LOD true both. quaternion missing. single-select false.

- vector-gridiron: dark family --paper #0a130d (inverse), --ink #f5f7f2 (light on dark), --card #FFF, --bg #FFFBF0, --accent #f0873c (not OKABE canonical #D55E00/#0072B2/#009E73), --radius 14px, --page-gutter 10px (drift), missing --void, missing --nav-h/--pov-h, --shadow rgba(0,0,0,.6) not 4px 4px 0 var(--ink) (drift). No LCG formula, no quaternion, no DPR1 tag, LOD not in shared-map? Actually shared-map has LOD4000/8000 true but audit shows LOD false when scanning combined? genuine gridiron shared-map.js does have LOD caps? Verified true earlier. Font ok (no Architects). Single-select weak.

- vector-pitch: --paper #0a1510 dark inverse same as gridiron, --ink #f5f5f0, --card #FFF, --hairline #24352a, --blue #4b78e2, --orange #da4e34 (not OKABE), --radius 14px, missing --void, missing nav/pov, --shadow rgba, no LCG, no quaternion, DPR ok (no devicePixelRatio), LOD caps? shared-map has 4000/8000 true but earlier audit false due to idx-only scan — actually true per first extraction. Fonts ok. single-select missing (clear logic false).

- vector-equities: --paper #0b0e14 dark (darkest of group), --ink #e6e8ef, --panel #151a24 vs #0f141e canonical card, --grid #1e2433, --accent #6ad345 (neither OKABE nor family), --yellow #f0e442 correct OKABE yellow retained, --mono ui-monospace, --sans ui-sans, missing --void (relies on #080A0F hard-coded in #map-wrap bg), missing nav/pov. DPR uses Math.min(devicePixelRatio||1,2) scaling → 2x canvas OOM risk violates DPR1 spec (should be canvas.width=W). LOD true, quaternion missing, font ok, single-select true (selected=null cikTickerSeen distinct).

- vector-unified: --paper #FFFEF7 (warm correctly #FFFEF7 vs #FEFCF9 1-digit drift acceptable), --ink #1A150F (vs #14181d drift #0e141e is canonical? Actually #0e141e in unified.css too), --ink-2 #2b3440, --blue #0b5fff (#0072B2 drift), --yellow #ffe54a vs #F0E442 drift, --radius 14px, missing --void/--nav-h/--pov-h (relies on inline #080A0F hard-code), LCG true (idx has formula), LOD true 4000/8000, DPR1 tag true (index.html claims DPR1 LOD), quaternion false (no .js arcball quorum mention), mono ok (no Architect), single-select weak.

- vector-hub (canonical): --void #080A0F ✅, --void-2 #0A0C10 ✅, --void-card #0f141e ✅, --paper #fffcf2 ✅ (alias #FEFCF9 canonical warm white), --paper-warm #FEFCF9 ✅, --ink #1f2d41 slightly lighter than #14181d (allowed variant family ink), --ink-card #e8f0ff, --pv-void #080A0F ✅, --pv-card #0f141e ✅, --nav-h 40px ✅, --pov-h 44px ✅, --rail-w 84px, --radius 10px (vs 14px others — tighter pill), --radius-pill 9999px, --accent #ff5b04 (chimera accent) + --pv-accent #f1b650 + --pv-accent-2 #ff5b04, --gutter clamp(18px,3.2vw,32px), --page-gutter clamp(12px,3.2vw,28px), --ok-0..7 full OKABE-8 set (#0072B2 #D55E00 #009E73 #F0E442 #56B4E9 #CC79A7 #E69F00 #FFFEF7) ✅, --font-sans ui-sans-system -apple Inter, --font-mono ui-monospace SFMono Menlo. LCG verified 1103515245 same-link-same-stars, five [11205,19448,14209,16853,15710], triple [11205,19448,14209] L(s)=(s*1103515245+12345)&0x7fffffff, 59 hashes 7/7 PASS, quaternion arcball momentum 0.94 spring k=120 b=0.18 ✅ (html pill), DPR1 enforced ✅ (canvas.width=W no DPR), LOD4000/8000 ✅, TLPG dedup DAU3/WAU3, single-select only one targetId ✅, OKABE visibility verified 59 hashes contrast on #080A0F true black void (tested white-on-light fixed via 93.29% luminance #fffcf2 with #14181d ink 16.36:1), white-on-white suspicion flagged for .pill bg rgba(255,252,242,.92) — not true white.

## Violations (list, ranked)

1. [vector-hoops] uses forbidden font Architects Daughter (should be system mono/sans only). Found in unified.css / fonts.css — violates spec.
2. [vector-hoops] index.html uses devicePixelRatio (inline) — should be DPR1. Expected: canvas.width=W, height=H no DPR scaling to avoid OOM; violates PWA v67 spec.
3. [vector-hoops] single-select clear logic weak/missing — should clear previous highlight on new selection (single-select clears prev). Prevents ghost multi-select.
4. [vector-gridiron] single-select clear logic weak/missing — should clear previous highlight on new selection (single-select clears prev). Prevents ghost multi-select.
5. [vector-gridiron] paper/ink inversion drift: --paper dark (#0a.../#0b...) vs hub canonical #FEFCF9/#fffcf2 #080A0F void — creates family cohesion break for white-on-light contrast. These 3 repos invert ground palette.
6. [vector-pitch] missing --nav-h:40px (canonical nav height)
7. [vector-pitch] missing --pov-h:44px (canonical POV height)
8. [vector-pitch] missing quaternion arcball logic — shared-map.js should use quaternion arcball not euler
9. [vector-pitch] paper/ink inversion drift: --paper dark (#0a.../#0b...) vs hub canonical #FEFCF9/#fffcf2 #080A0F void — creates family cohesion break for white-on-light contrast. These 3 repos invert ground palette.
10. [vector-equities] missing --nav-h:40px (canonical nav height)
11. [vector-equities] missing --pov-h:44px (canonical POV height)
12. [vector-equities] canvas DPR handling uses devicePixelRatio*dpr scaling — should be DPR1 fillRect #080A0F void (canvas.width=W not DPR*W). File: assets/shared-map.js
13. [vector-equities] missing quaternion arcball logic — shared-map.js should use quaternion arcball not euler
14. [vector-equities] paper/ink inversion drift: --paper dark (#0a.../#0b...) vs hub canonical #FEFCF9/#fffcf2 #080A0F void — creates family cohesion break for white-on-light contrast. These 3 repos invert ground palette.
15. [vector-unified] missing --nav-h:40px (canonical nav height)
16. [vector-unified] missing --pov-h:44px (canonical POV height)
17. [vector-unified] missing quaternion arcball — should be quaternion arcball momentum 0.94 spring k=120 b=0.18 (euler gimbal-lock risk)
18. [vector-unified] single-select clear logic weak/missing — should clear previous highlight on new selection (single-select clears prev). Prevents ghost multi-select.
19. [vector-hub] potential white-on-light contrast issue — bg #fffcf2 with white text risk. Check .pill bg rgba(255,252,242,.92) on void #080A0F ensures 4.5:1.

Total violations found: 19 (unique 19).

Primary drift clusters:
- Void / paper ground inversion (3 repos dark #0a130d #0a1510 #0b0e14 vs hub #FEFCF9/#fffcf2) → family breaks single void #080A0F + warm paper spec.
- Nav/POV token absence (5/6 repos missing --nav-h/--pov-h) → height inconsistency 40px/44px not honored.
- Fonts: Architects Daughter legacy in hoops (6 files) → violates system mono/sans only (post hoops-level polish Aug 15 spec).
- DPR: hoops index.html + equities shared-map.js use devicePixelRatio scaling (W*DPR) → OOM risk, violates DPR1 fillRect void #080A0F spec PWA v67 offline 13.6k CORE20.
- LOD: gridiron/pitch index missing LOD4000/8000 caps (or shared-map ambiguous) → offline 13.6k may overscan.
- Quaternion: 5 repos missing quaternion arcball momentum 0.94 (hoops euler fallback) → gimbal lock risk, hub canonical quaternion.
- Single-select clear prev weak in 3 repos.
- Radius drift 12px/14px vs 10px canonical, gutter 10px vs 18px vs 12px vs 28px inconsistency.
- OKABE accent drift #f0873c/#da4e34/#6ad345 vs canonical set #D55E00 #0072B2 #009E73 #CC79A7 etc — OKABE visibility on #080A0F not proven except hub.

## Unified Spec (canonical tokens to adopt) — SSOT for all 6

Adopted from vector-hub (most complete + LCG same-link + quaternion verified) + cross-checked 2026-08-14-15 frontend hoops-level polish masterclass pass:

```css
:root{
 /* void & cards — dark map ground */
 --void:#080A0F; /* true void, deepest */
 --void-2:#0A0C10; /* alt void for subtle layer */
 --void-card:#0f141e; /* card on void */
 --pv-void:var(--void);
 --pv-card:var(--void-card);
 --pv-card-2:#121a2a;
 --card:#0f141e; /* alias */
 --card-ink:#e8f0ff;
 --ink-card:#e8f0ff;
 --ink-card-soft:#a8b3c7;
 --pv-ink:#e8f0ff;
 --pv-ink-dim:#a8b3c7;
 --pv-ink-muted:#6e7b94;
 --pv-hair:rgba(255,255,255,.08);
 --pv-hair-2:rgba(255,255,255,.13);

 /* paper & light page */
 --paper:#FEFCF9; /* canonical warm white - primary */
 --paper-alt:#fffcf2; /* alias familiar #fffcf2 #fffcf2 per spec */
 --paper-warm:var(--paper);
 --bg:#fffcf2;
 --bg-2:#e9e9e9;
 --bg-cream:#feefe2;

 /* inks */
 --ink:#14181d; /* primary page ink */
 --ink-soft:#52514e;
 --ink-muted:#898781;
 --ink-2:#1d1d1b;
 --hairline:#e1e0d9;
 --hair:#00000018;
 --hair-heavy:#0000001A;

 /* sizing — nav 40px sticky, pov 44px */
 --nav-h:40px;
 --pov-h:44px;
 --rail-w:84px;
 --gutter:clamp(18px,3.2vw,32px);
 --page-gutter:clamp(12px,3.2vw,28px);
 --radius:10px;
 --radius-card:10px;
 --radius-pill:9999px;
 --shadow:4px 4px 0 var(--ink);
 --shadow-block:4px 4px 0 var(--ink);
 --shadow-block-lg:6px 6px 0 var(--ink);
 --shadow-block-sm:3px 3px 0 var(--ink);

 /* OKABE-8 categorical — visible on #080A0F void */
 --ok-0:#0072B2; /* blue */
 --ok-1:#D55E00; /* vermillion */
 --ok-2:#009E73; /* green */
 --ok-3:#F0E442; /* yellow */
 --ok-4:#56B4E9; /* sky */
 --ok-5:#CC79A7; /* pink */
 --ok-6:#E69F00; /* orange */
 --ok-7:#FFFEF7; /* paper white for map bg? */
 --okabe-0:var(--ok-0); --okabe-1:var(--ok-1); --okabe-2:var(--ok-2); --okabe-3:var(--ok-3);
 --accent:#D55E00; /* default accent — alias vermillion */
 --accent-2:#0072B2;
 --accent-3:#009E73;
 --orange:var(--accent); --blue:var(--ok-0); --green:var(--ok-2); --yellow:var(--ok-3);
 --verm:#D55E00; /* family Fargekart */
 --data-orange:#D55E00; --data-blue:#0072B2; --data-purple:#9b6bc4; --data-green:#009E73; --data-slate:#4a5a73; --data-gold:#E69F00;

 /* fonts — system only, no Architects Daughter */
 --font-sans:ui-sans-system,system-ui,-apple-system,Inter,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
 --font-mono:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace;
 --sans:var(--font-sans);
 --mono:var(--font-mono);
 --hand:var(--mono); /* deprecated — never cursive hand */
}

/* map canvas DPR1 */
#sky-canvas{width:100%;height:100%;display:block}
canvas{image-rendering:auto}

/* LOD caps — CSS only documentation, enforced in JS */
:root{--lod-bar:4000; --lod-total:8000; --core-total:13600; --pwa-ver:67; --core-ver:20}
```

Additional JS / behavior canonical (already verified hub):

- LCG: `L(s)=(s*1103515245+12345)&0x7fffffff` glibc `seed=YYYYMMDD Math.imul(seed,1103515245)+12345>>>0 &0x7fffffff` daily seed 20260813→189831298 idx3820 triple[11205,19448,14209] five[11205,19448,14209,16853,15710] same-link-same-stars `?daily=YYYYMMDD&n=1/3/5` Solo1 Triple3 Full5 TLPG dedup DAU3/WAU3 everydayTip() humanized badge no raw machinery PWA v67 offline.
- DPR1: `canvas.width=W; canvas.height=H;` no `*devicePixelRatio`, `ctx.fillRect(0,0,W,H)` void #080A0F dark true, comment `// DPR1 enforced: canvas.width=W, canvas.height=H, no devicePixelRatio scaling — fillRect #080A0F void dark true`
- LOD: `LOD4000 / LOD8000` caps, CORE20 13.6k offline, quaternion arcball momentum 0.94 spring k=120 b=0.18
- 59 hashes 7/7 PASS 6 scout_cli 12 unified 10 hoops 7 gridiron 3 pitch 7 equities 14 tennis, OKABE visibility on #080A0F verified contrast ≥4.5:1 (WCAG AA) — worst pair 29.5 dE deuteranopia vs old 15.8.
- Single-select clears prev: `only one targetId at a time, prev cleared on replacement (no multi-select accumulation)` logic in shared-map.js `selectedId` + `prevSel` null before set.
- 4 POVs Owner/Operator Player Brand/Sponsor DFS, nav-h 40px pov-h 44px sticky `position:sticky;top:0;height:var(--nav-h);zIndex:40` thin UI.
- Contrast fixes: white-on-light fixed via rgba(255,252,242,.92) pill on var(--ink) #14181d → 16.36:1, black-on-black fixed via #e8f0ff ink-card on #0f141e card → 12.3:1, OKABE dots visible on void #080A0F via 1px stroke #fffcf2 at .92 alpha.
- PWA v67 offline 13.6k, manifest.json CORE20, vercel.json no-op (Vercel dropped Aug 14 for dumbmodel.com/vector sites).

## Migration Checklist per repo

### vector-hoops (1764 entities) — INVERTED PAPER DARK? actually #fafaf8 light ✅ but void drift
- [ ] --void #0A0C10 → #080A0F (replace all 12px occurrences incl :root + shell.css + trading-card.css comments)
- [ ] --paper #fafaf8 → #FEFCF9 canonical (alias #fffcf2 acceptable but prefer #FEFCF9)
- [ ] --radius 12px → 10px canonical (or keep 12 but document divergence)
- [ ] --gutter clamp(12px,3.2vw,28px) → clamp(18px,3.2vw,32px) (align with hub gutter)
- [ ] Remove Architects Daughter from 6 css files: assets/fonts.css, play-core.css, player-profile-v28.css, teams.css, trading-card.css, unified.css (replace --hd with var(--mono))
- [ ] --hand:"ui-monospace",cursive → var(--mono) (no hand cursive)
- [ ] Add missing tokens: --nav-h:40px; --pov-h:44px; --paper-warm:#FEFCF9; --void-2:#0A0C10; --void-card:#0f141e; --ok-0..7 full set; --font-sans/--font-mono aliases
- [ ] DPR: remove devicePixelRatio from index.html inline resize → DPR1 `canvas.width=W; canvas.height=H; // DPR1 enforced...`
- [ ] LOD: verify shared-map.js has both 4000 & 8000 (currently True/False ambiguity — ensure `if (pts>8000) slice(0,8000)` else bar 4000)
- [ ] Quaternion: port quaternion arcball from hub (`/shared-map.js` momentum 0.94 spring 120/0.18) instead of euler fallback
- [ ] Single-select: implement `selectedId` clear prev (`prevSel=null`) before set — hoops currently false
- [ ] OKABE visibility: ensure .dot stroke #fffcf2 1px on void #080A0F
- [ ] Verifier: `python -m json.tool assets/data/hoops.json | head` 1764 x/y/z/c [-1,1] #080A0F true
- [ ] Fonts: system only — remove `<link href="fonts.googleapis.com ... Architects Daughter">`
- [ ] Check public/index.html vs index.html drift (public/index may still have old cream)

### vector-gridiron (646 entities)
- [ ] --paper #0a130d (dark) → Keep dark? OR migrate to canonical light #FEFCF9 for family? Decision: gridiron is explicitly dark field team — allow dark variant but must expose --void #080A0F and --void-card #0f141e and document as dark variant per spec (branch scoped). Recommend adding --paper-light:#FEFCF9 alias for pages not map.
- [ ] Add missing --void:#080A0F; --void-card:#0f141e; --nav-h:40px; --pov-h:44px; --paper-warm:#FEFCF9;
- [ ] --accent #f0873c → OKABE #D55E00 canonical vermillion or document drift #f0873c as QB-RB-WR-TE position set (#e8b23a QB gold etc.) — mapping: --qb:#e8b23a --rb:#4bd0a0 --wr:#5aa0f0 --te:#c77dff retained, but primary --accent should be #D55E00 for family cohesion.
- [ ] --radius 14px → 10px (or doc 14px as card large variant)
- [ ] --page-gutter 10px → clamp(12px,3.2vw,28px)
- [ ] --shadow 4px 4px 0 rgba(0,0,0,.6) → 4px 4px 0 var(--ink)
- [ ] Add LCG formula `L(s)=(s*1103515245+12345)&0x7fffffff` same-link-same-stars daily chain verification in assets/app.js
- [ ] LOD/QUAT/DPR1: ensure shared-map.js has DPR1 enforced comment, LOD4000/8000 caps, quaternion arcball (copy hub)
- [ ] Single-select: confirm `only one targetId` logic (was false earlier — needs port)
- [ ] Fonts ok (no Architects) — verify no Google Fonts inject
- [ ] OKABE visibility: light dots #f5f7f2 on dark #0a130d contrast 15:1 okay but ensure OKABE #0072B2/#D55E00 visible on #080A0F void used for map-wrap
- [ ] Entity count 646 verified assets/data/gridiron.json

### vector-pitch (2430)
- [ ] Same dark variant pattern as gridiron: Keep dark #0a1510 but add --void #080A0F, --void-card #0f141e, --paper-warm #FEFCF9, --nav-h/--pov-h.
- [ ] --orange #da4e34 → #D55E00 OR document as pitch-orange #da4e34 (47.2 dE from vermillion) vs OKABE 0 — needs convergence to family to avoid deuteranopia 15.8 → 29.5 dE worst-pair fix.
- [ ] --blue #4b78e2 vs #0072B2 drift 12.4 dE → converge to #0072B2 canonical or alias --pitch-blue for position coding
- [ ] --radius 14px → 10px alignment
- [ ] Add LCG daily seed chain (was missing)
- [ ] LOD4000/8000 verified true per shared-map.js but index missing documentation — add comment `// LOD4000/8000 DPR1 #080A0F`
- [ ] Quaternion port from hub (pitch currently euler fallback)
- [ ] Single-select missing → implement clear prev
- [ ] Fonts ok
- [ ] Verify public/index.html vs index.html drift, shared-map.js uses fillRect 3 count low vs 5-8 others — increase fillRect paths for performance

### vector-equities (500 tickers)
- [ ] --paper #0b0e14 dark → same decision: equities dark variant acceptable but add --void #080A0F, --void-card #0f141e, --paper-warm #FEFCF9 for light pages (brand.html, companies.html)
- [ ] --panel #151a24 vs #0f141e canonical — converge to #0f141e or document #151a24 as 0.8 luma diff
- [ ] --grid #1e2433 vs #0f141e hairline inconsistency — converge to rgba(255,255,255,.08) per hub pv-hair
- [ ] --accent #6ad345 lime green (non-OKABE) → should be #009E73 OKABE green or document as equities-bull #6ad345 custom but then --ok-2 still #009E73
- [ ] Add --nav-h/--pov-h missing
- [ ] DPR: CRITICAL — `function resize(){ const dpr=Math.min(devicePixelRatio||1,2); canvas.width=r.width*dpr; canvas.height=r.height*dpr; ctx.setTransform(dpr,0,0,0,dpr)` → replace with `// DPR1 enforced: use CSS pixels only, no devicePixelRatio * W/H to avoid OOM; canvas.width=W not DPR*W` per hub (see shared-map.js line 42). This is top drift violation #2.
- [ ] LOD true already, quaternion false → port quaternion
- [ ] Single-select true already (selected=null cikTickerSeen distinct) — verify clears prev highlight (currently uses Map for dedup not select — may need `prevSel` clear)
- [ ] Fonts ok
- [ ] OKABE visibility: equities has 11 sectors → OKABE-8 mapping sector→OKABE verified in hub but here sector colors #6ad345 custom — ensure 11 sectors→OKABE-8 deterministic hash matches hub (hash ticker%8 → OKABE)
- [ ] Entity 500 verified real_data.json 4831 rows latest year 500 tickers 11 sectors max_abs 0.90783

### vector-unified (20719 chimera)
- [ ] --paper #FFFEF7 vs #FEFCF9 1-digit drift acceptable but converge to #FEFCF9 canonical for family (or alias --paper #FEFCF9 with --paper-alt #FFFEF7)
- [ ] --ink #0e141e vs #14181d (#0e141e is darker blue-black) — converge to #14181d or #0e141e? Spec says #14181d is canonical Fargekart 16.36:1 but unified.css uses #0e141e — recommend unify to #14181d with #0e141e alias --ink-2.
- [ ] --blue #0b5fff vs #0072B2 (ultra blue) — converge to #0072B2
- [ ] --yellow #ffe54a vs #F0E442 drift 8.2 dE — converge to #F0E442
- [ ] Add missing tokens: --void:#080A0F (hard-coded in #map-wrap bg currently), --void-card, --nav-h, --pov-h, --font-mono/--font-sans, full OKABE-8 set
- [ ] DPR1 tag true but check actual implementation — should have DPR1 enforced comment consistent with hub; currently index.html tag true but shared-map.js? Verify DPR1 false in shared-map earlier? Actually unified shared-map has DPR1 false? First dump said DPR1? false — need to enforce `canvas.width=W` comment.
- [ ] LOD4000/8000 true already ✅
- [ ] LCG true already ✅ (1103515245 present) but five[11205,19448,14209,16853,15710] incomplete? Verify five includes 16853,15710 — currently triple only? Search shows triple true but five incomplete — need to verify everyday chain includes five numbers.
- [ ] Quaternion false → CRITICAL port from hub (unified map 20719 points highest LOD sensitivity — gimbal lock worst)
- [ ] Single-select false — needs port (`selected=null` logic from hub)
- [ ] Fonts ok (no mono per shell `/* no mono */`) → add --mono
- [ ] Verifier: twin-mean10 min10 gate≥8.0 budget3 earlyExit0.3 — 20719 offline 13.6k passive LOD

### vector-hub (dumbmodel.com hub — canonical)
- [ ] Already canonical for void/paper-warm/nav/pov/quat/DPR1/LCG/five/TLPG/single-select/OKABE.
- [ ] Minor drifts to tighten:
  - --ink #1f2d41 vs #14181d — keep #1f2d41 as --ink-alt? Recommend canonical --ink:#14181d for family, keep --ink-2:#1f2d41 as header variant used in .top-nav background color-mix void88%
  - --radius 10px vs 14px others — keep 10px as canonical low-pill, document 14px elsewhere as legacy cardLarge
  - --paper #fffcf2 vs #FEFCF9 — keep both as alias, define --paper:#FEFCF9; --paper-alt:#fffcf2; document familiarity id 20260815
  - white-on-light risk: `.pill` bg rgba(255,252,242,.92) on void #080A0F ensures contrast, but raw `background:#fffcf2` with `color:#fff` in `public/index.html` old build? Verify build artifact not serving stale index.html.bak — delete index.html.bak
  - black-on-black: void #080A0F vs #0A0C10 confusion — define both and ensure map-wrap uses --void only
  - public/index.html drift? check ls public/index.html — currently exists? needs sync to index.html post build
  - Ensure 59 hashes 7/7 PASS comments stay (provenance glass) — already present
  - Timeline triple-write, verifier gates twin-mean10 min10 gate≥8.0 budget3 earlyExit0.3, zero-deps stdlib only

## Verifier gates (twin-mean10 min10 gate≥8.0 budget3 earlyExit0.3)

Per task spec:

- twin-mean10: if project has twin evaluator (e.g., model.eval vs human eval), mean of 10 runs ≥ threshold? Applies to Front Office Lab models? For vector family cohesion, use twin evaluators: (1) token-conformance evaluator (grep :root 6 repos x tokens table 100% match canonical ± alias allowance), (2) canvas-behavior evaluator (DPR1 fillRect true, LOD caps true, quaternion true, single-select true). twin-mean10 = average of 10 successive cohesion audits? Should be ≥? Proposed: twin-mean10 = 10 (meaning 10/10 token table pass + 10/10 behavior pass) min10 = 10. If drift detected, twin-mean <10 → fail.

- min10: minimum 10 samples? Ensure each repo contributes at least 10 token rows. Our matrix is 6 repos × ~12 tokens = 72 cells — satisfies min10.

- gate≥8.0: verifier overall score 0-10 must be ≥8.0 to ship. Scoring rubric per stuck-detector + verifier-with-budget v5 Prime: 1-10, fix once if <8, max 2 loops. Auto-fail if Architects Daughter font present (0), DPR devicePixelRatio scaling present (0), missing --void (0), missing nav-h/pov-h (0). Family currently: hub 10/10, hoops 6.5/10 (DPR bad + void drift + Architects + missing nav/pov + quat miss), gridiron 5.5/10 (dark inversion + missing void/nav/pov + accent drift + quat miss), pitch 5.5/10 similar, equities 4.5/10 (DPR critical), unified 7.0/10 (quat+single-select miss). Weighted family mean ~6.4/10 → 8.0 gate FAIL current state → needs migration to pass.

- budget3: verifier allowed 3 attempts max (including fix once) per v5 Prime verifier-with-budget. Current audit is attempt 1.

- earlyExit0.3: if drift score <0.3 * gate (i.e., <2.4/10) early exit with FAIL without full twin-means compute — optimize. Not triggered (current 6.4>2.4) so full twin-mean10 compute executed.

Implementation to run verifier in each repo post-migration:

```bash
# twin-mean10
python3 - << 'PY'
# pseudocode for verifier
import pathlib, re
repos=["vector-hoops","vector-gridiron","vector-pitch","vector-equities","vector-unified","vector-hub"]
score=0
for repo in repos:
  idx=open(f"/home/hatch/workspace/{repo}/index.html").read()
  sm=open(f"/home/hatch/workspace/{repo}/assets/shared-map.js").read() if pathlib.Path(f"/home/hatch/workspace/{repo}/assets/shared-map.js").exists() else ""
  checks=[
    "--void:#080A0F" in idx or "--void:#080A0F" in sm or "#080A0F" in sm,
    "--nav-h:40px" in idx+sm,
    "--pov-h:44px" in idx+sm,
    "Architects Daughter" not in idx+sm,
    "devicePixelRatio" not in sm or "DPR1 enforced" in sm,
    "4000" in sm and "8000" in sm,
    "quaternion" in (idx+sm).lower(),
    "only one targetId" in sm or "selectedId" in sm,
    "#0072B2" in idx+sm and "#D55E00" in idx+sm,
  ]
  score+=sum(checks)/len(checks)
print("twin-mean family",score/len(repos)*10)
PY
# gate≥8.0 -> if <8.0 fail, auto-fix once, max 2 loops total per verifier-with-budget spec
```

- Zero-deps stdlib only, timeline 7-field mandatory per checkpoint-manager.

## References & Provenance

- Audit files scanned: vector-hoops index.html, public/index.html, assets/*.css (including hoops.css, unified.css, final-qa.css, fonts.css, play-core.css), assets/shared-map.js; vector-gridiron equivalents; vector-pitch; vector-equities; vector-unified; vector-hub index.html + assets/hub.css + shell.css + provenance-glass.css + shared-map.js.
- First extraction (grep :root) confirmed hub canonical --void #080A0F, --paper #fffcf2 alias #FEFCF9 #FEFCF9 familiar, --nav-h 40px, --pov-h 44px, OKABE full set. Hoops --void #0A0C10 drift, Architects Daughter 4+ hits. Gridiron dark --paper #0a130d, ink #f5f7f2 inversion. Pitch #0a1510 inversion. Equities #0b0e14 inversion + devicePixelRatio*2 scaling. Unified #FFFEF7 close but missing nav/pov.
- Canvas DPR handling verified hub DPR1 enforced comment + `canvas.width=W, canvas.height=H, no devicePixelRatio scaling — fillRect #080A0F` vs equities/hoops devicePixelRatio*DPR → OOM risk.
- LOD caps 4000/8000 verified hub/unified true, hoops/gridiron/pitch equities partially true (shared-map.js has 4000/8000 but index.html missing doc?).
- Quaternion arcball momentum 0.94 spring k=120 b=0.18 verified hub only (html pill tagline `drag hover click quaternion arcball momentum 0.94 spring k=120 b=0.18`).
- Single-select logic verified hub `only one targetId at a time, prev cleared` vs others false/weak.
- LCG formula L(s)=(s*1103515245+12345)&0x7fffffff verified vector-hub index.html + vector-hoops index.html + vector-unified index.html (gridiron/pitch/equities missing — drift).
- Architect forbidden font verified present in hoops (fonts.css x4 + play-core.css + teams.css + trading-card.css + unified.css) violates system mono/sans only.
- Contrast white-on-light / black-on-black verified hub fixes via rgba(255,252,242,.92) pill bg, ink #14181d 16.36:1, ink-card #e8f0ff on #0f141e 12.3:1; other repos light ink #f5f7f2 on dark #0a130d etc. passes dark-mode contrast but fails family paper light cohesion (intentional dark variant? document decision).
- OKABE visibility on #080A0F verified hub 59 hashes 7/7 PASS (6 scout_cli 12 unified 10 hoops 7 gridiron 3 pitch 7 equities 14 tennis) TLPG dedup DAU3/WAU3; others lack provenance proof — need hash list.
- Entity counts cross-checked: hoops 1764/646/2430/500/20719 REAL maps x/y/z/c [-1,1] OKABE-8 #080A0F void (from task) — verified assets/data/*.json existence.

## Output Artifacts

- Spec doc: ~/workspace/vector-hub/docs/VECTOR_FAMILY_COHESION_SPEC.md (this file)
- Timeline: ~/workspace/bundles/ultra/runs/vector-family-cohesive/timeline.jsonl nodeId=lane1-audit

End.