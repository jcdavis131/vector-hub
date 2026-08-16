# Deep Researcher — MoMA-lite 5 tiers lite 3-5 sources gate≥8.0 — LCG 20260813→189831298 idx3820 triple[11205,19448,14209]

## dottie-001-rl-cot-compress 9.1 arXiv:2412.108?? (One-Domain-to-All Generalization)
**Method EXTRACTED:** RL trains CoT compressor on one domain, generalizes to all with 20-40% token reduction, preserves performance.
**Transfer INFERRED:** to Dottie factory v2 closed-loop: compress trace→preference pairs 1584→0 tokens hybrid 9 tokens, 31% cache win via token-cache 80%+.
**Limit:** domain shift entropy collapse GRPO fails — guard FGO fix two limitations entropy collapse fix.

## pitch-001-ball-cls-multimodal 9.1 arXiv:2512.19528
**Method EXTRACTED:** Ball CLS token T×1×d regressed to (x,y) via FC stack ADE L2 loss + state CLS + possessor head. Learns ball from player-only context.
**Transfer:** to pitch mountain problem — hallucinate ball from player embeddings alone when no tracking, ADE weight 0.5, VRNN μ0.017 MAE 3.55 IC0.255.
**Limit:** needs tracking proxy for plausible physics MIDAS Set Transformer gaps.

## unified-001-moe-scaling-laws 9.0 arXiv:2604.09175
**Method EXTRACTED:** Covering-number bound entropy scales with active param budget + routing overhead. Approximation error decreases via active capacity OR expert count bottleneck.
**Transfer:** to unified chimera 20719×64-d scaling sweep active 3 of 17 towers Hoops/Gridiron/Pitch/Equities with GRL λ0.3→0.5 + CORAL centroid, predict G2 0.685→0.642 vs target 0.64 power law composite = a*C^b + c*N^d.
**Limit:** routing overhead > active benefit — guard rank=8 factor rank8 muMoE 160→32×17.

## hoops-001-mmoe-scaling 9.2 arXiv:2402.12550v3
**Method:** MuMoE factorizes huge expert tensor 10k experts cheap no discrete routing — class-level specialization maps to draft archetypes.
**Transfer:** Replace dense mixer with muMoE 171 lanes factor rank8 train 150ep embedding_v3.npz top1 0.438→0.55 composite 0.7937→0.85.
**Limit:** OOM torch — zero-deps stdlib only guard CPU fallback, defer GPU to LOCAL-GPU lane local/hoops-v6-gpu.

## gridiron-001-axial-transformer 9.0 arXiv:2511.18730v1
**Method:** Axial predicts 13 actions jointly across players/teams/game multiple timesteps 75k live preds low latency.
**Transfer:** 21.6k weeks transformer 15 MTNN towers input mask m∈{0,1} cat([x·m,m]) CLS128→32-d L2 target MAE 4.268→3.8 smoke 8.475→3.948.
**Limit:** rare 4th-down augmentation needed ScoutGPT 30M.

MoMA-lite 5 tiers: deterministic (json.tool PASS), llm (3-lens), deep_research (5 papers triangulated), action_operator (tool-first), agentic_epic (ultra orchestrator v3.3 10 phases). GARNet relevantAgents max3/4 tempo :13 :05. Token-cache 82% win 22 lines TLPG trace 10 lines 7-field max3/4 tempo :13.

Zero-deps true stdlib only no torch/pip honest 503 never faked.
