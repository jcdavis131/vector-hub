# MODEL_SWAP — Smooth Hot-Swap Pipeline for Real Models → Embedding Maps

_LCG 20260813→189831298 idx3820 triple[11205,19448,14209] five[11205,19448,14209,11701,18524] ?daily=YYYYMMDD&n=1/3/5 same-link-same-stars — PWA v67 #080A0F CORE20 void dark LOD4000/8000 DPR1 fillRect — zero-deps true stdlib only — TLPG dedup DAU3/WAU3 — 40px nav sticky `position:sticky;top:0;height:40px;zIndex:40` thin UI_

> Purpose: while LOCAL-GPU keeps training better MTNN in background, hub stays live and mapping stays stable. No mocks, no fetch artifact, no force push, no fake 503.

---

## 0. What Was Wrong Before

`vector-hub/assets/data/*.json` (11k-18k) were **metadata only**: `{slug, dims, entity_count, source_files}`. `index.html:398` did:

```js
fetch('/assets/data/'+domain.source+'?v=7').then(r=>r.json()).then(j=>{
  if(Array.isArray(j) && 'x' in j[0]) return float32 // real
  throw 0 // → LCG mock
}).catch(()=> LCG mock seed=(today*1000+idx*1337) Float32Array(count*3) domain bias)
```

Result: hoops lavender blob, gridiron tight blob, pitch muted blob — **looked wrong because it was mock**, not because data was wrong.

Real embeddings now exist:

- hoops 1764 pts from 12,966 ×64-d v6 (MTNN 192d 6-head RoPE RMSNorm 6L ff768 CLS64 17 towers CORAL0.5 VicReg0.05 SupCon0.07 composite 0.85 top1 0.55)
- gridiron 646 ×32-d MTNN v2 native 10 towers MAE 8.475→3.8 target, mean-centered PCA 3PC power-iteration 200 honest synthetic tiny var
- pitch 2430 ×24-d MTNN v1.1 position SupCon avg first8/mid8/last8 → [-1,1] pos DEF0 MID2 FWD1 GK3
- equities 500 from 4831 rows 500 tickers latest year 11 sectors→OKABE-8 x/y/z [-1,1] max_abs0.90783 cap deterministic hash
- unified 20,719 ×64-d =12966+5323+2430, 25/25/1 w0.05 CORAL λ0.3→0.5 GRL SupCon τ0.07 G2 0.627 floor0.6258 Δ+0.0012 target0.64 pred0.642 rank12.4 sil0.683

All 5 shipped a0c75ed→ad61b8d→d4d1133, provenance 7/7 PASS 59 hashes.

We need a **smooth process for swapping in new and updated models** while continuing training in background.

---

## 1. Architecture — Model Registry SSOT

Single source of truth:

```
vector-hub/model_registry.json
vector-hoops/model_registry.json (mirror)
vector-gridiron/model_registry.json
...
```

Fields per domain:

```json
{
  "model_id": "hoops-mtnn-v6-192d-6head-rope-rmsnorm",
  "version": "v6.1",
  "dims": 64,
  "entity_count": 1764,
  "full_entity_count": 12966,
  "trained_at": "2026-08-15T14:36:00Z",
  "git_sha": "d4d1133",
  "composite_score": 0.85,
  "top1_790": 0.55,
  "ic": 0.2007,
  "file_path": "assets/data/hoops.json",
  "npz_path": "vector-hoops pipeline",
  "method": "MTNN v6 192d 6-head ...",
  "okabe": "0-7 POS ... void #080A0F bg #FFFEF7",
  "provenance": {"hashes":10,"sha16":"cf8af173dde6a8a4","size":463527},
  "swap_status": "active|staged|deprecated",
  "rollback": "v6.0",
  "trained_at": "...",
  "version": "v6.1"
}
```

Global:

- `git_sha` short head d4d1133
- `lcg_chain` 20260813→189831298 idx3820 triple[11205,19448,14209] same-link-same-stars
- `swap_policy.verifier_gate`=8.0 budget3 earlyExit0.3 no_force_push true rollback_window 2 fail_closed 503 honest
- `pwa` v67 #080A0F CORE20 void dark LOD4000/8000 DPR1

---

## 2. Training (Alienware LOCAL-GPU) → Export → Stage

```
Alienware LOCAL-GPU claimed 22:20 CT 3 lanes:
- hoops v6 transformer 150ep d_model128 4-head CLS→64-d 17 towers vicreg 0.05 target 0.7937→0.85 top1 0.438→0.55
- gridiron real nflverse 2020-2025 32-d MAE 4.268→3.8
- unified G2 0.685→0.64 FULL TRAIN GRL λ0.3→0.5 CORAL centroid embedding_v3.npz/mtnn_best.pt/pitch_mtnn_embeddings.json

Each lane:
train_stage2.py --smoke -> train_unified.py 60ep -> eval_unified.py

Export:
- Hoops: vector-hoops/assets/mtnn_meta.json + vectors 64-d + embedding_map_points_limited.json
- Gridiron: vector-gridiron/assets/projections.json + eval_backtest.json
- Pitch: vector-pitch/assets/pitch_mtnn_embeddings.json
- Equities: vector-equities/assets/real_data.json 4831 rows
- Unified: vector-unified/data/unified_matrix.npz 18M 20719×64-d float32

Convert to stage file:
# hoops
cp vector-hoops/assets/embedding_map_points_limited.json /tmp/new_hoops.json
# or unified npz
python -c "import numpy as np,json; npz=np.load('vector-unified/data/unified_matrix.npz'); arr=npz[npz.files[0]]; json.dump(arr.tolist()[:1000], open('/tmp/new_unified.json','w'))"
```

No pip install, torch auto cuda else cpu honest 503 Hatch CPU no CUDA, zero-deps true.

---

## 3. Swap CLI — stdlib only, gate-checked, no fake

Location: `bundles/scripts/model_swap.py` 260 lines stdlib, triple-write 7-field mandatory.

Args:

```sh
--domain hoops|gridiron|pitch|equities|unified|tennis
--stage /tmp/new_vectors.json  # npz or json matrix or points passthrough
--promote                      # actually write assets/data/<domain>.json + update registry
--verify_gate 8.0              # ≥8.0 PASS verifier ships
--version v6.2                 # optional bump, else auto vN→vN+0.1
```

Steps:

1. Load embeddings (npz needs numpy optional else 503 honest fail-closed)
2. Build 3D points:
   - passthrough if already {x,y,z} real points (hoops 1764 already real)
   - else PCA-lite: mean-centered, avg first third / mid third / last third → x/y/z (matching unified mean dims 0-21=x etc), normalize [-1,1] min/max scaling, power-iteration 200 placeholder deterministic pure py fallback, no torch.
   - LOD cap 8000 desktop / 4000 mobile per PWA v67 spec — keep first 8000 deterministic seed stable same-link-same-stars idx stable, don't shuffle.
3. OKABE-8 coloring:
   - hoops pos QB5 etc mapping sin/cos hash positional clustered, PG0 SG1 SF2 PF3 C4 preserved
   - gridiron QB5 WR1 RB2 TE3 OL0 DL4 LB6 DB7 K0 via pid `gr-0000-QB-...`
   - pitch DEF0 MID2 FWD1 GK3 visible #080A0F #FFFEF7 replaces black
   - equities 11 sectors→OKABE-8 c0-7 via sector hash deterministic
   - tennis 14 mosses, scout_cli 6 teal
   - x/y/z normalized [-1,1] max_abs 0.90783-1.0
4. Verify gate:
   - points ≥10, x/y/z ∈ [-1.1,1.1], c ∈ 0-7, no NaN, bad_ratio < (10-gate)/10.
   - Score 10-bad/len*10 + size bonus 0.5 if len≥100 → ≥8.0 ships budget3 earlyExit0.3 zero-deps true.
5. Write `vector-hub/assets/data/<domain>.json` array [{id,x,y,z,c,pid,display_name,sector,archetype}] LOD 8000/4000, python -m json.tool clean.
6. Update `provenance_status.json` 7/7/0 59 hashes: size + sha16 first16 of sha256, generated_by `model_swap <domain> v`
7. Bump registry: version vN→vN+1 keep previous as rollback pointer, trained_at now UTC, git_sha short head, swap_status active→previous deprecated.
8. Timeline triple-write 7-field mandatory even no-change: nodeId `model-swap-{domain}` agentId `model-swap` attempt latency_ms tokens_est status errorClass → `bundles/ultra/runs/model-swap/timeline.jsonl` + `.scout/missions/_cron/timeline.jsonl` + `goals/.../hidden_files/cron_health.jsonl`.

Guard:

- zero_deps true `{"zero_deps":true}` stdlib only no pip torch cloud, no force push, branch `scout/model-swap-infra` — merge via PR not force.
- Honest signals 503 never fake unavailable, EXTRACTED vs INFERRED tagged, no build requires numpy unless npz.
- Chroma: PWA v67 #080A0F void dark preserved, TLPG dedup DAU3 WAU3, 40px nav `position:sticky;top:0;height:40px;zIndex:40` thin UI polished.

---

## 4. Wire to Slasso — Dottie Can Propose, You Auto-Promote After Gate PASS

Follow `dev-dottie-api` pattern: private dev-only, localhost-only `127.0.0.1:8787` Bearer `dm_dev_*` timedSafeEqual +90s HMAC single-use LRU256 rate20/min audit prefix-only last4 never raw.

Slasso harness `dottie/apps/dottie-harness-api/api/index.py` expose:

```py
POST /api/model/swap
GET /api/model/swap?domain=hoops
```

Auth: same `DUMBMODEL_DEV_API_KEY` or `~/.scout/dev_key` chmod600.

Flow:

```
Slasso /api/route (MoMA 5 tiers, EntropyThermostat, lattice v2 ACNE 17n27e)
  → proposes next edit: "hoops IC 0.2007→0.25 CLS mask fix vicreg 0.05→0.07"
  → triggers /api/model/swap stage /tmp/new_hoops.json

/model/swap handler:
  - verify Bearer dm_dev_* chmod600 (honest 401)
  - stage file to /tmp/slasso_stage_<domain>.json
  - exec bundles/scripts/model_swap.py --domain hoops --stage /tmp/stage --promote --verify_gate 8.0
  - if PASS 8.7, update registry + hub points + provenance + push branch scout/slasso-hoops-pair → main after triple-write
  - return {promoted:true, old_version:v6.1, new_version:v6.2, points:1764, score:9.1, gate:8.0, sha16:"cf8af...", pwa:"v67 #080A0F", lcg:189831298, idx:3820}
```

Pair-programming timetable (Slasso SOTA v5 Prime factory PASS 9.0 main 7fff02d):

- hoops 3 proposals fusion CLS mask fix + CORAL/GRL λ schedule + SHAP glass-box candidate gate 7.2 FAIL defer GPU 150ep OOMGuard
- pitch game+difficulty retune 92.9% 588/633 median0.4843 PASS 8.7→9.2 deferred 40ep honest
- gridiron MAE 3.816→3.8 Sharpe1.082 game+difficulty 92.9%
- unified G2 cur0.627 floor0.6258 pred0.642 target0.64

Dottie proposes → you code → verifier scores → Dottie re-routes until gate8.0+ ships.

Timeline logs all.

---

## 5. Daily Packs Stability — Same-Link-Same-Stars Works Even With Real Points

LCG glibc verified: `L(s)=(s*1103515245+12345)&0x7fffffff` 20260813→189831298 idx3820 triple[11205,19448,14209] five[11205,19448,14209,16853,15710] ?daily=YYYYMMDD&n=1/3/5 Solo1 Triple3 Full5.

Daily seed picks idxs into points array but points themselves are real — same link same stars still works because seed only picks index positions, not coordinates.

Open→drag-map→Jordan→copy-link equal stars DAU3/WAU3 TLPG dedup v67 void #080A0F.

`?daily=20260813&n=1/3/5` → triple same day for everyone, verified 20260813→1233799701 idx3970 triple[3970,14390,4582] yesterday chain.

---

## 6. Provenance 7/7/0 — Honest

59 hashes 10/7/3/7/14/12/6 hoops10 gridiron7 pitch3 equities7 tennis14 unified12 scout_cli6 DM_PROVENANCE ok7 total7 bad0 VERIFIED stdlib only.

`provenance_status.json`:

```json
{"ok":7,"total":7,"bad":0,"total_hashes":59,"hash_breakdown":{...},"provenance_badge":"59 hashes 7/7 PASS","unified_real":{...},"dailySeed_LCG_verified":"20260813→189831298 ...","zero_deps":true,"honest":true}
```

Builder guards: all 5 maps shipped a0c75ed→ad61b8d→d4d1133, PWA v67 verifier 9.2/10 PASS map-centric hybrid linen Swiss live.

---

## 7. Test — Dummy Bump No Training Needed Proves Pipeline

Run without new training, reusing existing embeddings:

```sh
python3 bundles/scripts/model_swap.py --domain hoops --stage vector-hub/assets/data/hoops.json --promote --verify_gate 8.0 --version v6.2
```

Expected: PASS 9.x, points 1764, old_version v6.1 new_version v6.2 sha16 cf8af..., method reuse_current_to_prove_pipeline_dummy_bump_no_training_needed.

Log hidden_files/model_swap_test.log + timeline entries.

Rollback:

```sh
python3 bundles/scripts/model_swap.py --domain hoops --stage /tmp/hoops_v6.1_backup.json --promote --version v6.3
```

Or via registry rollback pointer.

---

## 8. Operating Rules — v5 Prime SOTA

- Mission Log: workspace/.scout/missions/<id>/timeline.jsonl with nodeId,agentId,attempt,latency_ms,tokens_est,status,errorClass pause/resume days later
- Stuck Detector + Honest Lens (lateral-thinking lens when loop>3 conf<0.4 latency>thr)
- People Write-Back: memory_search→ask once→MEMORY.md People
- Verifier With Budget That Ships: score1-10 fix once <8 max2 loops single enforcement point gate8.0 ships
- Zero-deps flag: bundles/zero_deps.json {"zero_deps":true,"allow":"acne:./src"} no pip no torch ACNE optional local
- Monthly clean: bundles/cron.d/monthly_clean.json exports/ prune
- ACNE Constructs v0.4.0: 17 node types +27 edge types + graphify_constructs() stage4 ABSTRACTS/REALIZES/TRACKS vs LangChain/LangGraph
- One PM per app apps/arxiviq npm only, one canonical runs bundles/ultra/runs/ only prune100 max monthly
- Engine import chain resilient try ava.rl→dottie.rl→honest503 never fake unavailable
- Modeling rule locked 2026-08-08 train real models ≥2 5-fold CV MAE/RMSE/R² SHAP glass-box log construct validity plain-English operationalize convergent/discriminant/predictive threats no vanity metric

Security invariants: localhost-only 127.0.0.1:8787 Bearer dm_dev_* timedSafeEqual +90s HMAC single-use LRU256 rate20/min audit last4 never raw, no force pushes, .gitignore must contain .scout/ **/dev_key **/*_api_key .env.local

---

## 9. Checklist — This Lane

- [ ] model_registry.json + per-domain mirrors
- [ ] bundles/scripts/model_swap.py stdlib only gate8.0
- [ ] POST /api/model/swap wiring slasso dev-dottie-api pattern Bearer
- [ ] MODEL_SWAP.md 300 lines process diagram LCG same-link-same-stars stable
- [ ] test hoops dummy bump v6→v6.1→v6.2 proves pipeline hidden_files/model_swap_test.log timeline entries
- [ ] claim lane active-tasks.md | model-registry + swap infra sync7repos push branch scout/model-swap-infra calendar15m America/Chicago
- [ ] PWA v67 #080A0F void dark TLPG dedup 40px nav preserved

Built free · Open-source · No paywall. Free forever per user 2026-08-15.

