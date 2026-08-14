# HEARTBEAT.md — Index (v5.1) SSOT is cron.d JSON

> CRON.D is SSOT per AGENTS.md v5 Prime. This file is index only. Every cron needs owner + schedule + logged entry even "no change" → timeline.jsonl mandatory 7-field nodeId,agentId,attempt,latency_ms,tokens_est,status,errorClass per checkpoint-manager. Zero-deps true.

Last updated: 2026-08-14T12:38 CDT v5.1 Guard+Sync — active_tasks_sweep v1.2 max7 non-GPU 3 GPU exempt never cleared hillclimb_backoff max3/4 tempo :05 conf0.82

## SSOT Guard v5.1

- **SSOT board**: `bundles/coordination/active-tasks.md` ≤15 rows claimed/todo 3 LOCAL-GPU exempt hoops-v6 150ep composite 0.7937→0.85 top1 0.438→0.55 gridiron 32-d MAE 4.268→3.8 unified G2 0.685→0.64 per 2026-08-13 22:09 CT
- **Guard**: `bundles/scripts/all-lanes-busy-guard.js` v5.1 hillclimb_backoff max3/4 tempo :05 swarm faster conf0.82 — enforce max7 non-GPU, 3 GPU exempt never cleared, free slots = 7 - non_gpu_active, 0 free = no swarm log no-op <5s mandatory 7-field timeline.jsonl nodeId hillclimb-loop attempt latency_ms tokens_est status errorClass all_lanes_busy
- **Tool**: `bundles/scripts/board_sync.py` zero-deps pure python stdlib only triple-write workspace/.scout/missions/_cron/timeline.jsonl + bundles/ultra/runs/board-sync/timeline.jsonl + hidden_files status

## Active Crons (owner + required_fields + version 1.0+ tags always-on/operator + zero_deps true)

| id | owner | interval | file | purpose |
|---|---|---|---|---|
| active_tasks_sweep | operator | 30m interval UTC | active_tasks_sweep.json | Board Orchestrator v5.1 Guard+Sync — Check active-tasks.md clear stale >4h in-progress, claim one free lane if any, sync COORDINATION.md to all 7 repos + root push branch scout/board-sync- |
| all-lanes-busy-guard | operator | embedded 30m/5m tempo :05 | all-lanes-busy-guard.js v5.1 | Enforce max7 non-GPU 3 GPU exempt never cleared free=7-non_gpu 0=no-swarm <5s 7-field timeline nodeId hillclimb-loop all_lanes_busy |
| board-sync-tool | operator | on-demand + 30m | board_sync.py | Triple-write sync mirrors 8 repos COORDINATION.md idempotent zero-deps true stdlib only |
| dottie_triple_write_check | operator | 30m interval UTC | dottie_triple_write_check.json | Verify 7/7 triple-write healthy |
| goal_health | operator | daily 08:30 America/Chicago | goal_health.json | Goal health daily 08:30 CT |
| local_gpu_handoff | operator | 30m interval UTC | local_gpu_handoff.json | LOCAL-GPU handoff 3 exempt |
| foundation_dataset_build | operator | 30m interval UTC | foundation_dataset_build.json | Rebuild dataset when ledger changes |
| monthly_clean | operator | cron 0 3 1 * * America/Chicago | monthly_clean.json | Prune exports >30d |
| observability_tick | operator | 15m interval UTC | observability_tick.json | Live health |
| podcast_brief_auto_exec | goal:ultracode-brief-exec | 90s interval UTC | podcast_brief_auto_exec.json | 90s poll briefs TODOs |
| podcast_brief_watchdog | operator | 30m interval UTC | podcast_brief_watchdog.json | Brief watchdog |
| poll_merge_watchdog | operator | 30m interval UTC | poll_merge_watchdog.json | Poll merge heartbeat |
| self_improvement_board_poll | operator | 1m interval UTC | self_improvement_board_poll.json | Poll board self-improve |
| self_improvement_tick | operator | daily 04:00 America/Chicago | self_improvement_tick.json | Daily scan |

All crons log even no-change → timeline.jsonl mandatory fields nodeId,agentId,attempt,latency,tokens,status,errorClass per checkpoint-manager spec.
