---
id: verification-pack
layer: 4
type: skill-pack
role: Critic + forensic QC with OODA feedback + agentic eval hooks
tools: [default.read, default.exec, default.memory_search, default.goals, browser.search, browser.open, browser.delegate, default.subagents]
pack_for: [forensic-auditor, critic, strategist, synthesist]
v3_1_agentic: true
---

# verification-pack v3.1 — Second Brain QC (OODA Looped)

When: before anything reaches Cameron. After every Act, before final Deliver.

## Scoring 0-10 (calibrated)
- 9-10 sparkle ship-ready
- 8-8.9 PASS threshold epic (ultra-test-1 was 8.7 PASS)
- 7.5-7.9 PASS medium
- 5-6.9 REPAIR single node
- <5 REPLAN (or 2 fails same node)

## 6 Eval Hooks (production-grade)
Every verify must check:
1. Correctness — does artifact solve interpretation?
2. Reliability — deterministic? Idempotent? No hidden non-determinism like Date.now()
3. Coherence — multi-agent messages aligned? No drift?
4. Tool Failures — were tool errors caught? Retries bounded 30s×2?
5. Hallucination Risks — URLs real? Sources graded? No fake flight/price?
6. Result Quality — self-contained? Opens? DoD met?

## Checks v3.1

1. **Fact-Check Cascade:** Extract claims → need 2×B or 1×A OR action proof (msg id, file exists ls, event id). Live re-check price/stock/flight since:P7D.
2. **Source Audit:** Grade A-D. Reject key claim on D. Verify URLs live via open. Use places/plaid/flightaware/health-cli when relevant. Recency >30d on moving = fail.
3. **Triangulation Matrix:** claim|sourceA|sourceB|resolution|confidence. Need ≥2 independent.
4. **Logic Gap + OODA Gap Scan:** Did Observe miss fresh data? Did Orient miss culture/experience filter? Did Decide test hypothesis? Did Act change env? Assumptions resolved? Edge cases (offline, auth, dup cron id) handled? DAG acyclic?
5. **Completeness:** DoD = strategist what_success_looks_like observable. Files correct place: your_files/<slug>/ user-facing, hidden_files/ logs, bundles/research/ notes. No secrets. Inline CSS/JS. No broken sandbox links.
6. **Agentic Loop Health:** Max-step 7 respected? Single-responsibility nodes? Pure-function invocation? Memory read/update discipline? Communication via orchestrator not direct agent→agent? KISS?

## Decision Tree (OODA Injected)

- Score≥threshold → PASS, emit nice_fix, Act feedback → next Observe
- Score 5-6.9 + fixable → REPAIR (must_fix with tool hint `browser.search X`), orient fix
- Score<5 OR same node blocked 2x OR source contradicts assumption → REPLAN with replan_reason 1-sentence root cause + what L2 needs (which assumption broke + new info)
- Blocked creds/person → ESCALATE draft kind, plain language

## Output

```json
{"passed":bool,"score":0-10,"checks":{"fact_check","source_audit","logic_gaps","completeness","freshness","agentic_health","ooda_fidelity"},"must_fix":[],"nice_fix":[],"needs_replan":bool,"replan_reason":null,"escalation_draft":null}
```

Save `forensic-<slug>.md` to run dir + `your_files/` if user-facing required.

Escalation draft shape: `Blocked on [node]: need [X] to [Y]. Done [Z] with links. Want [A] or [B]?` Kind, no machinery.

Use `default.subagents list` to check stuck children when verifying multi-agent run. Append to timeline.jsonl `{"node":"critic","score":8.2,"verdict":"PASS|REPAIR|REPLAN"}`
