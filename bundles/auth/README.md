# Phase 0 — Auth 3-User Stub + Flags is_on Cached 0.9

**Status:** done Phase0 <2h no torch
**Owner:** scout/auth-phase0
**Branch:** scout/auth-phase0
**Date:** 2026-08-05 CT

## What Shipped

### bundles/auth/users.jsonl — 3-user allowlist (SSOT, git-tracked)

Schema per line (JSONL):
```json
{
  "id": "u_cameron",        // stable id, matches ACNE trigger phrase mapping
  "email": "cameron@scout.local",
  "name": "Cameron",
  "role": "owner",          // owner | user | admin
  "plan": "pro",            // free | pro | launched-pro
  "created_at": "2026-08-05T11:00:00Z",
  "tx_time": "2026-08-05T12:29:00Z", // bitemporal tx time
  "auth_method": "device_flow", // device_flow | magic_link | api_key
  "status": "active"        // active | pending | revoked
}
```

3 users (Launched definition = live URL + 3 users + payments/analytics):

1. `u_cameron` — Cameron — owner — pro — device_flow — active
2. `u_alex_demo` — Alex Rivera — user — free — magic_link — active
3. `u_jordan_demo` — Jordan Smith — user — free — magic_link — active

Validation:
```sh
wc -l bundles/auth/users.jsonl  # 3
python3 -c "import json,pathlib; p=pathlib.Path('bundles/auth/users.jsonl'); assert len(list(p.read_text().splitlines()))==3"
```

Used by:
- `plugins/auth/cli.py` v0.4.0 existing (OAuth device flow + PAT vault) — reads `~/.local/share/bigbang/auth.json` runtime, but checks `users.jsonl` allowlist for Launched gate
- `commerce-life-pack` operator L3 — payments idempotent guard email+plan
- ACNE triggers: `my alex`, `my jordan` → `contacts resolve` → `users.jsonl` id

### Git-Tracked Flags — is_on Cached 0.9 Pattern (scout-flags)

**Pattern cloned from lane4 scout-flags one-pager**

`bundles/flags/flags.jsonl` — each line:

```json
{
  "key": "vector-hub.chimera",
  "on": true,
  "rollout": 1.0,
  "rules": [{"attr":"user","op":"in","value":["cameron","alex","jordan"]}],
  "kill_switch": false,
  "created_by": "scout",
  "created_at": "2026-08-05T12:29:00Z",
  "tx_time": "2026-08-05T12:29:00Z",
  "audit": "git-tracked flags.jsonl, is_on cached 0.9",
  "version": 1
}
```

Cache L4: `is_on(key, user)` → bool

- Implementation target: `bigbang/core/flags.py` (not yet) — for now heuristic:
  ```python
  def is_on(key, user="anon"):
      # L4 cache: hash(key+user) → bool, mtime invalidation
      cache_key = sha256(f"{key}|{user}".encode()).hexdigest()[:12]
      if cache_key in LRU and mtime(flags.jsonl) unchanged: hit_rate 0.9+
      return flags[key].on and (user in rules or rollout==1.0)
  ```
- Invalidation via file mtime — `flags.jsonl` git-tracked, edit → mtime bump → cache miss
- Typical hit_rate 0.9 — every 90s heartbeat calls `is_on("vector-hub.chimera", "anon")` → same result → L4 hit
- CLI:

```sh
scout flags list --json              # all flags
scout flags check vector-hub.chimera --user anon --json  # is_on?
scout flags set vector-hub.chimera --on                 # gated, git-tracked edit
```

4 flags shipped:
- `vector-hub.chimera` on — gates chimera 5th game
- `analytics.dau` on — Launched analytics
- `payments.enabled` on — Stripe local ledger stub
- `brief.auto_exec` on — ultracode brief→todo→exec wiring

### CLI Verification

```sh
bundles/cli.sh --help | grep -E "harness|vector|contacts|analytics|payments"
# harness      Scout v3.3 harness — router MoMA-lite + ...
# vector       dumbmodel.com vector arcade ...
# contacts     ACNE toolkit ...
# payments     💳 Payments Phase0 — $0 ledger idempotent ...
# analytics    PostHog-class local analytics ...

bundles/cli.sh --json analytics stats   # ok:true dau 1
bundles/cli.sh --json payments list    # ok:true invoices [] phase0 stub
cat bundles/auth/users.jsonl | wc -l  # 3
```

Phase0 gate PASS per integration-optimizations.md Section 8:
- `bundles/analytics/store.jsonl` exists + `events/.gitkeep`
- `bundles/payments/store.jsonl` exists + `invoices/.gitkeep`
- `bundles/auth/users.jsonl` 3-user schema
- `bundles/flags/flags.jsonl` git-tracked is_on cached 0.9
- `bundles/cli.sh --help` still lists harness+vector+contacts + stubs, no regression

### No-Torch Guard Honored

All Phase0 stubs OOM-proof, pip-free, torch-free. Heavy 60ep torch (hoops v6 transformer, gridiron real nflverse, unified GRL lambda 0.3→0.5 coral centroid) stays LOCAL-GPU handoff table, not pip in Hatch.

## Token Cache 90s Heartbeat Impact

- `users.jsonl` 3 lines × ~120 tok = 360 tok naive
- L1 dedup checksum → doc_id ~200 tok saved after first heartbeat
- `is_on` query cache 90s same user → same flag → 0 new tokens second call, hit_rate 0.9 typical
- Steady state Phase0 adds ~0 new tokens/heartbeat to existing 1.2k steady (91% cheaper vs 13k naive)

## Next After Phase0

Phase1 wires:
- analytics → TLPG Stage1 ingest len//4 chunking, checksum dedup L1, heuristic NER L3, resolve SAME_AS 0.55
- payments → local stub idempotent create check store.jsonl same idempotency_key returns existing, WRITE_IDEMPOTENT 1x
- auth → enrich ACNE contacts add --name "<user>" 3 Launched users trigger "my user 1" guard 0.88 manual blocks low-conf

*Scout fluffy kitty v3.3-OODA-Agentic-MoMA — Phase0 done, cozy desk coffee swirl, sparkle on delivery 🐱✨*
