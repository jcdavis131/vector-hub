# HEARTBEAT.md — Scout v5 Prime Cron Index (SSOT = bundles/cron.d/*.json)

> Every cron needs owner + schedule + logged entry even "no change" → timeline.jsonl per checkpoint-manager spec (nodeId, agentId, attempt, latency, tokens, status, errorClass). HEARTBEAT.md is index only.

Last updated: 2026-08-07T09:47Z America/Chicago • 13 crons • operator-owned always-on • branch scout/orchestrator-hardening

## Active Crons

| id | owner | interval | file | purpose | logs to |
|----|-------|----------|------|---------|---------|
| active_tasks_sweep | operator | 30m | active_tasks_sweep.json | Sweep active tasks → clear stale >4h, preserve LOCAL-GPU OOM, claim free lane, sync COORD 7 repos | .scout/missions/_cron/timeline.jsonl + bundles/ultra/runs/timeline.jsonl |
| dottie-vec-monitor | goal:refine-dottie... / operator | 30m | dottie-vec-monitor.json | Dottie factory monitor + vec hub verifier — lightweight no-torch — hidden_files only | goals/.../hidden_files/cron_health.jsonl + .scout/missions/_cron/timeline.jsonl |
| dottie_triple_write_check | operator | 30m | dottie_triple_write_check.json | Verify dottie 7/7→17/17 triple-write | bundles/ultra/runs/timeline.jsonl |
| goal_health | operator | daily 08:30 America/Chicago | goal_health.json | 8:30am goal slip-proof check → goal_health.jsonl → mission timeline | bundles/memory/goal_health.jsonl + .scout/missions/*/timeline.jsonl |
| local_gpu_handoff | operator | 30m | local_gpu_handoff.json | GPU handoff if local available | bundles/ultra/runs/ |
| monthly_clean | operator | cron 0 3 1 * * America/Chicago | monthly_clean.json | Clean exports/ monthly — 1st 03:00 CT | workspace/exports/ + .scout/missions/_cron/timeline.jsonl |
| observability_tick | operator | 15m */15 * * * * | observability_tick.json | **Live health collector** — node bundles/observability/metrics_collector.js → metrics.jsonl + .metrics.log + dashboard_metrics.json — OODA 4/4, agentic 6/6, tempo :13, MoMA 5-tier, G_workflow+G_history, checkpoint 7-field, verification budget3, pacing max3 | bundles/ultra/runs/metrics.jsonl + bundles/memory/contacts_harness/.metrics.log + bundles/observability/dashboard_metrics.json |
| podcast-brief-auto-exec | goal:ultracode-brief-exec | 90s | podcast-brief-auto-exec.json | Turns briefs into TODOs, claims lanes, paces max3/4 :13 — SSOT mirrors interval md | bundles/ultra/runs/podcast-brief-auto-exec.jsonl + .scout/missions/_cron/timeline.jsonl |
| podcast_brief_watchdog | operator | 30m | podcast_brief_watchdog.json | Morning/evening brief watchdog — manifest != state last_slug stale>15m | bundles/ultra/runs/ |
| poll_merge_watchdog | operator | 30m | poll_merge_watchdog.json | Poll sync_log.jsonl + poll_merge.log heartbeat restart if >15m | bundles/ultra/runs/ |
| self_improvement_tick | operator | daily 04:00 America/Chicago | self_improvement_tick.json | Self-improvement loop reads runs → suggests skill upgrade | self_improvement/staging/ |
| sync_bundles | operator | hourly 0 * * * * | sync_bundles.json | Bundles manifest mtime → TLPG sync, zero-deps local-only | bundles/memory/contacts_harness/.sync.log + ultra/runs/timeline.jsonl |
| vector_hub_chimera_check | operator | 30m | vector_hub_chimera_check.json | Vector hub chimera 20k+ cross-sport health 5/5 OK DM_PROVENANCE 7/7/0 | bundles/ultra/runs/ |

## Zero-deps Enforcement

- `bundles/zero_deps.json` {"zero_deps":true,"allow":"acne:./src"} — no pip, no cloud, ACNE optional local
- Collector `metrics_collector.js` uses only fs/path/os — valid via `node -c` — no npm install

## Observability File Contract

From `bundles/observability/metrics_collector.js` v4:
- Reads: `bundles/manifest.json`, `bundles/ultra/runs/`, `bundles/memory/contacts_harness/nodes.jsonl`, `bundles/cron.d/*.json`
- Writes JSONL: `bundles/ultra/runs/metrics.jsonl` (line-delimited per-run), `bundles/memory/contacts_harness/.metrics.log`
- Writes snapshot: `bundles/observability/dashboard_metrics.json` + `ultra_metrics.json` for static dashboard artifact to embed
- Fields: `{runId, at, ooda:{fidelity:"4/4",steps:[4]}, agentic:{fidelity:"6/6",guarantees:6}, tempo:{current:":13"}, moma:{tiers:5}, graph:{workflow_nodes,g_history,tlpg_nodes,tlpg_edges,by_class}, checkpoint:{total,triple_write_verified,required_fields[7],last_10_health}, verification:{budget3,threshold8.0,earlyExit0.3,eval_hooks6}, pacing:{max3,concurrency_safe4,orient_timebox,observe_timebox}, recovery:{stages5,ladder}, stuck:{thresholds,lenses9}, last_sync,last_goal_health,last_checkpoint,crons_count,crons,manifest_version,agents_count,packs_count,zero_deps}`

## Timeline Compliance

Every cron tick writes timeline.jsonl entry even no-change with required 7 fields:
`nodeId`, `agentId`, `attempt`, `latency`, `tokens`, `status`, `errorClass` — see `bundles/ultra/checkpoint-manager.js` `requiredTimelineFields`

## Dashboard Link

- Live: `ts-spaces/scout-ops-live/` → [open](sandbox://workspace/ts-spaces/scout-ops-live/index.html)
- Keep-sake: `your_files/scout-ops-live/index.html` static single-file

## Scout Persona

Cute fluffy tabby with tiny desk who paces, steams coffee, waves/smiles, sparkles on PASS ✨ — everyday language outside, technically tidy inside.
