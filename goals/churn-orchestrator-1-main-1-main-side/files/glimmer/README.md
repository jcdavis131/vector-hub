# Lane 3 — Glimmer Orchestrator Tactician

Local Glimmer inference replaces cloud calls for churn aligner + climb-check.

## Why Glimmer
- 30B dense (29.6B = 28B decoder + 1.8B ViT-G/14), Apache 2.0, distilled from Muse Spark
- Designed for agent loop: plan → tool call → check → recover, single GPU 24GB VRAM
- 131072+ ctx, 100+ langs, controllable reasoning low/medium/high/xhigh via system prompt
- Integrations: llama.cpp, Ollama, LM Studio, vLLM, SGLang, ExecuTorch, MLX
- Always-on anywhere/anytime, offline, no per-token API charge, privacy-sensitive

## What changed
- `churn-aligner-glimmer-agent.ts` — TS zero-deps fetch wrapper, healthCheck + chat with num_ctx 131072, fallback model `muse-glimmer`, triple-write 7-field even no-change
- `climb-check-glimmer-wrapper.sh` — bash zero-deps, curl to Ollama, low reasoning fast path
- Preserves: nodeId, agentId=c86e297d (MUST stay alive), attempt, latency_ms, tokens_est, status, errorClass
- Topology: 1+1+N preserved, c86e297d +3 swarms +3 LOCAL-GPU exempt + loop
- SSOT: active-tasks.md ACTIVE 7 FREE 3, ALIENWARE 1 DONE 27k +3 PENDING single Forge lane hot

## Always-on anywhere/anytime
- Local inference removes network availability + per-token charges from loop (hardware/electricity still cost)
- If Ollama down → honest 503 but stdlib fallback still does board scan + 7-field log (never fake success)
- Env: GLIMMER_MODEL=glimmer OLLAMA_BASE_URL=http://localhost:11434 GLIMMER_REASONING=medium|low

## 7-field compliance
Every tick writes even no-change: nodeId, agentId, attempt, latency_ms, tokens_est, status, errorClass → timeline.jsonl triple-write + memory daily + goal files.

## Integration
Cron bodies now call local wrapper first, cloud LLM only as fallback (future removal). Branch scout/glimmer-orchestrator.
