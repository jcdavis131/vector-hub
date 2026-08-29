---
id: main-side-churn-aligner
enabled: true
mode: task
schedule:
  kind: interval
  timezone: UTC
  at: 2026-08-19T19:02:58
  every: 5m
delivery: []
metadata:
  originating_channel_context_json: '{"originating_channel":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"49af1944-5756-4791-98ec-e96b58662957"}'
---
# Main-Side Churn Aligner — Glimmer Local 30B 131k Always-On

> Glimmer local-first: try Ollama http://localhost:11434 model glimmer / muse-glimmer num_ctx 131072 reasoning medium/high, system prefix [reasoning:X]. If down → honest 503 but stdlib board scan still does 7-field triple-write. Always-on anywhere/anytime, no cloud token loop, privacy-sensitive. Wrapper: ~/workspace/goals/churn-orchestrator-1-main-1-main-side/files/glimmer/churn-aligner-glimmer-agent.ts

# Main-Side Churn Aligner — feeds main with critical next steps

Runs every 5m, delivers to main.

Check:
- active-tasks.md ACTIVE/DONE counts
- side chats list (1 main-side churn: c86e297d-ecc3-451c-9658-b648d0c54a31 MUST stay alive, plus N swarm chats for parallel bytes — do not archive swarms)
- goals/*/GOAL.md blockers
- ALIENWARE_HANDOFFS.md for pending GPU markers

If new critical step found -> send message to main chat via chat.send_message with:
  - what / why / which goal / which branch
  - one sentence max for why it unblocks downstream
Else: write no-change 7-field entry (nodeId=main-side-churn-aligner-glimmer agentId=c86e297d attempt latency_ms tokens_est status errorClass + glimmer_used glimmer_model reasoning context_tokens 131072 always_on anywhere_anytime). Triple-write: .scout/missions/_cron/timeline.jsonl + goal files + memory daily.

Keep 1 main + 1 churn aligner always-on, plus dedicated swarm side chats (schools, unified G2/G3, daily boards/PWA, GH unblock). Never archive churn or swarms to enforce old 1+1. Zero-deps true. English or code only.
