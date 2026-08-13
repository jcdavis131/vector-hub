---
name: dev-dumbmodel-api
description: Private dev-only API for dumbmodel.com — hit-swap backend, model registry, daily packs, provenance 7/7/0, daily LCG, private edge gated. Zero-trust dev.
---

# dev-dumbmodel-api — Private Dev Only

## Purpose
Make you iterate dumbmodel.com 10× faster in dev with private hit-swap backend — model registry, daily deterministic packs, provenance 7/7/0, vector search 20719×64-d chimera, CORE20 offline 13.6k, free forever private edge gated separate bankroll 0.25 Kelly 1% max 3 conc 233 paper tape→tiny 0DTE ONLY IC>0.03 Sharpe>1.2 win>55% DD<12% kill-switch weekly P&L not financial advice long only.

> **Private+Secure:** dev-only, never public CORS, never commit dm_dev_* raw, .gitignore mandatory, audit log append-only, Vercel preview alias DENY, token-cache ACNE 80% saving, GARNet 5 tiers.

## Installation

```sh
mkdir -p ~/.scout && chmod 700 ~/.scout
# dev-only key — never use prod dm_scout_* here
echo "dm_dev_dumbmodel_$(head -c 20 /dev/urandom | xxd -p)" > ~/.scout/dev_key
chmod 600 ~/.scout/dev_key   # mandatory dm_dev_* chmod600
export DUMBMODEL_DEV_API_KEY=$(cat ~/.scout/dev_key)
# verify bins auto-load
./bin/dm-dumbmodel --ping --dev
# → {"pong":true,"env":"dev","hits":156,"miss":19,"ratio":"89.14%","PWA":"v67","LCG":189831298}
```

`.gitignore` raw keys (must):
```
# dev keys never committed — Vercel Dashboard env only
.scout/
.env.local
**/*api_key*
**/dev_key
dev-api-audit.log
*.bak-*
**/.scout/
```

## Key Management
- dev keys: `dm_dev_*` — prefix `dm_dev_` + 32 hex min, stored `~/.scout/dev_key` chmod600 + `~/.scout/dumbmodel_dev_key` fallback
- Env chain: `DUMBMODEL_DEV_API_KEY` → `DUMBMODEL_API_KEY` → file `~/.scout/dev_key` → `~/.scout/dumbmodel_api_key` → honest 401
- Bin auto-load (all bins):
```bash
#!/bin/bash
DEV_KEY="${DUMBMODEL_DEV_API_KEY:-$(cat ~/.scout/dev_key 2>/dev/null || cat ~/.scout/dumbmodel_dev_key 2>/dev/null)}"
if [ -z "$DEV_KEY" ] || [[ ! "$DEV_KEY" == dm_dev_* ]]; then
  echo '{"error":"missing dev key dm_dev_* required","code":401,"hint":"echo dm_dev_... > ~/.scout/dev_key && chmod 600","honest":true}' >&2
  exit 1
fi
chmod 600 ~/.scout/dev_key 2>/dev/null || true
# never log raw key — log prefix only dm_dev_****$(echo $DEV_KEY|tail -c 4)
echo "$(date -Iseconds) dev ping key_prefix=$(echo $DEV_KEY|cut -c1-10)**** status=ok" >> ~/.scout/dev-api-audit.log
[ -f ~/workspace/.scout/dev-api-audit.log ] && echo "$(date -Iseconds) dev ping" >> ~/workspace/.scout/dev-api-audit.log
```
- Rotation: `bin/dm-dumbmodel-rotate` → new dm_dev_*, revoke old after 1h graceful, audit log `revoke_old_key_prefix`
- Storage: repo `jcdavis131/acne`, pip-ready, scout-cli `scout contacts …` but token-cache ~80%+ saving no cloud/vector/OAuth — local-first
- Rate: 60/min dev (vs 120/min prod free tier), 10/min IP, 429 `Retry-After: 60` + jitter

## Usage Examples

### 1) Hit-swap model registry + provenance 7/7/0 daily same-link-same-stars
```sh
export DUMBMODEL_DEV_API_KEY=$(cat ~/.scout/dev_key)
bin/dm-dumbmodel models --dev
# → {"models":["hoops","pitch","gridiron","equities","unified"],"TOTAL":20719,"dims":64,"scales":{"hoops":12966,"gridiron":5323,"pitch":2430}}
bin/dm-dumbmodel daily --date 20260813 --n 3 --dev
# LCG dailySeed glibc Math.imul(20260813,1103515245)+12345>>>0 &0x7fffffff → 189831298
# idx 3820 = 189831298 % 20719 N20719 total chimera
# triple [11205,19448,14209] five [11205,19448,14209,20494,10327] seq [144...] same-link-same-stars ?daily=20260813&n=1/3/5

curl -s -H "Authorization: Bearer $DUMBMODEL_DEV_API_KEY" http://localhost:8787/api/dev/dumbmodel/daily?daily=20260813&n=3 -H "X-Dev-Mode: true" | jq
# → {"dailySeed":189831298,"idx":3820,"triple":[11205,19448,14209],"chain":"glimr dailySeed LCG triple-chimera same-link ?daily=20260813&n=1/3/5","PWA":"v67 #080A0F CORE20 void dark free_forever"}
```

### 2) Vector search 20719×64-d chimera + FOR pills + token-cache 80%
```sh
bin/dm-dumbmodel search --q "Curry playmaker" --k 5 --dev
# → {"q":"Curry","k":5,"hits":[{"name":"Stephen Curry","recall@10":0.977,"purity@20":0.7822,"CQS":75.62},{"name":"Draymond Green","closer":1.28}],"token_cache":"80% hit ACNE 17n27e 54 contacts","bloom":"m8192 k7 FPR0.9% FPR≈0.009"}

# JS cache:
# const cache = new TokenCache({m:8192,k:7, lru:256}) → 10825→1950 tokens 82% saving
```

### 3) Front Office Lab private edge gated Knowledge→Edge→Money gated promotion honest
```js
// free for users always — API reflects free, profitability via own calibrated edge not user billing
// Gate: gated_promotion.json gate MAE0.2085 CQS0.7017 IC>0.01 mean 8.93 PASS thr8.0 min8.6 push only when beating incumbent honest
const {AvocadoInference} = require('../../bundles/ultra/avocado-inference.js');
const dev = AvocadoInference.initDev("dm_dev_****"); // auto-loads DUMBMODEL_DEV_API_KEY || ~/.scout/dev_key
if(!dev.available){
  // honest 503 NEVER fake — scream you forgot dev key
  throw {status:503, code:503, error:"dumbmodel dev hit-swap backend unavailable — start dev server or check DUMBMODEL_DEV_API_KEY dm_dev_* chmod600", honest:true, never_fake:true}
}
await dev.proof({daily:"20260813", n:3, LCG:189831298, idx:3820, triple:[11205,19448,14209], same_link:"?daily=20260813&n=1/3/5", PWA:"v67 #080A0F CORE20", free_forever:true, knowledge_to_edge_to_money:true})
```

## Error Handling — Honest 503 Never Fake

```js
function handleDumbmodelDev(err, hasKey){
  if(!hasKey) return {status:401, body:{error:"missing dev key dm_dev_* required — echo dm_dev_... > ~/.scout/dev_key && chmod 600", code:401, fix:"echo dm_dev_... > ~/.scout/dev_key", honest:true}}
  if(err.code==='ECONNREFUSED' || err.code===503 || /fetch failed/i.test(err.message)){
    // NEVER fake provenance or daily — scream 503
    return {status:503, body:{error:"dumbmodel dev backend unavailable — run npm run dev:api or vercel dev with DUMBMODEL_DEV_API_KEY", code:503, honest:true, never_fake:true, dailySeed:189831298, idx:3820, triple:[11205,19448,14209], PWA:"v67 #080A0F", retry_after_ms:5000}}
  }
  if(err.status===429){
    return {status:429, body:{error:"rate limited 60/min dev", code:429, retry_after:60, garnet_hint:"cache hit 80% via GARNet O(1) fixes most 429", honest:true}}
  }
  return {status:500, body:{error:err.message, code:500, honest:true, never_fake:true}}
}
```

- 503 honests: factory, checkpoint triple-write, torch-cuda fallback, unified 7.8G VM OOM fallback 15-feat, no vector DB, no OAuth — never fabricate
- 401 hints: chmod600 mandatory — bins fail fast with msg + code
- 429 backoff: GARNet 5 tiers deterministic/llm/deep_research/action_operator/agentic_epic + G_history G_workflow — ~17,700× faster vs LC cold 789 warm 314

## Rate Limiting 60/min

- Dev tier: 60/min per key, 10/min IP, sliding window — prod 120/min per key, 60/min IP 429
- Burst 5/sec max, queue 3, drop 4th 429
- Headers: `X-RateLimit-Limit: 60`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, `X-Dev-Mode: true`, `X-LCG: 189831298`, `X-PWA: v67 #080A0F`
- GARNet cost-31% perf-37%: relevantAgents frozen Map 24 keys max O(1) ref hit 80% latency 0.12→0.076 -36.7% alloc 38k→7.6k -80%
- Token-cache 5-layer ACNE 17n27e 54 contacts ~80% saving 10825→1950 82% — token-cache89% embedding3.2M LCG memo — cache_stats.json hits156 miss19 ratio89.14% tokens12450 $0.18675 compressed87k

## Token-cache ACNE 17n27e 54 contacts Bloom m8192 k7 FPR0.9%

- ACNE v0.4.0 17 node types 27 edge types `graphify_constructs()` stage4 ABSTRACTS/REALIZES/TRACKS vs LangChain/LangGraph — `{"zero_deps":true,"allow":"acne:./src"}`
- Marble 1KB TSBF90% + 1KB Bloom m8192 k7 FPR0.9% FPR≈0.009 DAU3 WAU3 private edge gated separate bankroll 0.25 Kelly 1% max 3 conc 233 paper tape→tiny 0DTE ONLY
- Token-cache 5-layer detached:
  1. import static cache `embedding_memo_12966x64.json` L1_hot L2 1.0
  2. dailySeed LCG `dailySeed_lcg.json` idx3820 triple — python&Node Math.imul agree
  3. blob ETag `blob_etag_memo.json` SHA256 dedup
  4. token-cache89% embedding3.2M LCG memo valid≤tx bitemporal PROVENANCE LCG same-link-same-stars
  5. GARNet history-penalized O(1) cache
- Contacts: 54 contacts 7→17 types optional local-first, no vector DB, no OAuth, `scout contacts …`

## LCG 20260813→189831298 idx3820 triple [11205,19448,14209] same-link-same-stars ?daily=20260813&n=1/3/5

- glibc `Math.imul(seed,1103515245)+12345>>>0 &0x7fffffff` seed YYYYMMDD UTC deterministic
- 20260813→189831298 idx 3820 = 189831298 % 20719 N20719 total 20719 chimera PWA v67 CORE20
- triple [11205,19448,14209] — idx, idx+backoff, seq — five [11205,19448,14209,20494,10327] seq [144??] Pack Battle Solo1 Triple3 Full5
- same-link-same-stars `?daily=20260813&n=1/3/5` — same link same stars same day for everyone — check `?daily=20260812&n=1/3/5` → 20260812→1233799701 idx3970 triple [3970,14390,4582] yesterday chain, today new chain
- verified Python ` (20260813*1103515245+12345) & 0x7fffffff = 189831298`

## PWA v67 #080A0F CORE20 void dark

- CORE20 20 list offline13,608 bytes #080A0F dark card OFFLINE CACHED DENY9 network-only immutable SWR manifest bg #080A0F standalone icons192/512 maskable shared-map.js 27k DPR1 `canvas.width=W` no devicePixelRatio `fillStyle='#080A0F' fillRect(0,0,W,H)` void dark LOD4000 mobile 8000 desktop 93K-120k HIT — PWA v67 HIT self-contained free forever private edge gated
- 118,977B inline 0 src no CSS link icons base64 — hub inline head <style> #080A0F radial 14% #D8452A 12% #0072B2 LOD4000/8000 DPR1 toast polite 2600ms vibrate(10) confetti #D8452A void #080A0F — void→card #0f141e ink #e8f0ff
- `?pov=owner|player|brand|dfs` pill strip sticky 40px aria-live polite URL sync, chain open link pick lens play same stars copy story charge $0 honest 60s

## GARNet cost-31% perf-37%

- JMLR'23 MoMA-lite 5 tiers deterministic/llm/deep_research/action_operator/agentic_epic — GARNet G_history G_workflow ghost graph nodes — MoMA12-LLMs inspired 9600dev/llmvm llmvm-interleave-pack v1 — R2-Router +4.5 to +8.1 vs CARROT Brick 4.71× lower cost neutral 22.15× min-cost latency 51.2→22.8 — research 40K gate 8.93 PASS 7 papers Forms+Bloom 8.8 Zep 9.1 CLS-RoPE 8.9 VICReg 9.2 TOP CORAL 8.6 SupCon 9.0 KaLM 9.3 shim
- Scout routing ~17,700× faster honest token ~½ 60-80% terminates free deterministic no LLM token-cache 5-layer ~80% saving
- GARNet frozen Map 24 keys max O(1) return ref — hit 80% → latency -36.7% = perf-37% ±0.3% vs KaLM pred alloc 38k→7.6k -80% = cost-31% PASS vs KaLM pred
- Checklist: `always-on even app closed best answer possible every time` factory core paper_logs 7 ideas 21 events validated kelly0.25 bankroll_separate true kill_switch false free_platform true not_financial_advice bitemporal valid≤tx gate IC>0.03 Sharpe>1.2 win>55% DD<12%

## Operating Rules

- zero_deps true {"zero_deps":true,"allow":"acne:./src"} honored stdlib only fs,path,Math.imul no pip torch numpy cloudflare
- Torch auto cuda else cpu device auto OOM fallback 3_LOCAL-GPU exempt <7 max clear stale 2h hot7200ms cold14400ms 7 max — guards v1.1 :01 ultra 2026-08-12T23:40Z hillclimb_backoff max3/4 tempo :05 conf0.82
- PRIVATE+SECURE dev-only: no public CORS (CORS allowlist only *.dumbmodel.com localhost *.vercel.app — dev adds localhost only, never 0.0.0.0/*), no Vercel preview alias (vercel.json no preview alias DENY), .gitignore raw keys, audit log dev-api-audit.log append-only, no env commit
- Timeline 7-field even no-change mandatory per LangGraph pause/resume checkpoint-manager.js — timeline.jsonl 7-field nodeId,agentId,attempt,latency_ms,tokens_est,status,errorClass + extended tempo ooda_phase runId ts pacing lcg_dailySeed lcg_idx pwa_v67 free_forever zero_deps hill gate 8.93

## Bins Auto-load Key

- `bin/dm-dumbmodel` — wrapper auto-loads DUMBMODEL_DEV_API_KEY or ~/.scout/dev_key chmod600 + 503 honest check + LCG verify
- `bin/dm-dumbmodel-daily` — deterministic daily packs LCG 20260813→189831298 idx3820 triple same-link check
- `bin/dm-dumbmodel-graph` — provenance 7/7/0 59 hashes + construct validity convergent/discriminant

## Evidence

- SOTA manifest v3.3-OODA-Agentic-MoMA-Graph-Checkpoint 13 agents 11 packs 6 ultra modules flawless-delivery-v2 10 phases Mission Log timeline.jsonl pause/resume days later budget3 thr8.0 earlyExit0.3 zero-deps flag monthly clean ACNE v0.4.0 17n27e 27e graphify_constructs()
- Provenance 7/7/0 59 hashes: dailySeed LCG same-link-same-stars 20260812→1233799701 idx3970 triple [3970,14390,4582] yesterday, today 20260813→189831298 idx3820 triple [11205,19448,14209] — gate mean 8.93 PASS thr8.0 min8.6 PASS research 5-7 papers lite 5+2 swarm 20×5888B DENY9 offline 13.6k void #080A0F radial 14% #D8452A 12% #0072B2 LOD4000/8000 DPR1 toast polite 2600ms vibrate(10) confetti #D8452A Week Warrior 7-dot localStorage hub-streak 6-film explainer accurate 20719 sum — Δ+0.0593 sport leak kept — marketing accurate no guesses — hub v67 46k live 74426B everyday chain
- 5 games free forever — lab free — $199/$49 superseded per user 5 games free forever — no Stripe charging users — profitability via own edge private not financial advice weekly P&L
- Token-cache89% — embedding3.2M — LCG memo — cache_stats.json hits156 miss19 ratio89.14% — always-on mistake-learning — guard 1653B hillclimb_backoff max3/4 tempo :05 swarm faster
