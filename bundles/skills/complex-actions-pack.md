---
id: complex-actions-pack
layer: 3
type: skill-pack
role: Multi-system action chaining with OODA loops + agentic best practices
tools: [default.cron, default.devices, default.goals, default.exec, default.read, default.write, default.trash, browser.search, browser.delegate]
pack_for: [action-operator, executor, operator, scout-prime]
v3_1_agentic: true
---

# complex-actions-pack v3.1 — The Closer Engine (OODA-Enabled)

When: touches >1 system, writes, money, calendar, external world. Long-running agentic loops.

## 9 Production-Grade Principles (from arXiv 2512.08769 + dev.to)
- Tool-first over MCP, Pure-function invocation, Single-tool + single-responsibility agents, Externalized prompt management, Responsible-AI consortium, Clean separation workflow vs servers, Containerized scale, KISS, Deterministic orchestration
- Orchestration MUST guarantee: Structured Execution (DAG/state machine), Tool Safety (schema validation), Memory Mgmt (read/update discipline), Reasoning Boundaries (max steps), Eval Hooks, Multi-Agent Coordination (routing, message passing, concurrency)

## Stack
- `gmail`, `google_tasks`, `google_calendar`, `google_drive`, `google_docs`, `google_sheets`
- `plaid` / `duffel` / `opentable` / `flightaware` / `shopping`
- `default.devices status|describe|invoke`
- `default.cron add|list|remove`
- `default.goals add_entry`
- `web_artifacts`

## Protocol: OODA-Enabled Action Chaining v3.1

1. **Observe:** Memory pull + device status + calendar agenda bounds + gmail search 7d + file ls before write. What's true now? (no guessing)
2. **Orient:** Filter using lattice + culture + past launches (Launched = live URL + 3 users + payments/analytics by Aug 31 11:59pm CT). Is this tool call safe? Single-responsibility? Schema valid?
3. **Decide:** One hypothesis chain step: plan gmail→tasks→calendar→drive→sheets→commerce→devices→cron. Show if >3 steps. Max 7 steps per loop (KISS). Externalize prompts to files if used.
4. **Act:** Execute topological, max 4 concurrent safe nodes. Log each: action + id/path + result to timeline.jsonl. If blocked → status:blocked with precise ask + resolution_path.

5. **Loop & Verify:** Re-read what you wrote (read, open draft, calendar get). Capture proof IDs. Feedback → next Observe.

6. **Idempotency:** Dedup key `goal+date+type`. Search before create. Skip if exists same payload, return existing id.

7. **Rollback:** For each write store undo: draft→delete, event→remove, file→trash put, cron→remove. Fail step n → rollback 1..n-1 auto + log.

8. **Monitor Hook:** If watch/when: `cron add id:<slug>-watch kind:interval|daily time:HH:13 delivery {surface:main}`. Owner `goal:<slug>` when goal-tied. Use :13 minute. Stop condition + log even no-change to hidden_files/cron_health.jsonl.

9. **Agentic Loop Control:** Two loops: Linear for analysis (Observe→Orient→Decide→Act sequential), Circular streaming for live enrich (background agents enrich context real-time via comm layer). Never agent calls agent directly — route via orchestrator.

10. **Eval Hooks:** After each Act, self-score hint 1-10, check correctness/reliability/coherence/tool_failure/hallucination/comms/quality. Fail → repair not replan first.

Error hygiene: rate limit → 30s backoff 2× then blocked retryable:true. Offline device → ask open Hatch phone then retry. Memory chaos → halt + re-orient.
