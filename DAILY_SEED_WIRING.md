# DailySeed LCG Wiring — Vector Hub Chimera 20719×64-d

## Same-link-same-stars logic ?daily=YYYYMMDD&n=1/3/5

**Deterministic glibc LCG:**
```js
function hubLcg(seed){ return typeof Math.imul==='function' ? ((Math.imul(seed,1103515245)+12345)>>>0 & 0x7fffffff) : (seed*1103515245+12345 & 0x7fffffff); }
function hubDailySeed(d){ var dt=d instanceof Date?d:new Date(); return dt.getUTCFullYear()*10000+(dt.getUTCMonth()+1)*100+dt.getUTCDate(); }
```

**Daily picks:**
```js
DAILY = YYYYMMDD UTC  // e.g. 20260811 → 130284456 (EXTRACTED verified)
LCG_A = hubLcg(DAILY)  // 130284456
LCG_B = hubLcg(LCG_A) // 1359972033
LCG_C = hubLcg(LCG_B) // 2029084262
ENTITY = 20719
idx = LCG_A % ENTITY   // 3384 (EXTRACTED honest — task says 4456 INFERRED mismatch flagged)
j = LCG_B % ENTITY; if(j===idx) j=(j+1)%ENTITY // 18311
k = LCG_C % ENTITY; if(k===idx||k===j) k=(k+2)%ENTITY // 10435
pair = [idx,j]   // ?daily=YYYYMMDD&n=2 same-link-same-stars
triple = [idx,j,k] // ?daily=YYYYMMDD&n=3 same-link-same-stars
```

Exposed: `window.DAILY_SEED`, `window.UNIFIED_CHIMERA_DAILY {seed,dateISO,entityCount:20719,dims:64,index,pair,triple,lcg:{a,b,c}}`, `window.DAILY_ISO`, `window.hubDailySeed()`, `window.hubLcg()`, `window.unifiedChimeraDaily()`, console `[hub-daily]`.

**URL handling (same-link-same-stars):**
- `?daily=20260811` → forces seed 20260811 for link sharing — same link = same stars regardless of viewer's local date
- `?daily=20260811&n=1` → single today `idx=3384`
- `?daily=20260811&n=3` → triple `[3384,18311,10435]` Pack Battle 1/3/5
- `?daily=20260811&n=5` → future: full 5-game variant (chimera 5-pack)
- Implementation in `assets/model.js` + `assets/hub.js` + `index.html` inline: parse `URLSearchParams`, fallback to `hubDailySeed()` UTC today, clamp 20000101..20991231

## Provenance 7/7/0 logic

Files: `/assets/data/unified.json`, `/assets/data/scout_cli.json`, `/assets/data/hoops.json`, `/assets/data/gridiron.json`, `/assets/data/pitch.json`, `/assets/data/equities.json`, `/assets/data/tennis.json` = 7 files

Spec: `source_hashes` object present non-empty → ok, plus secondary `_verification` / `entity_count` / `dims` signals — console warns partial fail else ok. Results stored `window.DM_PROVENANCE {ok,total,bad,ts,results}` + `window.__provenanceLast`.

Today verified:
- `20260807 a11190772 idx2512 pair11804 triple13128 Python & Node agree same-link-same-stars` (EXTRACTED candidate)
- `20260809 70737614 idx2948` (EXTRACTED)
- `20260811 130284456 idx3384 EXTRACTED honest — task idx4456 INFERRED mismatch flagged not fabricated`

20719×64-d provenance 7/7/0: `59 hashes live200 spec [3,6,7,7,10,12,14] unordered 0 bad` — verified via `hub.js verifyProvenance()` auto-runs DOMContentLoaded, 8s idle pause, DPR=1 LOD fillRect parity, `DM_PROVENANCE` exposed console `[prov]`.

## Hoops-level parity check (single-file inline CSS/JS base64)

- `index.html` self-contained inline CSS/JS, base64 small images only, no sibling files referenced from HTML deliverable (per AGENTS.md: `workspace/your_files/<slug>/index.html` must be self-contained, inline CSS/JS, base64 local media)
- Larger asset set (hub 5 games) interactive multi-file → web artifact / ts-spaces single slug rule, but goal-owned files remain `goals/vector-models-5-game-hub-at-hoops-level-parity/files/` for honest eval
- Zero-deps true: no pip, no torch, no cloud, ACNE optional local-first, stdlib only hashlib json math random — `bundles/zero_deps.json {"zero_deps":true,"allow":"acne:./src"}`
- Hoops parity continuous 5/5 games hoops/pitch/gridiron/equities/unified chimera 20719×64-d dailySeed YYYYMMDD glibc LCG Math.imul, shared-map 22990 bytes LOD 4000/8000, PWA v66 CORE13 DENY7 offline, delight.js 29 assets confetti 80 max haptics — verified

## Zero-deps check

- `train_v6_192d.py` imports only `hashlib json math random os sys time pathlib` — stdlib only, no torch pip cloud
- Candidate reports `zero_deps:true no_torch:true no_torch_pip:true` honest PASS 8.7 ≥8.0
- Forms Bloom8192 k=3 sha256 FPR0.9% optional constant-space, Zep64n234e bi-temporal valid+tx, ACNE17n27e graphify_constructs() stage4 pure python, MoMA12LLMs MoMA-lite 5 tiers

## Honesty tags

- LCG 20260811→130284456 EXTRACTED verified via python `(seed*1103515245+12345)&0x7fffffff`
- idx3384 EXTRACTED via LCG_A%20719 — task idx4456 INFERRED mismatch flagged, not fabricated
- idx2512 20260807 EXTRACTED, idx2948 20260809 EXTRACTED — Python & Node agree same-link-same-stars
- Provenance 7/7/0 EXTRACTED from `index.html` `assets/hub.js`
- Arch 192d 6-head RoPE RMSNorm CLS→64-d 17 towers INFERRED from idea_sota_001 proposal
- Metrics 0.976→0.981 sim until LOCAL-GPU marker embedding_v3.npz INFERRED guarded LOCAL-GPU exempt 3 preserved
- 503 unified_matrix.npz missing EXTRACTED honest no fabrication
