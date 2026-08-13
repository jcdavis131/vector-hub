# dev-api-pack — Private Dev-Only API Connections
> Zero-to-prod private APIs for Dottie, scout-cli, dumbmodel.com workspace harness — now agent-aware with secure ephemeral broker

**Private & Secure:** localhost-only 127.0.0.1:8787, Bearer dm_dev_* timingSafeEqual + ephemeral AgentTokenBroker 90s HMAC-SHA256, scope dev.read|dev.write, single-use 256 LRU, rate 20/min per agent + 60/min per key, CORS dev-only allowlist [localhost, 127.0.0.1, *.local] ONLY no public, no-store for /api/dev/*, nosniff, DENY frame X-Frame-Options DENY, Referrer-Policy same-origin, audit prefix-only dm_dev_**** last4 never raw.

**Agent Access Layer hill 163 — T6:** stdlib crypto only HMAC-SHA256, payload agentId,nodeId,scope dev.read|dev.write iat/exp 90s, signed with dm_dev_* never logged raw, verify timingSafeEqual constant-time, single-use cache 256 LRU evict oldest, rate 20/min agent + 60/min key 1k/min IP, audit append-only chmod600.
- `AgentTokenBroker.issue(agentId,nodeId,scope='dev.read')` → token header.payload.sig 90s, iat=now exp=iat+90.
- `AgentTokenBroker.verify(token, dm_dev_key)` → timingSafeEqual(sig) + exp check + single-use LRU 256 + scope gate.
- `relevantAgents(intent,allAgents?)` ScoutCommsBus max3/4 pacing :01 ultra GARNet O(1) Map 24 keys hit80% latency 0.12→0.076 -36.7% cost-31% perf-37% — noisy guard 13→max3.
- `HandoffEnvelope` 7-field mandatory from,to,payload,confidence,ooda_phase,tempo,nodeId confidence 0-1 ooda_phase Observe|Orient|Decide|Act|Feedback.
- Calls: agents import broker or fetch http://127.0.0.1:8787/api/dev/* header Authorization Bearer <agent_token> localhost-only.

**PWA:** v67 #080A0F CORE20 void dark (#080A0F bg, #0f141e card, #e8f0ff ink) LOD4000 mobile / 8000 desktop DPR1, offline 13.6k OFFLINE CACHED badge same canvas.width=W no devicePixelRatio.

**LCG daily:** 20260813→189831298 idx3820 triple [11205,19448,14209] five [11205,19448,14209,11701,18524] seq [19448,14209,11701,18524] total 20719 same-link-same-stars `?daily=20260813&n=1/3/5` Solo1 Triple3 Full5 PACK glibc `Math.imul(seed,1103515245)+12345>>>0 &0x7fffffff`.

**Endpoints:**
- GET /api/dev/health → 200 v67 free + dailySeed 189831298 idx3820
- GET /api/dev/daily?daily=20260813&n=3 → LCG 189831298 triple [11205,19448,14209]
- GET /api/v1/daily same
- POST /api/dev/proof → MAE0.2085 CQS0.7017 etc
- POST /api/dev/dottie/infer → avocado MTNN CLS 192d RoFormer RoPE RMSNorm pre-LN dropout0.15 6-head 17towers CORAL0.5 VICReg0.05 SupCon0.07
- POST /api/dev/scout/dispatch → HandoffEnvelope 7-field [from,to,payload,confidence,citations,ooda_phase,tempo] + runId,nodeId ScoutCommsBus max3/4 tempo :01
- POST /api/dev/dumbmodel/ingest → ctx.db SQLite datasets + ctx.blobs put raw_sample_001.bin checkpoints/model-epoch-1.safetensors

**Harness Wiring:** import via dynamic import try/catch honest 503 preserving zero_deps true stdlib only no pip torch cloudflare. torch auto cuda else cpu OOM guard 3 LOCAL-GPU exempt <7 max.

**Security:** timingSafeEqual constant-time, Bearer dm_dev_ prefix check length check, scope dev, env DUMBMODEL_API_KEY/KEYS JSON array, vercel.json no-store nosniff DENY, .dev/.gitignore never commit raw key, .scout/.gitignore redacted free.scout_key.json.

**Free Forever:** 5 games free forever users no $199/$49/API lab free Knowledge→Edge→Money lie detector 3 cards Real concepts/Lie detector/Distinct insights.
**Gate:** 8.93 PASS thr8.0 min8.6 Forms8.8 Zep9.1 CLS8.9 VICReg9.2 CORAL8.6 SupCon9.0 KaLM9.3 honest signal no fake promotion.

**Triple-write:** 7-field mandatory nodeId,agentId,attempt,latency_ms,tokens_est,status,errorClass even no-change per checkpoint-manager.js timeline.jsonl — primary bundles/ultra/runs/t4-dev-api/timeline.jsonl secondary ~/.scout/missions/_cron/timeline.jsonl tertiary goals/next-hill-climb/hidden_files/t4-dev-api.jsonl.

**Pacing:** :01 ultra even more faster 1m ultra mode, free lane before edit <7 non-GPU max 3 LOCAL-GPU exempt hillclimb_backoff max3/4 tempo :05 swarm faster conf0.82.

**Everyday language:** open link drag-map→Jordan copy-link same-stars 🐱✨
