# L1 Strategist — Optimistic Lens — 14:40 CT

**Board:** 6 active + 3 LOCAL-GPU exempt, 0 stale, 1 free lane claimed — clean tempo.
**Goal mean target:** 9.0+ across 5 picks (9.2, 9.1, 9.1, 9.0, 9.0)
**Confidence:** 0.85 — all five are lift-capable, zero-deps true.

## 3 Best-Case Opportunities (max lift)

1. **hoops-001-mmoe-scaling 9.2 → 0.55 top1 is the headline win** — muMoE 171 lanes factor rank8 160→32×17 is pure stdlib math, no torch. If we ship it, hoops backboard lights up, and unified-001-moe gets free reuse (same MoE pattern). This alone pulls gate mean +0.15 and makes daily triple [11205,19448,14209] feel instant — open→drag-map→Jordan→copy-link same stars.

2. **pitch-001-ball-cls 9.1 + gridiron-001-axial 9.0 stack = parity story** — pitch ball CLS with 0.5 ADE loss fixes our biggest realism gap (ball chases player). Gridiron axial 13-action live 75k preds turns 646-pt map into a playable lab. Together they give dumbmodel.com 4 dailies at hoops-level, plus 5th chimera 20719×64-d still 7/7/0 59 hashes. DAU3/WAU3 lift from playable novelty.

3. **dottie-001-rl-cot-compress 9.1 → factory flywheel** — 20-40% CoT shrink one-domain-to-all = 31% cache win on 9-token FGO hybrid. That's not just a model save, it's a cost save for every L2/L3 lane (tokens_est drops across board). Scout-cli 770B v0.8.0 hallways 57 members already doctor 7/7 PASS — this makes it faster.

## 1 Risk to Mitigate (optimistic edge)

**MoE routing overhead vs active params** — unified-001 G2 0.685→0.64 target is great, but if muMoE adds routing cost without real sparsity, we regress void #080A0F PWA v67 offline perf (13k budget). Keep factor rank=8 strict, measure G2 on CPU-only path.

## 1 Concrete Action for L3 Builder/Synthesist

Ship **hoops-001-mmoe first in this lane** — single file stdlib only:

- Implement factorized muMoE: `E = U(160×8) @ V(8×32) × 17 experts`, gating top-k=2, no pip
- Eval: top1 0.438→0.55 on 20719 rows, latency <15ms, G2 tracked
- Wire reuse to unified-001 and everydayTip badge (humanized, no raw machinery)
- Verifier: gate ≥8.0, 7/7/0 provenance, PWA offline still 13k

If hoops lands, cascade to unified-001 same PR — fastest mean lift 9.0→9.2.

*LCG 20260813→189831298 idx3820 triple[11205,19448,14209] same-link-same-stars — preserve ?daily=20260813&n=1/3/5*
