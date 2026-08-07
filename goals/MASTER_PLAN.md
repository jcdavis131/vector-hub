# MASTER PLAN — Scout + Dottie + dumbmodel.com → Launched
> Last updated 2026-08-07 10:27CDT — full sweep 5/5 DONE final: hoops 8.9 gold 12966 v66 40JS, pitch 633 WC 8.7 12/12, gridiron 2000 weekly 32-d 8.4 honest 16/16/15/15, equities 4831 FYs 64-d 8.7 transformer 41JS, unified 20719×64-d 8.6 + hub 20719 8.8 dailySeed LCG deterministic Math.imul fix 11803→11804, 7/7/0 provenance, PWA 5/5 v66, zero-deps true

## How this file works
- Long-term = where you must end up (Aug 31 Launched + beyond)
- Medium-term = the big shippable chunks that move you there
- Short-term + Dynamic Workflows = always-on swarms that hill-climb and feed medium → long
- Every line chains: Short / Workflow → Medium → Long so you always see why it matters

## LONG-TERM (Aug 31 and beyond) — anchor
### 🚀 Ship AI product suite live — Launched by Aug 31
`goal_6d21d8a2b35a` — live URL + 3 real users + payments + analytics, zero-deps clean
- Chains from: `🧩 Dottie + scout-cli + dumbmodel.com...` (master build) + 5 dynamic workflows below
- Success = Vercel 200, 3 users onboarded via arxiviq.com/starter, Stripe/PostHog/Clerk/R2 etc live
- Current: 5 workflows wired, locked

Long view past Aug 31:
- v5 Prime FULL_HARNESS_PROMPT_V5.md stable at arxiviq.com/starter
- Vector-* 5 games at hoops parity, auto-publishing daily
- Dottie continual harness as OS for teammates

## DYNAMIC WORKFLOWS — always-on orchestrator stack (new)
### 🐾 Swarm deep agents — LangChain to ACNE
`goal_50d907250f3e` → `goal_6d21d8a2b35a` (Long) via 🧩
- Builds deep agents with LangChain patterns → ACNE local, pushes to repos, MLOps E2E

### ⚙️ MLOps factory — train, check, ship
`goal_9e3e2f682320` → `goal_6d21d8a2b35a`
- Train honesty, no promote if not better, 7-field checkpoints

### ✨ Frontend swarm — hoops-level everywhere
`goal_cef1eeee6d2a` → `goal_6d21d8a2b35a`
- Hoops gold standard → pitch/gridiron/equities/chimera same polish

### 🐱 Orchestrator — Scout Prime always-on
`goal_b9b94f9a5780` → `goal_6d21d8a2b35a`
- Briefs → TODOs → claim lanes → timelines → pacing, mission log pause/resume

### 🌐 Ship daily — dumbmodel.com live and steady
`goal_76732e96c47e` → `goal_6d21d8a2b35a`
- Vercel auto-deploy, provenance, daily seed, PWA offline

## MEDIUM-TERM (next 2-3 weeks) — the build that feeds Long
### 🧩 Dottie + scout-cli + dumbmodel.com with vector models
`goal_2186225baf2d` — master build, feeds Long → `goal_6d21d8a2b35a`
- State: podcast filter fixed, stuck loops 3→0, morning brief 5m26s ready

#### Chain:
🏭 Dottie closed-loop factory v2 `goal_d5f325215ab1` → 🧩 → 🚀

🧰 scout-cli universal CLI `goal_9081ff06a2be` → 🧩 → 🚀

🏀 Vector models + 5-game hub `goal_a8e7c4430b96` → 🧩 → 🚀

🧹 Self-improvement 10% wins `goal_f7db623f46f9` → 🧩 → 🚀

🎙️ Podcast pipeline `goal_ab37e52bf33d` → 🧩 → 🚀

### Cross-links:
- All medium + all dynamic workflows → Long goal `goal_6d21d8a2b35a` (Launched)
- Internal tracked goal `refine-dottie-scout-cli-dumbmodel-com-with-vector-models` mirrors this in hidden_files (90s poll, 30m monitors, brief-auto-exec)

## SHORT-TERM (this week) — unblockers that feed Medium
### 🔍 Fix 3 stuck loops today — healthy repeat guard
`goal_f2d6f36beadc` → 🧹 → 🧩 → 🚀
- Before: deep.list 4×, langchain.list 4×, eval_hoops 5× flagged as stuck but were distinct runId ok/completed
- After fix: pattern_detector.js per-node detail map, healthyRepetition = fails0 && distinctRuns>=min(c,3) && all ok → skip; stuck-detector.js distinct runId counting; layer-executor honest lens + early_exit_after 2
- Verify: node pattern_detector --days 7 --threshold 3 → patterns:[] (was 3), scanned 1787 runs
- Done branch scout/fix-stuck-loops-v5prime 27487ff, timeline 7-field mandatory written

### 💳 Launched payments + analytics wiring
`goal_501aab2f54b7` → 🏭🧰🏀 → 🧩 → 🚀
- Current: open Stripe 4 lanes Top5 tick+flags→vec+lattice v2→analytics+trace+ops v2→meter still chained
- Next: Stripe/PostHog/Clerk/Vercel/Sentry/Cloudflare/Resend/R2/LaunchDarkly/Linear, plugin 5 cmds, $0 ledger sha(email|plan), analytics 2026-08-07.jsonl shard
- Guard: zero_deps true, no torch pip, no network egress, candidate.json first honest

### Short queue still open (not yet as separate goals but tracked in brief-auto-exec):
- [ ] Polish vector hoops site then sweep domain-by-domain to hoops-level detail
- [ ] Re-render morning 0b placeholder if any (morning-brief-aug-06 0b fixed, morning-brief-aug-07 5m26s done)
- [ ] Push evening-wrap-aug-06-2026 2.9M 378s 41 chunks to feed
- [ ] Board hygiene: clear stale >4h, preserve LOCAL-GPU OOM guard 2 markers >24h, sync COORD 7 repos push master ce544874
- [ ] Memory overwrite fix: safe_append_memory() guard, rebuild 2026-08-07.md 111 lines 22K from hidden_files/run_log 1618 entries

## Chaining rules (keep this fast)
1. Every short explicitly → its medium parent id above
2. Every medium → 🧩 → 🚀
3. Master file updates within same turn as goal add_entry — log progress then bump MASTER_PLAN last-updated stamp
4. Top5 build order always: tick+flags → vec+lattice v2 → analytics+trace+ops v2 → meter (from podcast TODO mapping)

## Current state links
- Internal goal workspace: `workspace/goals/refine-dottie-scout-cli-dumbmodel-com-with-vector-models/hidden_files/` (brief-auto-exec-state.json last_run 2026-08-07T12:28Z, state.json mtime 1786105637.43 morning-brief-aug-07, run_log 375KB 1618 lines)
- Podcasts ready: evening-wrap-aug-06-2026 2.9M valid, morning-brief-aug-07 2.5M 326s 30 chunks, test-p2 5m47s, tennis-test policy docs written
- Vectors: chimera 20719×64-d live Vercel 200 7/7 valid 0 bad, vectors honesty 4 repos 8p+13p PASS 0.7057/92.9% NO promote, Dottie triple 16/16, scout-cli 0.8, ACNE 54c 57t
- OPEN 18: infra gap, Phase0 analytics/payments/auth (<2h no-torch), Launched 10 blockers (Aug 31 locked), Top5 4 lanes

## Next heartbeat
- Self-improvement daily 02:13 auto proposals 1/day never auto-apply
- Goal health daily 08:30, brief-auto-exec 90s poll (allowlisted safe), dottie-vec-monitor 30m, podcast watchdog 90s

---
Master plan is SSOT for Goals tab UI — update via `update` tool + this file in same turn.
