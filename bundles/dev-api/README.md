# Dumbmodel Dev API — PRIVATE dev-only

> **PRIVATE** — dev-only, localhost allowlist. Never expose publicly. Never commit dm_dev_ keys.

## Overview
Title: `Dumbmodel Dev API private` v0.1-dev (openapi 3.0.3)
Servers (localhost only):
- `http://localhost:3000`
- `http://127.0.0.1:3000`
- `https://api.dumbmodel.local`

## Security Hardening
- **Auth:** `bearerAuth` http bearer, prefix `dm_dev_` mandatory. Description in spec.
  - Validate with `timingSafeEqual` (Node: `crypto.timingSafeEqual(Buffer.from(a), Buffer.from(b))` length-safe)
  - Constant-time compare, never leak timing.
  - Never log raw key. Scope=dev only.
- **CORS allowlist only:** `localhost/*.dumbmodel.local`
  - Allowed: `http://localhost:3000`, `http://127.0.0.1:3000`, `https://*.dumbmodel.local`
  - Deny all others. No `*`.
- **Rate limiting:** 60/min per key, 20/min per IP. Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, `Retry-After` on 429.
- **Headers (vercel.json /dev/*):**
  - `Cache-Control: no-store, no-cache, must-revalidate, proxy-revalidate`
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `Referrer-Policy: DENY` (per spec — strict DENY, not when-cross-origin)
  - `Permissions-Policy: camera=(), microphone=(), geolocation=()`
  - `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload` (for https://*.dumbmodel.local)
  - `Content-Security-Policy: default-src 'none'; frame-ancestors 'none'`
- **Secrets hygiene:**
  - `.env.example` placeholder `dm_dev_LOCAL_ONLY_REPLACE_ME`
  - `.gitignore` contains `dm_dev_*`
  - Never commit raw key. Add to `~/workspace/.scout/.gitignore` line `dm_dev_*`

## Paths
All require `security: [bearerAuth]` + rateLimit headers.

- **POST /dev/infer** — `prompt`, `max_new_tokens` (1-512) → `{final, turn}` final turn.
- **POST /dev/dispatch** — `intent`, `complexity`, `payload` → `{relevantAgents, envelopeId}`. MoMA-lite 5 tiers deterministic router. HandoffEnvelope 7 req fields.
- **GET /dev/daily** — `?daily=YYYY-MM-DD&n=5` → `{lcg, idx, triple, five, sameLinkSameStars}`.
  - LCG deterministic from dailySeed. Canonical: `20260812→1233799701`.
  - Invariant: same-link-same-stars (same link → same stars).
- **GET /dev/provenance** — → `{provenance: "7/7/0", ok:7, total:7, bad:0, hashes[]}`. 7/7/0 mandatory healthy.

## Runtime Flags (AGENTS.md compliance)
- `zero_deps=true` — no pip installs, no cloud, ACNE optional local
- `torch auto: cuda else cpu` — `torch.cuda.is_available()` ? cuda : cpu, zero-deps true
- LCG dailySeed: `YYYYMMDD int` → LCG → idx/triple. Example `20260812→1233799701`

## Dev Usage
```bash
export DUMBMODEL_DEV_API_KEY=dm_dev_LOCAL_ONLY_REPLACE_ME
curl -H "Authorization: Bearer $DUMBMODEL_DEV_API_KEY" http://localhost:3000/dev/daily?daily=2026-08-12
curl -X POST -H "Authorization: Bearer $DUMBMODEL_DEV_API_KEY" -H "Content-Type: application/json" \
  -d '{"prompt":"hello","max_new_tokens":64}' http://localhost:3000/dev/infer
```

## Verification
- `bundles/ultra/runs/dev-api-spec/timeline.jsonl` — 7-field mandatory: nodeId, agentId, attempt, latency, tokens, status, errorClass (triple-write per checkpoint-manager)
- OpenAPI validates: openapi 3.0.3, servers localhost-only, bearerAuth dm_dev_ prefix

PRIVATE. Keep local only.
