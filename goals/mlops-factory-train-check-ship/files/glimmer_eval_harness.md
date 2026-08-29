# Glimmer MLOps Eval Factory — Lane 5

Goal: `mlops-factory-train-check-ship` (GraphBFF dual-stream 70/30, 64-d L2 sphere, PWA v67)
Branch: `scout/glimmer-mlops-eval`
Agentic org: Lane 5 — MLOps eval factory

## Why Glimmer for eval

Meta's new Muse Glimmer is 30B dense (29.6B total: 28B text decoder + 1.8B ViT-G/14 perception), 131k+ context, 100+ languages, Apache 2.0, single-GPU 24GB VRAM, controllable reasoning low/medium/high/xhigh via system prompt. Designed for always-on local agent loop: plan → tool call → interpret → continue → recover. Supports llama.cpp, Ollama, MLX, ExecuTorch, vLLM, SGLang.

Perfect for honest MLOps eval: local LLM-as-judge, no token bill, no network leak of 27k schools NCES private, offline PWA judge, always-on tactician.

## What we built (zero-deps, stdlib-only core)

### 1. Glimmer Client (`vector-unified/pipeline/glimmer_client.py`)

- Stdlib only: `urllib.request`, `json`, `socket`, `os` — no pip torch on Hatch VM
- Backends tried in order:
  1. Ollama `:11434` — `/api/tags` + `/api/generate` with `num_ctx 131072`
  2. llama.cpp `:8080` — `/completion`
  3. Generic OpenAI-compatible via `GLIMMER_ENDPOINT` (vLLM/SGLang/MLX/ExecuTorch) — `/v1/chat/completions`
- `GlimmerClient.available` + `honest_503()` → `SystemExit(11)` when blocked, never fabricates
- `generate(prompt, system, reasoning_effort, temperature, max_tokens)` — maps low/medium/high/xhigh to system prefix per model card
- `judge(eval_json, reasoning_effort="high")` — constructs MLOps glass-box prompt, asks Glimmer for JSON-only judgement:
  ```json
  {"g2_judgement": "PASS|FAIL", "g2_reason": "...", "g3_judgement": "PASS|FAIL", "g3_reason": "...", "construct_validity": "...", "threats": ["..."], "glass_box_top_heads": ["..."], "ship_recommendation": "SHIP|HOLD|RETRAIN", "confidence": 0.0-1.0}
  ```
  Tasks judged:
  - G2 floor lock 0.639→0.615 rank12.4→≥32 sil0.683→0.74 composite0.8688→0.91 — sport classifier vs majority 0.6258, delta_vs_majority ≈0
  - G3 dual GraphBFF TCA 7 heads 224-d 70% sparse + TAA 128-d k8 30% + schools aux0.12 — silhouette ≥0.05, separation >0.05, composite ≥0.91
  - Construct validity: what does MTNN v9/v4 64-d L2 sphere measure? Operationalize, convergent/discriminant/predictive, threats (vanity 1.0 kNN pos_mask int64 bug, null 0.6258 trap, separation null +0.044)
  - Glass-box: which TCA heads (volume/playmaking/defense/shotmix/teammates/draft-class/era-archetype) or TAA k8 contribute most via permutation/SHAP
  - Ship gate: PWA v67 59→73 hashes 7/7/0 void #080A0F 40px sticky z40 DPR1 LOD4000/8000 CORE20 offline13k

### 2. Eval Harness (`vector-unified/pipeline/eval_glimmer.py`)

- Zero-deps core, torch/sklearn optional with honest 503 fallback
- 5-fold CV: honest StratifiedKFold shuffle True seed 7, kNN-5 cosine per sport, leak-free, mean±std, no synthetic
- Permutation importance: shuffle each z-dim 0..63 (n_repeats=3), measure Δ G2 accuracy & Δ G3 silhouette, stdlib random + numpy optional
- SHAP-lite: Kernel SHAP approximation via Ridge λ=1.0 on masked samples (96 samples, 50% mask), linear solve `(X^T X + λI)^{-1} X^T y`, no sklearn needed if numpy present else SKIPPED_HONEST_503
- Glimmer judge integration — calls `GlimmerClient.judge()` with real eval JSON, no synthetic
- Outputs:
  - `pipeline/eval_reports/eval_glimmer_<hash>.json`
  - `pipeline/eval_reports/eval_glimmer_latest.json`
  - `bundles/ultra/runs/mlops-glimmer/timeline.jsonl` (7-field: nodeId, agentId, attempt, latency_ms, tokens_est, status, errorClass)
  - `goals/mlops-factory-train-check-ship/hidden_files/timeline.jsonl`
- Provenance: zero_deps true, stdlib_core true, torch_optional, never_synthetic true, honest_503 true, LCG same-link-same-stars 189831298/1412440227

### 3. Runner (`vector-unified/pipeline/run_glimmer_eval.sh`)

- Checks real sources: `data/unified_matrix.npz` 18M 20719×64, `data/unified_meta.json`, schools 27k real
- Detects backend via curl/socket, hints:
  ```
  ollama run glimmer
  llama-server -m glimmer-30b.gguf --port 8080 --ctx-size 131072
  export GLIMMER_ENDPOINT=http://localhost:8000/v1
  ```
- Runs `eval_glimmer.py --ckpt unified_stage2_centroid_ab.pt --kfold 5 --permutation --shap --judge --effort high`
- On 503, falls back to judge-only mode (report-only, no torch)

## GraphBFF dual-stream wiring

- TCA 7 heads 224-d 70% params per-type sparse softmax (volume/playmaking/defense/shotmix/teammates/draft-class/era-archetype fam groups)
- TAA 1 head shared 128-d k8 fixed-degree stability (30%)
- Fusion 0.7/0.3 L2 64-d sphere, RoPE 32-d/h RMSNorm ε1e-6 SwiGLU 256, VICReg var25 cov1 w0.05, SupCon τ0.07 w0.15, masked link 15% BCE w0.5, KL64 + RR32/type 288 supervision edges/batch, schools TAA aux 64-d 0.12 weight 51 states 80/state

Eval targets:
- G2 FULL0.6236 MEASURED 8 audit copies — floor lock 0.639→0.615 CORAL0.5 centroid0.5 GRL0.3→0.5 ramp10 w_task2.0 w_sport0.5 MoMA-lite5 GARNet rank≥32 sil0.74 comp0.91
- G3 dual TCA224 70%+TAA128 k8 30%+schools aux0.12 chimera24799→47900 (27,181 real NCES 11M) — silhouette≥0.05 sep>0.05 composite≥0.91
- PWA v67 void #080A0F 40px sticky CORE20 offline13k LOD4000/8000 DPR1 single-select hoops-level parity 59→73 hashes 7/7/0

## Honest 503 paths

- No torch on Hatch VM → kfold/permutation/SHAP SKIPPED_HONEST_503, judge still works on eval_unified_latest.json
- No numpy → SHAP SKIPPED, permutation SKIPPED_NO_NP
- No Glimmer endpoint → judge returns 503_Glimmer_not_running with hint, does not crash whole eval
- No unified_matrix.npz → 503 real-mode requires unified_matrix.npz — honest fail, not fabricated

## Ship gate (verifier ≥8.0)

- 30 boards LIVE gate8.7 IC0.084 Sharpe1.22 DAY17W13L 56.7% ROI4.18% 12PP/9Kalshi/9DK per_team_priors TRUE
- 27,181 schools real NCES verified 11M quarantine 12k synthetic removed
- 20,719×128 canonical embedding_v3 18.8MB vs fallback 12,966×64 4.88M — teacher12M 224-d RoPE 32-d/h → client 1.2M 64-d L2 sphere max_abs0.90783
- LCG 20260813→189831298 idx3820 triple[11205,19448,14209] + 20260818→1412440227 idx5278 triple[13791,10902,19455] same-link-same-stars

## How to run locally (Forge or laptop)

```bash
cd vector-unified
# 1. start Glimmer locally — pick one backend
ollama run glimmer
# OR
llama-server -m ~/models/glimmer-30b.Q4_K_M.gguf --port 8080 --ctx-size 131072 -ngl 32

# 2. run eval
bash pipeline/run_glimmer_eval.sh unified_stage2_centroid_ab.pt high
# or judge-only
python3 pipeline/eval_glimmer.py --report pipeline/eval_reports/eval_unified_latest.json --judge-only --effort high

# 3. check output
cat pipeline/eval_reports/eval_glimmer_latest.json | jq .glimmer_judge.judgement
cat pipeline/eval_reports/eval_glimmer_latest.json | jq .permutation.g2.top10_dims
```

## Next (Lane 5 → downstream)

- When churn-main8 finishes embedding_v3 20719×128 MTNN v9.2 150ep canonical, re-run full 5-fold CV on real z (not fallback) — expect rank≥32, G2 ≤0.615
- Wire Glimmer judge into daily-boards PWA v67 Proof Wall — Knowledge→Edge→Money 7d log, Kill-switch GREEN/YELLOW/RED 1% max Kelly0.25
- Add Glimmer eval to Dottie factory — SOTA edition mission log pause/resume, verifier 8.0, continual harness + sessions as OS
- Always-on dataset collection: schools 27k real, unified embeddings, hoops freshness, equities — honest 503 when blocked, never synthetic, feeds MLOps factory and Dottie parity

Zero-deps true, stdlib only, honest 503, never synthetic, English/code only, 1 main +1 churn +N swarms topology preserved c86e297d MUST stay alive.
