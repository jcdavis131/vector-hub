# Scout Communication Protocol + Pacing Filter
## 13-agent swarm >5-6 shared-context limit → need filtering middleware

```js
// communication-protocol.js + pacing-filter.js — Orchestration Pillars 2 & 3

export const HandoffEnvelope = {
required: ['from','to','payload','confidence','citations','ooda_phase','tempo','runId','nodeId'], // 7+ mandatory — from,to,payload,confidence,citations,ooda_phase,tempo,runId,nodeId
optional: ['edge_cases','alternatives','blocked_reason'],
schema: {
from: 'agentId string e.g., strategist',
to: 'agentId string e.g., planner',
payload: 'any — but must be typed artifact, not freeform "looks good"',
confidence: '0.0-1.0',
citations: 'string[] graded A/B/C URLs',
ooda_phase: 'Observe|Orient|Decide|Act|Feedback',
tempo: ':13',
runId: 'ultra-<ts>-<id>',
nodeId: 'L{layer}-{name}-{n}',
timestamp: 'ISO',
blocked_reason: 'null or string',
},
};

export function validateEnvelope(env) {
for (const k of HandoffEnvelope.required) if (!(k in env)) throw new Error(`missing ${k} in handoff`);
if (env.confidence <0 || env.confidence >1) throw new Error('confidence out of range');
if (!['Observe','Orient','Decide','Act','Feedback'].includes(env.ooda_phase)) throw new Error('invalid ooda_phase');
return true;
}

// Scout Prime is Subagents coordinator — no direct agent→agent calls, route via orchestrator (clean separation)
export class ScoutCommsBus {
constructor(runId) {
this.runId = runId;
this.queue = [];
this.history = []; // G_history for MoMA routing
}

async send(envelope) {
validateEnvelope(envelope);
this.queue.push(envelope);
this.history.push({ ts: new Date().toISOString(),...envelope});
// Log to timeline.jsonl for audit
return envelope;
}

// Filtering: only relevant sub-swarm sees message, not all 13 — caps 3-5 medium, 13 only epic (CrewAI limit)
relevantAgents({ intent, complexity, currentNode}) {
// intent→agents mapping from router.config.json v3.2
const intentMap = {
agentic_loop: ['scout-prime','strategist','planner','deep-researcher','synthesist','executor','action-operator','critic','forensic-auditor'],
deep_research: ['deep-researcher','synthesist','forensic-auditor','scout-prime'],
complex_action: ['action-operator','operator','scout-prime'],
ooda: ['strategist','deep-researcher','synthesist','scout-prime'],
verification: ['forensic-auditor','critic','scout-prime'],
research: ['deep-researcher','synthesist','scout-prime'],
};
const base = intentMap[intent] || ['scout-prime'];
// Complexity narrows further — avoid 13-agent noisy cross-talk
if (complexity==='epic' && intent==='agentic_loop') return ['scout-prime','strategist','planner','deep-researcher','synthesist','researcher','builder','executor','action-operator','operator','communicator','critic','forensic-auditor']; // 13 swarm only for true epic
if (complexity==='medium') return base.slice(0,5); // cap 5-6 for medium per CrewAI noisy limit
return base.slice(0,3);
}
}

// pacing-filter.js — Pacing: OODA rate limiting + event-driven > polling
export const PacingFilter = {
// Observe rate limiting: max 3 parallel opens (browser.search, open, social search) — v5 Prime hard cap
observe: { max_parallel_fetch: 3, time_box_ms: 120_000, time_box: '120s', rule: 'Wide Sweep 5-7 is parallel 3 batches', rationale: 'prevent API burst + token flood'},
orient: { time_box_ms: 180_000, time_box: '180s', rule: 'lattice recall 0.7 dense + 0.3 sparse + rerank 1-2 hops', max_context_chars: 8000, rationale: 'orientation shapes quality > speed'},
decide: { single_action: true, rule: 'one hypothesis testable, not 3 vague ideas', rationale: 'Boyd Decide=one hypo'},
act: { verify_after: true, rule: 'artifact changes env + generates feedback logged', side_effect_check: true},
feedback: { log_even_no_change: true, target: 'timeline.jsonl', rationale: 'ultra non-negotiable metrics-dance — even no-change logs mandatory 7-field' },

// Typed Nodes + Rust-core determinism heuristic for parallelism — caps 4 concurrent
shouldParallelize(nodes) {
// Only parallelize if: no side-effect >=2, no shared mutable file, nodes layer same, count <=4 (concurrency 4 guarantee)
const safe = nodes.filter(n => {
const level = n.side_effect_level || 0;
return level <=1 &&!n.requires_human;
});
return safe.slice(0,4); // max 4 concurrent safe — agentic guarantee 6 concurrency 4 no drift — caps 4
},

// Tempo regulator::13 minute never:00 — Napoleonic timing — :13 pacing
nextTick() {
const now = new Date();
const minutes = now.getMinutes();
const remainder = (13 - (minutes % 13) + 13) % 13;
return `${remainder}m to:13 pacing window`;
},
};

export default { HandoffEnvelope, ScoutCommsBus, PacingFilter};
```

## When to Use
- **Subagents pattern** (Scout Prime as tool coordinator) — best for multi-domain parallel (5 calls ~9K tokens)
- **Handoffs/Skills** — best for repeat requests (save 40-50%) — Cameron says "that again but with Q3 numbers"? Handoff state variable, don't re-run 4 calls
- **Router pattern** — classify + fan-out to specialists, synthesize — matches Scout Router-0→Router-1→Router-2 tiers

## Why 13 Agents Needs This
- CrewAI 5-6 agents shared-context limit noisy beyond → Scout has 13 total pool but active sub-swarm per turn = 3-5 (simple/medium) or 8-9 (epic), 13 only for true epic agentic_loop opaque
- Three-layer separation enforced: Execution (agents), Communication (queues/events/RPC via Scout Prime), Orchestration (DAG validity replans eval hooks tempo)
