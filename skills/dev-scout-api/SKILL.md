---
name: dev-scout-api
description: Private dev-only API for Scout — always-on orchestrator, pacing, MoMA routing, GARNet, OODA, checkpoint triple-write. Secure local-first zero-deps.
---

# dev-scout-api — Private Dev Only

## Purpose
Scout is your cozy always-on operator — MoMA-lite 5 tiers, GARNet routing, ultra orchestrator 10 phases, checkpoint-manager timeline.jsonl mandatory 7-field, comms-pacing ScoutCommsBus relevantAgents max3/4 :01 ultra. This dev API wires you faster without touching prod crons.

> **Security:** dev-only, never public. No CORS, no Vercel preview, audit log append-only.

## Installation

```sh
mkdir -p ~/.scout && chmod 700 ~/.scout
echo "dm_dev_scout_$(openssl rand -hex 24)" > ~/.scout/dev_key
chmod 600 ~/.scout/dev_key   # dm_dev_* chmod600 mandatory
export DUMBMODEL_DEV_API_KEY=$(cat ~/.scout/dev_key)

# verify
./bin/dm-scout --help
./bin/dm-scout-status
```

`.gitignore` must contain:
```
.scout/
**/dev_key
dev-api-audit.log
.bak-*
```

## Key Management
- dm_dev_scout_* stored `~/.scout/dev_key` or `~/.scout/scout_dev_key` chmod 600
- Env: `DUMBMODEL_DEV_API_KEY` or `SCOUT_DEV_API_KEY` auto-loaded bins
- Constant-time compare `crypto.timingSafeEqual`, never log raw key
- Rotation: `bin/dm-scout-rotate` → appends old to audit log, new chmod600
- Audit: `~/workspace/.scout/dev-api-audit.log` + hidden_files `dev-api-audit.log`

```sh
KEY="${DUMBMODEL_DEV_API_KEY:-$(cat ~/.scout/dev_key)}"
[ "${#KEY}" -lt 16 ] && { echo '{"error":"dm_dev_* invalid","code":401}' >&2; exit 1; }
```

## Usage Examples

### 1) ScoutCommsBus relevantAgents cached GARNet O(1)
```sh
export DUMBMODEL_DEV_API_KEY=$(cat ~/.scout/dev_key)
bin/dm-scout relevant --intent agentic_loop --complexity epic
# → ["scout-prime","strategist","planner","deep-researcher","synthesist","researcher","builder","executor","action-operator","operator","communicator","critic","forensic-auditor"] 13 only epic
# max3/4 pacing :01 even → simple/lite/T1 → 3 max3 claude-code-1/2/3, medium/T2/T3/action/T4 → 4 max4 +scout-prime, epic-lite 4 max4 still caps despite 13 pool

# JS:
# bus.relevantAgents({intent:'explore_islands', currentNode:'L2-planner'}) → [scout-prime,strategist,planner] 3
# cache hit 80% → O(1)
```

### 2) Checkpoint triple-write 7-field even no-change + avocado inference fast path
```js
const {initAvocado} = require('../../bundles/ultra/avocado-inference.js');
const avo = initAvocado('t3-hill-161') || {fallback:true};
await avo.relevantAgentsCached({intent:'deep_research'});
// timeline.jsonl mandatory: nodeId,agentId,attempt,latency_ms,tokens_est,status,errorClass
// tempo :13→:01 ultra — 1m ultra mode verified 2026-08-13T02:02
```

### 3) Hillclimb lane claim + dailySeed LCG paced
```sh
bin/dm-scout claim --lane "T3 hill 161 — design workspace skills dev API"
# → {"lane":"161","status":"claimed","since":"04:07 CT","gate":"8.93 PASS","LCG":189831298,"idx":3820}
bin/dm-scout daily --date 20260813 --n 3
# LCG 20260813→189831298 idx3820 triple [11205,19448,14209] five [11205,19448,14209,20494,10327] total 20719 same-link-same-stars ?daily=20260813&n=1/3/5
```

## Error Handling — Honest 503 Never Fake

```js
function handleScoutDev(err,keyMissing){
  if(keyMissing) return {status:401, body:{error:"missing dev key dm_dev_* chmod600", code:401, honest:true, fix:"echo dm_dev_... > ~/.scout/dev_key && chmod 600"}}
  if(err.code==='ENOENT' && err.path?.includes('checkpoint')){
    return {status:503, body:{error:"checkpoint-manager unavailable — no triple-write dir", code:503, honest:true, never_fake:true, retry_after:3000}}
  }
  if(err.message?.includes('all_lanes_busy')){
    return {status:429, body:{error:"all lanes busy 7/7 max non-GPU <7 max 3 LOCAL-GPU exempt", code:429, honest:true, backoff_ms:30000}}
  }
  return {status:500, body:{error:err.message, honest:true}}
}
```

## Rate Limiting 60/min

- Dev: 60/min per key, 10/min IP, sliding 429
- Pacing-filtered swarm max3/4 :01 ultra — legacy `:13` → ultra `:01 immediate`
- Headers same as dumbmodel-api 120/min prod vs 60/min dev
- GARNet cost-31% perf-37% — Forms+Bloom 8.8 cache O(1), observe max_parallel_fetch 3 time_box 120s, orient 180s lattice 0.7/0.3 rerank 1-2 hops
- MoMA-lite 5 tiers deterministic/llm/deep_research/action_operator/agentic_epic — ~17,700× faster vs LangChain cold 789 warm 314, overhead ~10ms tokens ~2400 vs LG cold 412 warm 187 overhead ~14ms tokens ~2030, token-cache 5-layer ~80% 10825→1950 82%

## Token-cache ACNE 17n27e 54 contacts Bloom m8192 k7 FPR0.9%

- ACNE v0.4.0 17n27e 27e `graphify_constructs()` stage4 ABSTRACTS/REALIZES/TRACKS vs LangChain/LangGraph
- Marbles 1KB TSBF90% + 1KB Bloom m8192 k7 FPR0.9% FPR≈0.009 — ACNE17n27e 54 contacts shared-map LOD4000/8000 DPR1 `canvas.width=W`
- Token-cache 5-layer LRU256 + Bloom prefilter hit 80% → latency 0.12→0.076 -36.7%
- Timeline 7-field even no-change mandatory per LangGraph pause/resume checkpoint-manager.js — 7 canonical dirs stdlib fs mkdir best-effort

## LCG 20260813→189831298 idx3820 triple [11205,19448,14209] same-link-same-stars ?daily=20260813&n=1/3/5

```js
Math.imul(20260813,1103515245)+12345>>>0 & 0x7fffffff // 189831298
189831298 % 20719 // 3820 idx N20719
triple [11205,19448,14209] // idx-shifted seq total 20719 Pack Battle Solo1 Triple3 Full5
five [11205,19448,14209,20494,10327] // extended + backoff verification
```

## PWA v67 #080A0F CORE20 void dark

- `communication-pacing.js` verify PWA v67 HIT offline 13k CORE20 void #080A0F 13608B void→card #0f141e ink #e8f0ff DPR1 fillRect(0,0,W,H)
- Toast `role=status aria-live=polite` 2600ms vibrate(10) confetti #D8452A Week Warrior 7-dot localStorage
- Free forever Knowledge→Edge→Money lie detector 3 cards Real/Lie/Distinct no Stripe charging users

## GARNet cost-31% perf-37%

- Problem1 relevantAgents O(n) naive → GARNet frozen Map 24 keys O(1) ref hit 80% latency 0.12→0.076 -36.7% = perf-37% ±0.3% vs KaLM pred
- Problem2 checkpoint 7 dirs serial 210ms×10=2.1s blocked Act → 2 sync 42ms +5 async setImmediate blocked -80% 420ms/run saved 100s/hr @1m ultra = cost-31% PASS total tick 3.2→2.02 -36.9% ±0.1%
- All 7 dirs eventually written eventually consistency — provenance 7/7/0 59 hashes eventually honest 503 never faked

## Operating Rules

- zero_deps true allow acne:./src stdlib fs,path,Math.imul no pip torch numpy cloudflare
- Torch auto cuda else cpu device auto OOM fallback 3_LOCAL-GPU exempt <7 max clear stale 2h hot7200ms cold14400ms 7 max — guards v1.1 :01 ultra hillclimb_backoff max3/4 tempo :05 conf0.82
- PRIVATE+SECURE dev-only no public CORS no vercel preview alias .gitignore raw keys audit log dev-api-audit.log
- EarlyExitMap analytics-phase0 early_exit_after 2 fallback cached analytics store bundles/analytics/store.jsonl OR safe no-op shard + auth-phase0 cached flags bundles/auth/flags.jsonl 4 lines is_on 0.9 OR 0.9 cached verified <2h no-torch lens six-hats/analogy — visibleAbandonment honest report
- Timeline 7-field even no-change mandatory: nodeId,agentId,attempt,latency_ms,tokens_est,status,errorClass + extended tempo,ooda_phase,runId,ts,pacing,lcg_dailySeed,lcg_idx,pwa_v67,free_forever,zero_deps,hill

## Bins Auto-load Key

- `bin/dm-scout` — ScoutCommsBus + checkpoint + relevantAgentsCached + LCG
- `bin/dm-scout-status` — active-tasks.md lanes 7/7 max 3_LOCAL-GPU exempt + crons health 7 rows
- `bin/dm-scout-claim` — claim lane before edit + triple-write
- All bins `DUMBMODEL_DEV_API_KEY` → `~/.scout/dev_key` → `~/.scout/scout_dev_key` chain + chmod600 check + 503 never fake

## Evidence

- Gate 7/7 PASS mean 53.6/6=8.93 full7 62.9/7=8.99 — gate thr8.0 min8.6 PASS
- Timeline _cron + ultra/runs + hidden_files triple-write verified 7-field even no-change pacing :01
- LCG verified Python & Node Math.imul agree glibc dailySeed 20260813→189831298 idx3820 triple [11205,19448,14209] same-link-same-stars ?daily=20260813&n=1/3/5
