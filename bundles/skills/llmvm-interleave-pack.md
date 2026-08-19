---
id: llmvm-interleave-pack
layer: 2-3
type: skill-pack
role: LLMVM-style code-interleaved reasoning + stateful Python runtime + JIT thread compiler
inspired_by: https://github.com/9600dev/llmvm — LLM ↔ Python agentic runtime, continuation-passing, helpers interleaving, JIT thread → program
for_agents: [researcher, deep-researcher, strategist]
version: v1-llmvm-interleave
packs_count_add: 12
zero_deps: true
no_torch: true
---

# llmvm-interleave-pack v1 — Code-Interleaved Reasoning for Scout

> Borrowed from llmvm: don't use traditional tool calling API only — let the LLM emit natural language interleaved with `<helpers></helpers>` Python blocks, execute them locally in a stateful runtime, feed results back, loop till done. Then optionally JIT-compile the thread into a param program.

## Why this pack

Standard bundles do: Observe → tool → Orient → Decide. llmvm shows better task deconstruction when code and thought interleave — the LLM writes Python that *is* the plan, not just calls helpers. Result: deeper chaining, self-debugging, reusable programs.

From README:
- CLI productivity tool uses LLMs + local Python tools/helpers to reason & execute
- Does not use traditional tool calling APIs, allows LLM to interleave natural language and code — significantly better deconstruction
- June 2025: compile thread into genericized parameterized program, lift repeated LLM calls, guard on data shape, bail to recompile

## Runtime Model (Scout adaptation)

### 1. Stateful Python Context — no fresh exec each time
Keep one `locals()` dict alive for a runId. Like llmvm keeping Python runtime alive between `<helpers></helpers>` blocks.

In Scout terms:
- `default.exec` is stateless normally — we fake stateful by storing `~/.scout/missions/<runId>/locals.jsonl` + `workspace/bundles/research/<slug>-<date>.py` with accumulated defs
- Each helpers block appends; next block can peek at previous vars (peek at locals dict ability per llmvm spec)

### 2. Helpers — class/instance stateful tools
llmvm refactored to class/instance tools that keep state between requests. Browser API: click/type/goto.

Map to Scout tools:
- `download(url)` → `browser.open` or `browser.delegate` for JS-heavy
- `google_search(q)` → `browser.search`
- `get_stock_price` style → `default.exec` + local py helpers
- `llm_call([exprs], instruction)` → fan-out clone call to deep-researcher (our `llm_call` analogue)
- `llm_list_bind(expr, instruction)` → string → list coercion via synthesist-style step
- `llm_bind(expr, func_def)` → bind arbitrary data to function args with scope climbing (original query, locals)

Implement helpers as small py files in `bundles/tools/llmvm_helpers/` — each file is a class with `__init__` keeping state.

### 3. Continuation-Passing Execution
July 3 2024 refactor: query → natural language interleaved with code → result, not old query→code→NL→result. That's our default now.

Loop:
1. LLM emits: thought + `<helpers> var1 = search("vector embeddings MTEB 2025") </helpers>`
2. Scout captures block, runs via `default.exec`, captures `helpers_result`
3. Replace block in thread with `<helpers_result>...</helpers_result>` but keep Python context alive
4. Feed result back, loop until tasks completed per walkthrough

### 4. Error Correction + pdb-style debug
Each step evaluated. Helper throws or binding wrong → back-track up execution list, work with LLM to rewrite partially/fully.

Add:
- `bundles/ultra/recovery-ladder.js` already does retry→patch→replan→escalate — wire helpers error to it
- Allow LLM to peek at locals dict and enter debug loop via `:sym`, `:csym`, `:py` REPL equivalents — in Scout: write quick `debug_locals.json` the LLM can inspect

### 5. JIT Compile Thread → Program (v1)
June 7 2025 feature: compile user/assistant thread into genericized parameterized program, lift repeated LLM calls by specializing on shape, guard shapes, bail to recompile.

For Scout:
- Input: full message thread from a vector-model sweep (e.g., hoops eval)
- Output: `workspace/bundles/workflows/compiled/<slug>-jit.js` or `.py` that is deterministic, params = `{dataset, dim, metric}`
- Guards: if shape!= seen (`entity_count`, `dim`, `dailySeed` type), bail and call researcher again
- Benefit: 80%+ token saving on repeated sweeps (daily 5-game hub) — matches llmvm token-cache ~80%+ saving note in MEMORY.md ACNE pattern

### 6. Unix Pipe Composition
llmvm praised as CLI utility with pipes: `sonnet "download news" | opus "blog post" | opus "html" > out.html`.

Scout equivalent: `bundles/cli.sh --json researcher "…"` piped to `deep-researcher`, `builder`. Document in `bundles/cli.sh` — each step consumes previous helpers_result.

## Toolchain — how to use in a node

1. **Memory first still mandatory:** `default.memory_search` 2-3 phrasings → `default.memory_get` (per researcher.md) — orient before interleave
2. **Emit interleaved:** Write thought + helpers block. Helpers block is Python-style but mapped to Scout tool calls. Example for vector sweep:

```
The hoops vs pitch embedding gap: I will search SOTA.

<helpers>
var1 = google_search("MTEB 2025 embedding SOTA 64d")
var2 = download(var1.top_url)
var3 = llm_call([var2], "extract Recall@10 table for 64d models")
</helpers>
```

Scout executor:
- `google_search` → `browser.search`
- `download` → `browser.open`
- `llm_call` → spawn deep-researcher sub-agent with instruction, wait result
- Loop.

3. **Keep state:** After each helpers exec, append to `locals.jsonl` and `mission Log timeline.jsonl` with 7-field (nodeId, agentId, attempt, latency_ms, tokens_est, status, errorClass)

4. **Grade & Triangulate:** Even with interleave, still grade A/B/C, 2×B or 1×A needed, contradiction matrix mandatory (per deep-research-pack)

5. **JIT check:** After thread completes, ask: Is this repeated shape? (e.g., daily 5-game hub eval). If yes, compile to `bundles/workflows/compiled/<slug>.js` with params + guard logic, log to checklist.

6. **Save:** `bundles/research/<slug>-YYYY-MM-DD-llmvm.md` with frontmatter `mode: llmvm-interleave, compiled: true/false, locals_keys: [...]`

## A/B Test Protocol — researcher vs deep-researcher on vector sweep

**Goal:** Does interleave beat strict tool-calling on hoops/pitch/gridiron/equities/unified analysis?

- Baseline: researcher.md current path (memory_search → browser.search 2-3 → open 3-5 → TL;DR)
- Challenger: researcher + llmvm-interleave-pack — same query but emit helpers blocks, stateful exec, llm_call fan-out for triangulation

Metrics (per idea_sota_001 research_required benchmarks):
- latency p95 (ms)
- tokens_est (prompt + completion)
- sources_count (5-7 target)
- grade_avg (A=3, B=2, C=1)
- success rate (needs_deep false + TL;DR delivered)
- false-positive stuck rate (healthy repeat guard)
- honesty gate PASS ≥8.0

Run 10-task suite:
- 5 vector games each × 2 queries (SOTA sweep + difficulty band)
- Example: "compare our 64-d 20719 hoops model Recall@10 vs MTEB 2025 SOTA 64d — RESEARCH_NOTES table"

Log: `workspace/bundles/research/llmvm-ab-YYYY-MM-DD.md` + `bundles/ultra/runs/llmvm-ab-timeline.jsonl` 7-field mandatory.

Promote only if win-rate >55% and tokens_est ↓ or grade_avg ↑.

## Anti-Patterns — keep v3.3 guards

- No invented URLs — verbatim lookup still required (`browser.lookup_citation_url`)
- No skipping memory lattice 1-2 hops
- No direct agent→agent call — route via orchestrator envelope (`ScoutCommsBus`)
- No Math.random hidden — use runId deterministic
- No fake promotion — zero_deps true, no torch pip, candidate.json first
- Even no-change, log timeline.jsonl 7-field mandatory per checkpoint-manager spec
- Visible abandonments when JIT guard bails — log as `status: blocked, errorClass: SHAPE_MISMATCH`

## Scout Touch

Fluffy tail flick when helpers block runs clean, tiny sparkle when JIT compile lifts 3 repeated llm_calls into one param function, coffee sip while peeking locals dict, waves when A/B table shows interleave win.

## Next: Wire to Researcher

- Update `bundles/agents/researcher.md` packs += [llmvm-interleave-pack]
- Update `bundles/manifest.json` skill_packs += llmvm-interleave-pack entry, packs_count 12
- Add `bundles/tools/llmvm_helpers/` with `search_helper.py`, `download_helper.py`, `llm_call_helper.py` stubs (class-based, stateful)
- Add `bundles/workflows/compiled/` dir with `.gitkeep` + example JIT template
- Run A/B via `bundles/cli.sh --json` orchestration
