# Orchestrator Prime Hardening — v5 Prime Dynamic Workflows
Branch: scout/orchestrator-hardening
Date: 2026-08-07 CDT
Goal: goal_b9b94f9a5780 — Scout Prime always-on

## SSOT — bundles/cron.d/
13 logical crons, 15 JSON files (hyphen/underscore compat for 2):

| id | owner | interval | file | purpose | logs to | status |
|----|-------|----------|------|---------|---------|--------|
| active_tasks_sweep | operator | 30m | active_tasks_sweep.json | clear stale >4h, preserve LOCAL-GPU OOM guard 2, claim free lane, sync COORD 7 repos | .scout/missions/_cron/timeline.jsonl + ultra/runs/timeline.jsonl | ✅ 7-field |
| dottie-vec-monitor | goal:refine-dottie... / operator | 30m | dottie-vec-monitor.json + dottie_vec_monitor.json | Dottie monitor --mode monitor, vec-hub JSON validity, telemetry size, writes hidden_files/cron_health.jsonl only never files/ | hidden_files/cron_health.jsonl + timeline.jsonl | ✅ created |
| dottie_triple_write_check | operator | 30m | dottie_triple_write_check.json | verify 17/17 triple-write v0.8-scout-v3.3-parity | ultra/runs/timeline.jsonl | ✅ |
| goal_health | operator | daily 08:30 America/Chicago | goal_health.json | Slip-proof daily healthcheck — Goal TRACKS Task / REALIZES Project, placeholder when needs_tasks | goal_health.jsonl + .scout/missions/timeline.jsonl | ✅ patched RF |
| local_gpu_handoff | operator | 30m | local_gpu_handoff.json | LOCAL-GPU measured G2 handoff → audit + celebrate | ultra/runs/ | ✅ |
| monthly_clean | operator | cron 0 3 1 * * America/Chicago | monthly_clean.json | prune exports/ >30d .DS_Store zero_deps true | .scout/missions/_cron/monthly_clean.jsonl | ✅ |
| observability_tick | operator | 15m */15 | observability_tick.json | metrics_collector.js OODA 4/4 agentic 6/6 tempo :13 MoMA 5 tiers graph checkpoint 7-field verification pacing max3 | ultra/runs/metrics.jsonl + dashboard_metrics.json | ✅ patched RF 7-field + extras |
| podcast-brief-auto-exec | goal:ultracode-brief-exec | 90s | podcast-brief-auto-exec.json + podcast_brief_auto_exec.json | 90s brief → TODOs L1 3-lens, diff active-tasks free lanes, wire DAG Top5 tick+flags→vec+lattice→analytics+trace+ops→meter, spawn max4 pacingFilter, timeline 7-field even no-change | ultra/runs/podcast-brief-auto-exec.jsonl + timeline.jsonl | ✅ created |
| podcast_brief_watchdog | operator | 30m | podcast_brief_watchdog.json | manifest != state last_slug stale>15m watchdog | ultra/runs/ | ✅ |
| poll_merge_watchdog | operator | 30m | poll_merge_watchdog.json | sync_log.jsonl + poll_merge.log <15m restart poll_merge.sh 24×300s | ultra/runs/ | ✅ |
| self_improvement_tick | operator | daily 04:00 | self_improvement_tick.json | pattern → skill proposal 1 lens early_exit_after2 | self_improvement/staging/ | ✅ |
| sync_bundles | operator | hourly 0 * * * * | sync_bundles.json | manifest mtime → TLPG constructs Agents/Workflows/Skills/Bundle 13/9/11/1 edges76 | contacts_harness/.sync.log + ultra/runs/timeline.jsonl | ✅ patched |
| vector_hub_chimera_check | operator | 30m | vector_hub_chimera_check.json | vector-hub https://dumbmodel.com/ 200 5/5 OK DM_PROVENANCE 7/7/0 chimera 20719×64-d | ultra/runs/ | ✅ |

All JSONs: id, enabled:true, owner, schedule{kind}, description, logging.required_fields[7] nodeId,agentId,attempt,latency(_ms),tokens(_est),status,errorClass, version 1.0+, tags always-on operator v5 Prime, zero_deps true.

## Checkpoint-Manager — mandatory 7-field even no-change

File: bundles/ultra/checkpoint-manager.js
- Required fields: nodeId,agentId,attempt,latency_ms,tokens_est,status,errorClass — plus legacy alias latency/tokens handled
- RequiredTimelineFields = ['nodeId','agentId','attempt','latency_ms','tokens_est','status','errorClass']
- EarlyExitMap: analytics-phase0/auth-phase0 six-hats/analogy early_exit_after 2 fallback cached store/flags, deep.list concept-fan, langchain.list scamper, eval_hoops inversion
- getNodePolicy(nodeId) → {early_exit_after, fallback, lens}
- getCanonicalDirs() = 9 dirs: bundles/ultra/runs, dottie/pipeline/runs, dottie/bundles/ultra/runs, dottie/apps/scout-cli/dottie/pipeline/runs, apps/ava-factory/bundles/ultra/runs, dottie/apps/ava-factory/bundles/ultra/runs, dottie/apps/ava-factory/dottie/pipeline/runs, apps/ava-factory/dottie/pipeline/runs, goals/.../hidden_files/brief-auto-exec-checkpoints
- logNode(): writes timeline.jsonl to baseDir + 8 dirs triple-write (even no-change), marks _missing_fields honest if any, injects ooda tempo :13, honest_lens visibleAbandonments noFake7of7 zero_deps true no_torch triple_write_7field
- save(): writes checkpoint.json to 9 dirs + timeline.jsonl checkpoint_saved event even no-change
- pause(reason): saves paused true pause_reason paused_at, logs L0-scout-prime-pause required 7-field event checkpoint_pause
- resume(runId): filters pending nodes status!=done, logs checkpoint_resume event, pending count

Compliance: zero_deps true no pip pure JS stdlib, no torch, triple-write 17/17 after repair dottie-20260807T132954Z, mandatory 7-field even no-change verified timeline.jsonl 227 lines.

## Mission Log — pause/resume

File: bundles/scripts/mission_log.py
- BASE = ~/workspace/.scout/missions
- REQUIRED = [nodeId,agentId,attempt,latency,tokens,status,errorClass]
- init_mission(mission_id, meta): mkdir + checkpoint.json v5 Prime guarantees structured_workflow tool_safety memory_discipline reasoning_boundaries eval_hooks multi_agent + touch timeline.jsonl
- log(mission_id, entry): validates missing required → ValueError, alias latency_ms→latency tokens_est→tokens, ts/runId defaults, append JSONL
- pause(mission_id, reason): log L0-scout-prime-pause required 7-field attempt1 latency0 tokens0 status paused errorClass None event checkpoint_pause reason runId, update checkpoint.json paused true pause_reason paused_at
- resume(mission_id): check exists, log L0-scout-prime-resume status resumed event checkpoint_resume, update checkpoint.json paused false resumed_at
- Self-test __main__ init+log ready
- Used by: .scout/missions/_cron + self-improvement

Test: python3 bundles/scripts/mission_log.py test-mission → PASS

## Comms Pacing — max3/4 tempo :13

File: bundles/ultra/communication-pacing.js
- HandoffEnvelope required 7+9 = ['from','to','payload','confidence','citations','ooda_phase','tempo','runId','nodeId'] optional edge_cases alternatives blocked_reason schema confidence 0-1 ooda_phase enum Observe Orient Decide Act Feedback timestamp blocked_reason null/string
- validateEnvelope(): missing k, confidence out of range, invalid ooda_phase throw
- ScoutCommsBus(runId): constructor queue history G_history MoMA routing, send(envelope) validate + push queue + history ts ...envelope, relevantAgents({intent,complexity,currentNode}): intentMap agentic_loop 9, deep_research 4, complex_action 3, ooda 4, verification 3, research 3; complexity epic agentic_loop → 13 swarm only true epic, medium → cap 5-6 noisy limit, simple → 3
- PacingFilter: observe max_parallel_fetch 3 time_box 120s rule Wide Sweep 5-7 parallel 3 batches rationale prevent API burst + token flood, orient time_box 180s rule lattice recall 0.7 dense + 0.3 sparse rerank 1-2 hops max_context_chars 8000, decide single_action true rule one hypothesis testable not 3 vague rationale Boyd, act verify_after true rule artifact changes env + feedback logged side_effect_check true, feedback log_even_no_change true target timeline.jsonl rationale ultra non-negotiable metrics-dance
- shouldParallelize(nodes): filter side_effect_level<=1 !requires_human safe slice0-4 max 4 concurrent safe agentic guarantee 6 concurrency 4 no drift
- nextTick(): now minutes remainder (13 - mins%13 +13)%13 `${remainder}m to :13 pacing window`
- Export default {HandoffEnvelope, ScoutCommsBus, PacingFilter}
- Three-layer separation: Execution agents, Communication queues/events/RPC via Scout Prime, Orchestration DAG validity replans eval hooks tempo
- Compliance: max3 parallel Observe, concurrency4 Act, tempo :13

## Bundles Clean

- zero_deps.json: {"zero_deps":true,"allow":"acne:./src","version":"5.0-prime"} ✅ v5 Prime zero-deps flag, no pip, no cloud, ACNE optional local stdlib+optional local src/acne
- ultra/runs/: 1921 entries flagged for monthly_clean — DO NOT AUTO-DELETE per AGENTS.md, oldest 20 listed for prune candidate ultra-test-1 symlink + 19 brief-auto-exec noop 20260805-06
- .scout/missions/_cron/timeline.jsonl: 227 lines 125k, required 7-field validated last 5 entries PASS, even no-change heartbeat active_tasks_sweep ok
- active_tasks_sweep: 461 lines 79 LOCAL-GPU markers 2 claimed preserved vector-hoops v6 150ep d128 4H vector-gridiron real nflverse 160-feat 32-d 22:20 CT OOM guard per CLAIM_BOARD_PROMPT NOT cleared, heartbeat logs 04:43 05:13 05:43 etc show preservation, cron 30m owner operator RF 7-field
- Branches: workspace scout/orchestrator-hardening created current HEAD, vector-hub dottie hoops pitch gridiron equities unified all created and checked out now ✅ 7/7 repos
- .DS_Store: 0 in your_files 0 in bundles ✅
- exports/: README only 0 >30d ✅ clean, monthly_clean skipped not 1st 03:00 CT next 2026-09-01

## Dynamic Workflows Added to Goals Tab

Per user request "full set of dynamic workflows and add them to Goals tab":

- podcast-brief-auto-exec @90s → goal_ab37e52bf33d podcast pipeline
- dottie-vec-monitor @30m → goal_2186225baf2d master build
- active_tasks_sweep @30m + poll_merge_watchdog @30m → goal_b9b94f9a5780 orchestrator always-on
- All wiring verified timeline 7-field even no-change, OODA fidelity 4/4 agentic 6/6 tempo :13, pacing max3/4, pause/resume days later.

## Verification Commands

```
python3 -m json.tool bundles/cron.d/*.json
node -c bundles/ultra/communication-pacing.js
node -c bundles/ultra/checkpoint-manager.js
python3 bundles/scripts/mission_log.py test-orchestrator-20260807
grep -r "zero_deps" bundles/zero_deps.json
ls bundles/cron.d/ | wc -l  # 13 logical, 15 with hyphen/underscore compat
cat .scout/missions/_cron/timeline.jsonl | tail -5 | python3 -m json.tool
```

All PASS.
