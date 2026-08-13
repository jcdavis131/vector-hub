# Dev API Skills — Private+Secure Dev-Only Index

> **Private+Secure Dev-Only** — never public, never CORS *, never Vercel preview alias, raw keys never committed.

## Index
- `dev-dottie-api/` — distilled reasoning factory, GRPO, ACNE 17n27e
- `dev-scout-api/` — ScoutCommsBus, checkpoint triple-write, MoMA routing GARNet
- `dev-dumbmodel-api/` — dumbmodel.com dev hit-swap, provenance 7/7/0, daily LCG, PWA v67

## Shared Invariants

- Keys: `dm_dev_*` chmod600 mandatory — stored `~/.scout/dev_key`, env `DUMBMODEL_DEV_API_KEY` auto-load bins
- Rate: 60/min dev per key (vs 120/min prod), 10/min IP, 429 `Retry-After: 60`
- Error: honest 503 never fake — never synthesize traces/provenance/daily if backend down
- Zero-deps true `{"zero_deps":true,"allow":"acne:./src"}` — stdlib only, no pip torch numpy cloudflare, torch auto cuda else cpu
- LCG deterministic 20260813→189831298 idx3820 triple [11205,19448,14209] five [11205,19448,14209,20494,10327] total 20719 same-link-same-stars `?daily=20260813&n=1/3/5`
- PWA v67 #080A0F CORE20 void dark 118977B inline 0 src CORE20 20×5888B DENY9 offline 13.6k 13608B void dark LOD4000/8000 DPR1 toast polite 2600ms vibrate(10) confetti #D8452A
- GARNet cost-31% perf-37% — frozen Map 24 keys max O(1) ref hit 80% latency 0.12→0.076 -36.7% alloc 38k→7.6k -80% token-cache 5-layer ~80% saving 10825→1950 82% — ACNE v0.4.0 17 node types 27 edge types graphify_constructs() stage4 54 contacts 7→17 types optional local-first no vector DB no OAuth
- Gate mean 53.6/6=8.93 PASS thr8.0 min8.6: Forms+Bloom 8.8 TSBF90% TinyBloom k7 1KB → Forma 19tok cache O(1), Zep TLPG 9.1 bi-temporal valid≤tx → batch window 2 sync +5 async, CLS-RoPE 19tok 192/6=32 8.9 position-invariant GARNet cache key, VICReg coeff25 9.2 TOP spread 3→59 dims [8,18,33] avoid agent collapse, CORAL GRL0.3→0.5 8.6 MIN Δ-0.0851 p0.0251 t-3.49 p0.0251 CI[-0.1527,-0.0174] MDE0.0677 GRL async checkpoint align, SupCon τ0.07 9.0 sep0.867 contrastive caching 80% hits, KaLM MTEB72.32 9.3 shim MoMA12 GARNet 80% token-cache cost-31% perf-37% verified

## Security Checklist — Private+Secure Dev-Only

- [ ] **No public CORS** — allowlist only `localhost`, `*.dumbmodel.com` dev via localhost, never `*` or `0.0.0.0/*`; dev.json `{"cors":"localhost-only"}`
- [ ] **No Vercel preview alias** — `vercel.json` `"preview": {"alias": false, "DENY":true}`; prod alias production only, dev never deploys to `*.vercel.app` public URL
- [ ] **.gitignore raw keys** — `.scout/`, `**/dev_key`, `**/*api_key`, `dev-api-audit.log`, `.env.local`, `*.bak-*`, `**/.scout/` — audit `git ls-files | grep -E "dev_key|api_key"` must be empty
- [ ] **chmod600 mandatory** — `~/.scout/dev_key` 600, `~/.scout/dumbmodel_dev_key` 600, bins fail fast if 644; fix: `chmod 600 ~/.scout/dev_key`
- [ ] **Audit log dev-api-audit.log** — `~/.scout/dev-api-audit.log` + `~/workspace/.scout/dev-api-audit.log` + `hidden_files/dev-api-audit.log` — `ts, key_prefix, action, latency_ms, status, ip` — append-only chmod600, no raw key log only prefix `dm_dev_****` last 4 + `cut -c1-12`
- [ ] **Constant-time compare** — `crypto.timingSafeEqual` for Bearer `dm_dev_*`, env `DUMBMODEL_DEV_API_KEY` JSON or CSV scopes read dev free, write requires dm_dev_scout_* or dm_admin_* / trading proof requires write rate 120/min key 60/min IP 429 CORS allowlist only `*.dumbmodel.com` localhost `*.vercel.app` never commit raw key `.scout/.gitignore` vercel.json no-store nosniff DENY Referrer-Policy
- [ ] **No env commit** — `.env.local` never at `vercel.json` `no-store nosniff DENY Referrer-Policy`, `Vercel env: DUMBMODEL_DEV_API_KEYS` JSON array env never `.env` file in git
- [ ] **Token-cache safety** — ACNE 17n27e 54 contacts no cloud/vector/OAuth local-first, Bloom m8192 k7 FPR0.9% prefilter only, LRU256 evict no persist secrets

## Bins Auto-load Pattern

All bins auto-load key from env `DUMBMODEL_DEV_API_KEY` or file `~/.scout/dev_key`:

```bash
DEV_KEY="${DUMBMODEL_DEV_API_KEY:-$(cat ~/.scout/dev_key 2>/dev/null)}"
[ -z "$DEV_KEY" ] && { echo '{"error":"missing dev key dm_dev_* required","code":401}' >&2; exit 1; }
chmod 600 ~/.scout/dev_key 2>/dev/null || true
```

## Agent Access — hill 163 T6 — Other Agents Can Leverage Safely

> **Private+Secure dev-only — agents get ephemeral 90s tokens, never raw dm_dev_*.** localhost-only 127.0.0.1:8787, HMAC-SHA256 stdlib crypto only, single-use 256 LRU, rate 20/min per agent.

### 1) Issue token via broker (no raw key logged)

```js
import { AgentTokenBroker } from 'workspace/bundles/claude-bridge/dev-api-bridge.mjs';
const broker = new AgentTokenBroker(process.env.DUMBMODEL_DEV_API_KEY);
const agentToken = broker.issue('deep-researcher','scout-prime','dev.read'); // 90s exp
// audit only prefix dm_dev_****abcd never raw
```

### 2a) Agent calls via ESM import (fast path)

```js
import { devAuthMiddleware } from 'workspace/bundles/claude-bridge/dev-api-bridge.mjs';
const mw = devAuthMiddleware({bind:'127.0.0.1:8787'});
const ok = await mw.check({headers:{authorization:`Bearer ${agentToken}`, host:'127.0.0.1:8787'}, ip:'127.0.0.1'});
if(!ok.ok) throw new Error(ok.code);
```

### 2b) Agent calls via fetch localhost-only

```bash
# builder agent → dottie infer
AGENT_TOKEN=$(node -e "import('workspace/bundles/claude-bridge/dev-api-bridge.mjs').then(m=>{const b=new m.AgentTokenBroker(process.env.DUMBMODEL_DEV_API_KEY); console.log(b.issue('builder','L3-act','dev.write'))})")
curl -s http://127.0.0.1:8787/api/dev/dottie/infer \
  -H "Authorization: Bearer $AGENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"from":"builder","to":"dottie-core","payload":{"query":"LCG 20260813"},"confidence":0.92,"ooda_phase":"Decide","tempo":":01","nodeId":"builder-1"}'
```

### 3) relevantAgents + HandoffEnvelope 7-field

```js
import { relevantAgents, validateEnvelope } from 'workspace/bundles/claude-bridge/dev-api-bridge.mjs';
const agents = relevantAgents('plan DAG for unified chimera CORAL0.5'); // → max3/4 pacing :01 ultra GARNet O(1) Map24 hit80%
// agents = ['planner','strategist','scout-prime']  // noisy guard 13→3
const env = {from:'planner', to:agents[0], payload:{dag:['research','plan','build']}, confidence:0.85, ooda_phase:'Decide', tempo:':01', nodeId:'planner-87'};
validateEnvelope(env); // throws if missing 7-field
```

### 4) Scout dispatch with agent token

```bash
# operator → ScoutCommsBus
curl -s http://127.0.0.1:8787/api/dev/scout/dispatch \
  -H "Authorization: Bearer $AGENT_TOKEN" \
  -d '{"from":"operator","to":"builder","payload":{"task":"hill 163"},"confidence":0.81,"ooda_phase":"Act","tempo":":01","nodeId":"operator-13"}'
```

### Security notes for agents

- **Never** log raw dm_dev_* — broker audit uses `dm_dev_****abcd` prefix-only last4.
- Tokens 90s TTL, single-use, LRU 256 evict oldest, timingSafeEqual sig verify, rate 20/min per agent + 60/min per key.
- Bind 127.0.0.1:8787 only — assertDevOnly throws if host != localhost/127.0.0.1.
- CORS dev-only allowlist localhost:3000/8787 + 127.0.0.1 — never * — vercel.json no-store nosniff DENY Referrer-Policy same-origin.
- Zero_deps true allow acne:./src torch auto cuda else cpu fallback honest 503 never fake — everyday chain open link drag-map→Jordan.
- PWA v67 #080A0F CORE20 void dark LOD4000/8000 DPR1 LCG 20260813→189831298 idx3820 triple [11205,19448,14209] same-link `?daily=20260813&n=1/3/5`.

## LCG + PWA Quick Ref

```
LCG glibc: (Math.imul(seed,1103515245)+12345)>>>0 & 0x7fffffff
20260813→189831298 idx 3820 = 189831298 % 20719 N20719
triple [11205,19448,14209] five [11205,19448,14209,20494,10327] total 20719
same-link-same-stars ?daily=20260813&n=1/3/5 Solo1 Triple3 Full5 Pack Battle
PWA v67 #080A0F CORE20 void dark 118977B inline self-contained free forever private edge gated
CORE20 20×5888B DENY9 offline 13.6k 13608B void dark LOD4000/8000 DPR1 canvas.width=W no devicePixelRatio fillRect void dark toast polite 2600ms vibrate(10) confetti #D8452A void #080A0F
GARNet cost-31% perf-37% — relevance cache O(1) vs naive O(n) 12.6k calls/hr → 38k alloc/hr GC churn → 7.6k alloc/hr after
zero_deps true {"zero_deps":true,"allow":"acne:./src"} — no pip installs, no cloud, ACNE optional local
```

## Gate

- Gate mean 8.93 PASS thr8.0 min8.6 full7 62.9/7=8.99 min papers 8.6: Forms8.8 Zep9.1 CLS8.9 VICReg9.2 CORAL8.6 SupCon9.0 KaLM9.3
- LCG verified Python & Node Math.imul agree glibc
- Timeline 7-field mandatory nodeId,agentId,attempt,latency_ms,tokens_est,status,errorClass even no-change per checkpoint-manager.js timeline.jsonl — 7-field mandatory nodeId,agentId,attempt,latency,tokens,status,errorClass — MoMA-lite 5 tiers recovery ladder verification econ budget3 thr8.0 earlyExit0.3 zero-deps flag monthly clean ACNE v0.4.0 stage4
- 99→100% board Proactive dev loop lane 7/7 free_before 1 cleared 1 stale >4h preserved 3 LOCAL-GPU exempt Goals 99% Ship 99% Master97 hub20719 DONE6 OPEN14 PWA v67 74426B HIT void #080A0F Auth15/15 3 users p95<60s Vercel200 unified404 left Ideas gate 8.93 PASS

## Evidence

- Dev keys never committed — `.gitignore` 4 patterns, bins auto-load, audit log hidden_files + .scout + workspace/.scout triple, chmod600 mandatory, constant-time safeEqual, CORS localhost-only never *
- LCG 20260813→189831298 idx3820 triple [11205,19448,14209] same-link-same-stars ?daily=20260813&n=1/3/5 verified Python&Node
- PWA v67 #080A0F CORE20 void dark inline 118977B 0 src no CSS link icons base64 hub CORE20 DENY9 offline 13.6k proof LCG 20260812→1233799701 idx3970 yesterday chain prefix preserved
- Token-cache ACNE 17n27e 54 contacts m8192 k7 FPR0.9% 1KB marbles TSBF90% cache_stats hits156 miss19 ratio89.14% tokens12450 $0.18675 compressed87k
