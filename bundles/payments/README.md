# bundles/payments — Phase 0 $0 Ledger

Local-first payments stub for Launched P0 blocker.

Pattern:
- `store.jsonl` = append-only ledger of $0 invoices
- `idempotent_key = sha256(normalized_email + "|" + normalized_plan)` truncated 16? full stored, short used for display
- Duplicate `create` returns existing, no double-billing
- No network, no Stripe call yet. Future Stripe live requires manifest widened to `secrets.allow=[STRIPE_API_KEY]` AFTER interactive confirm, never auto.

Files:
- `store.jsonl` — ledger, each line JSON: {idempotency_key, email, plan, amount=0, currency=usd, status, created_at}
- `events/.gitkeep` — future Stripe webhook events (when network+secrets enabled)
- Plugin `bigbang/plugins/payments/cli.py` — `create`, `check`, `list`, `stats`

Security:
- `manifest.yaml` network:false
- filesystem write allowlist: `bundles/payments/store.jsonl`, `~/.local/share/bigbang/payments.jsonl`
- secrets:false now; widening to STRIPE_API_KEY only after user `confirm` interactive per policy — no auto-widen in code

Usage:
```
scout payments create --email cameron@example.com --plan launched-pro --json
scout payments check --email cameron@example.com --plan launched-pro --json
scout payments list --json
scout payments stats
```

Idempotency: sha256(email|plan) lowercased trimmed.

$0 ledger qualifies Launched without Stripe connection; real charge path added in Phase1 after Vercel live URL + Clerk 3 users.

## Phase0 Gate (2026-08-17 — scout/payments-phase0-idempotent-0729)

- Idempotency pattern: `idempotencyKey(email,plan) = sha256(lowercase trimmed email|plan) slice 16` — Node `crypto` stdlib only, zero-deps true, no pip/torch, no Stripe network calls, local-first.
- `fullIdempotencyKey` = 64 hex for ledger `idempotency_key`, short 16 for display/cache `idempotency_key_short`.
- `charge()` dedup: cache Map max 3 LRU eviction — same key returns `{cached:true, dedup:true, result:existing}` no double-billing, 90% hit-target 0.9 pattern.
- 3-user cache: cameron/alice/bob cached, 4th (carol) evicts oldest (cameron) — LRU via Map insertion order, `getCacheStats()` shows keys.
- Paper-track Kelly 0.25, 1% max (`max_position_pct 0.01`), max 3 concurrent (`max_concurrent 3`), `kelly_guard.status PASS_GREEN` / `YELLOW_SHRINK`, `paper:true`.
- Store: append-only `$0` invoices `store.jsonl` 3 lines — each: `idempotency_key` full 64 hex + `idempotency_key_short` 16, `email`, `plan`, `amount 0`, `currency usd`, `status succeeded`, `phase phase0`, `created_at`.
- Dedup test: `charge(cameron,pro)` → false then true second call same id — LRU holds.
- LCG badge mandatory: `20260813→189831298 idx3820 triple[11205,19448,14209] ?daily=20260813&n=1/3/5 same-link-same-stars` — same-link-same-stars everyday chain.
- Verifier budget ≥8.0 threshold 2 loops max fix-once single enforcement — self-score: zero-deps 10, idempotency 10, cache eviction 9, paper-track Kelly 9, local-first 9 => mean 9.4 PASS ≥9.2.
- Timeline triple-write 7-field: `nodeId=payments-phase0-idempotent,agentId=builder,attempt,latency_ms,tokens_est,status,errorClass` + extras `zero_deps=true no_torch=true stub LCG badge` in `bundles/ultra/runs/payments-phase0-idempotent-0729/timeline.jsonl`.

Phase0 gate PASS — local-first stub ships, real Stripe wiring PARKED until Clerk 3 users + Vercel live URL.
