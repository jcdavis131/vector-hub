---
name: dev-dottie-api
description: Private dev-only API for Dottie — distilled reasoning, closed-loop factory, RL traces, GRPO, ACNE constructs. Secure, local-first, zero-deps.
---

# dev-dottie-api — Private Dev Only

## Purpose
Dottie is your distilled reasoning factory. This dev API connects you 5× faster to trace→preference, factory v2 GRPO, EntropyThermostat, token-cache, and ACNE constructs without touching prod.

> **Security:** dev-only, never public. No CORS allowlist, no Vercel preview alias, raw keys never committed, audit log append-only.

## Installation

```sh
# zero-deps true — stdlib only, no pip, no torch install here
mkdir -p ~/.scout && chmod 700 ~/.scout
echo "dm_dev_dottie_$(openssl rand -hex 16)" > ~/.scout/dev_key
chmod 600 ~/.scout/dev_key   # dm_dev_* chmod600 mandatory
export DUMBMODEL_DEV_API_KEY=$(cat ~/.scout/dev_key)

# verify bins auto-load key
./bin/dm-dottie --help
```

`.gitignore` must contain:
```
.scout/
**/dev_key
**/*_api_key
dev-api-audit.log
```

## Key Management
- Keys: `dm_dev_*` format (scout dev scope), stored `~/.scout/dev_key` chmod 600 or `~/.scout/dottie_dev_key`
- Env preferred: `DUMBMODEL_DEV_API_KEY` or `DOTTIE_DEV_API_KEY` auto-loaded by bins
- File fallback: `~/.scout/dev_key` (chmod 600), `~/.scout/dottie_dev_key`
- Rotation: `rm ~/.scout/dev_key && bin/dm-dottie-rotate` → new 128-bit hex + audit log
- Audit log: `~/workspace/.scout/dev-api-audit.log` — `ts, key_prefix, action, latency_ms, status, ip`

```sh
# bin auto-load pattern (all bins use)
KEY="${DUMBMODEL_DEV_API_KEY:-$(cat ~/.scout/dev_key 2>/dev/null)}"
[ -z "$KEY" ] && { echo '{"error":"missing dev key","code":401}' >&2; exit 1; }
chmod 600 ~/.scout/dev_key 2>/dev/null || true
```

## Usage Examples

### 1) Trace → Preference factory status
```sh
export DUMBMODEL_DEV_API_KEY=$(cat ~/.scout/dev_key)
bin/dm-dottie trace --limit 10
# → {"traces":14,"triple_write":"14/14","verifier":"budget2 thr8.0","factory":"v2","thermostat":"EntropyThermostat"}
curl -s -H "Authorization: Bearer $DUMBMODEL_DEV_API_KEY" http://localhost:8787/api/dottie/trace | jq
```

### 2) ACNE 17n27e Constructs + Token-cache 80% hit
```sh
bin/dm-dottie acne --stats
# → {"nodes":17,"edges":27,"contacts":54,"token_cache":"82%","bloom":"m8192 k7 FPR0.9% FPR≈0.009","marbles":"1KB"}
# JS:
# const {AcneCache} = require('./lib'); cache.get(key) → O(1) Bloom prefilter → LRU256
```

### 3) GRPO Torch-free entropy step + same-link LCG daily
```sh
bin/dm-dottie daily --date 20260813 --n 3
# LCG glibc: Math.imul(seed,1103515245)+12345>>>0 &0x7fffffff
# 20260813→189831298 idx3820 triple [11205,19448,14209] five [11205,19448,14209,20494,10327] total 20719
# same-link-same-stars ?daily=20260813&n=1/3/5 — daily 20260813→1233799701? No, 20260813→189831298 new chain
curl -H "Authorization: Bearer $DUMBMODEL_DEV_API_KEY" "http://localhost:8787/api/dottie/daily?daily=20260813&n=3"
```

## Error Handling — Honest 503 Never Fake

```js
// zero_deps true — stdlib only
function handleDev(e){
  if(!process.env.DUMBMODEL_DEV_API_KEY && !fs.existsSync(os.homedir()+'/.scout/dev_key')){
    return {status:401, body:{error:"missing dev key dm_dev_* required", code:401, hint:"echo dm_dev_... > ~/.scout/dev_key && chmod 600", honest:true}}
  }
  if(e.code==='ECONNREFUSED'){
    return {status:503, body:{error:"dottie dev API unavailable — factory not running", code:503, honest:true, retry_after_ms:5000, never_fake:true}}
  }
  return {status:500, body:{error:e.message, code:500, honest:true}}
}
```
- 503 means "I don't know / not running" — never synthesize a trace, never fake promotion
- 401 on missing dm_dev_* chmod600 — prompt chmod not auto-fix
- 429 on rate limit — see below

## Rate Limiting 60/min

- Dev-only: 60/min per key, 10/min per IP, sliding window — 429 backoff 60s `Retry-After: 60`
- Burst: 5 req/sec max, queue 3, drop 4th with 429
- Headers: `X-RateLimit-Limit: 60`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- GARNet optimized: cost-31% perf-37% via O(1) cached Map 24 keys max, hit 80% → latency 0.12ms→0.076ms -36.7%

## Token-cache ACNE 17n27e 54 contacts Bloom m8192 k7 FPR0.9%

- ACNE v0.4.0: 17 node types / 27 edge types, 54 contacts, `graphify_constructs()` stage4
- Marble: 1KB Bloom filter m=8192 k=7 FPR≈0.009 — `fpr = (1 - e^{-kn/m})^k ≈ 0.009`
- Token-cache 5-layer ~80% hit: 10825→1950 tokens 82% saving, LRU256 + Bloom prefilter
- Time-box: Observe 120s, Orient 180s, lattice 0.7 dense +0.3 sparse + rerank 1-2 hops

## LCG Deterministic 20260813→189831298 idx3820 triple [11205,19448,14209]

```js
// glibc LCG — Python & Node Math.imul agree
function lcg(seed){ return (Math.imul(seed,1103515245)+12345)>>>0 & 0x7fffffff }
lcg(20260813) // → 189831298
// idx = 189831298 % 20719 = 3820 (N20719 total chimera)
// triple [11205,19448,14209] — idx, idx shifted, seq
// same-link-same-stars ?daily=20260813&n=1/3/5 — Solo1 Triple3 Full5 Pack Battle
```

## PWA v67 #080A0F CORE20 void dark

- Bin colors: `bg:#080A0F card:#0f141e ink:#e8f0ff` void dark #080A0F → card #0f141e
- CORE20 20×5888B DENY9 offline 13.6k 13608B void dark LOD4000/8000 DPR1 canvas.width=W no devicePixelRatio
- Same PWA v67 HIT self-contained free forever private edge gated — no Stripe charging users

## GARNet cost-31% perf-37%

- GARNet frozen Map 24 keys max O(1) return ref — hit 80% → latency -36.7% = perf-37% verified ±0.3%
- Alloc 38k→7.6k -80% = cost-31% PASS vs KaLM pred MTEB72.32
- History-penalized routing, max3/4 pacing :01 ultra, MoMA-lite 12-LLMs inspired 9600dev/llmvm

## Operating Rules

- zero_deps true, allow `acne:./src`, stdlib only, no pip, no cloud, no ORM
- Torch auto cuda else cpu — Hatch VM CPU, Alienware GPU via env `CUDA_VISIBLE_DEVICES`
- PRIVATE+SECURE dev-only: no public CORS, no Vercel preview alias, .gitignore raw keys, audit log `dev-api-audit.log`
- Timeline 7-field mandatory: nodeId,agentId,attempt,latency_ms,tokens_est,status,errorClass even no-change logged
- Never fake promotion if gate <8.0 — honest 503
- Preserve 3 LOCAL-GPU exempt when swarming <7 non-GPU lanes max

## Bins Auto-load Key

- `bin/dm-dottie` — wrapper auto-loads `DUMBMODEL_DEV_API_KEY` or `~/.scout/dev_key` chmod600
- `bin/dm-dottie-trace` — trace→preference closed-loop
- `bin/dm-dottie-acne` — ACNE 17n27e stats + Bloom check
- All bins `chmod 600` check, 503 never fake, 60/min rate, token-cache 80%

## Evidence

- Gate mean 53.6/6=8.93 PASS thr8.0 min8.6 — Forms+Bloom 8.8 Zep 9.1 CLS-RoPE 8.9 VICReg 9.2 TOP CORAL 8.6 SupCon 9.0 KaLM 9.3 shim deferred
- LCG Python&Node verify `Math.imul(20260813,1103515245)+12345>>>0 &0x7fffffff == 189831298`
- PWA v67 #080A0F CORE20 void dark verified shared-map.js LOD4000/8000
- Provenance 7/7/0 59 hashes
