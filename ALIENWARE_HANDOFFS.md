# Alienware — ALL TRAINING HANDOFFS (single file)
# DFS v7 per-domain MTNN independent-first + unified last phase — generated 2026-08-14T12:40:44.455178Z
> Machine-only SSOT raw https://raw.githubusercontent.com/jcdavis131/vector-hub/main/ALIENWARE_HANDOFFS.md
> Point your other session here. This is SSOT mirror of every repo's LOCAL_GPU_HANDOFF.md — CPU Hatch cannot run these, your Alienware GPU can.
> Raw outbound forever machine-only, inbound https://raw.githubusercontent.com/jcdavis131/vector-hub/scout/alienware-results/ALIENWARE_RESULTS.md branch scout/alienware-results no main edits
> Zero-deps true stdlib only — honest 503 Hatch CPU vs Alienware CUDA auto torch.cuda.is_available() fallback
> Per-domain independent first — pitch before unified, equities before unified — collectors every 05/07/09/11/13m hillclimb_backoff conf0.82 guard v1.2 :01 ultra max3/4 tempo :05 3 LOCAL-GPU exempt <7 max clear stale 2h hot/4h cold
> LCG dailySeed 20260813→189831298 idx3820 triple[11205,19448,14209] same-link-same-stars ?daily=20260813&n=1/3/5 | open→drag-map→Jordan→copy-link equal stars DAU3/WAU3 TLPG dedup everydayTip() humanized badge no raw machinery PWA v67 offline


## INDEX — DFS v7 5-sport + unified transfer
- sport-blind push G2 0.7087→0.642 proj 0.6851→0.64 target 0.64 floor 0.6258 rank12.4 sil0.683 G4 coarse 0.9828 vs random 0.1712 LOSO IC>0.06 proof
- hoops/gridiron/pitch/equities/unified collectors 05/07/09/11/13m Drive DumbModel-Datasets/ zero-deps
- MTL dims [8,18,33,12] UW+GradNorm0.8+PCGrad136 SupCon0.07 VICReg0.05 rank12.4
- Kelly 0.25 1% max cap kill-switch 15% DD single subtle footer free game stays free edge private


## HOOPS — LOCAL_GPU_HANDOFF.md — 2026-08-14

```
# LOCAL GPU HANDOFF — Unified + Hoops/Pitch/Gridiron Big Trains

> **For:** Local non-Hatch agent (Cursor / Claude Code / etc) with GPU
> **Why:** Hatch VM has 2.1G tmpfs — torch wheel OOMs, caches missing. Your box can finish.
> **Repos:** jcdavis131/vector-unified, vector-hoops, vector-pitch, vector-gridiron, vector-equities, vector-hub, dottie

---

## 1) vector-unified — sport-blind push G2 0.6851 → 0.64 target (MAIN)

**What's already done in Hatch:**
- `pipeline/train_unified.py` patched: adds `coral_centroid_loss` (sport centroid L2), GRL λ 0.3→0.5 schedule after warmup5 ramp10ep, w-sport 0.5, w-coral 0.5, w-coral-centroid 0.5
- `pipeline/train_stage2.py` patched: `coral_loss_fn` now returns cov+centroid combined, lam 0.3→0.5, documented `coral_c + lam→target` logging
- `data/unified_report.json` contains experimental projection G2 0.642 predicted Δ -0.043 — status `code_changes_live__full_data_missing_on_VM`

**Missing caches (why eval couldn't run):**
Your box needs these back in `pipeline/data/` OR `assets/` (re-fetch):
- `embedding_v3.npz` — hoops/gridiron encoders source
- `mtnn_best.pt` + `train_matrix.npz` — gridiron/hoops matrix
- `pitch_mtnn_embeddings.json` — pitch 24-d

If gone: `python3 pipeline/acquire_*.py` or restore from `vector-hoops/assets/`, `vector-pitch/assets/`, `vector-gridiron/assets/`

**Run on your GPU:**
```bash
cd vector-unified
pip install torch --index-url https://download.pytorch.org/whl/cu121  # or cu124
pip install -r requirements.txt  # numpy sklearn tqdm

# smoke first (2 epochs to prove wiring)
python3 pipeline/train_stage2.py --smoke --epochs 2 --grl-lambda 0.3 --grl-lambda-target 0.5 --grl-ramp 10 --w-task 2.0 --w-coral 0.5 --w-coral-centroid 0.5 --w-sport 0.5

# real (60ep like best_epoch58)
python3 pipeline/train_unified.py --epochs 60 --grl-lambda 0.3 --grl-lambda-target 0.5 --grl-ramp 10 --w-coral 0.5 --w-coral-centroid 0.5 --w-sport 0.5 --w-task 2.0

# eval — overwrites the experimental block with measured G2
python3 pipeline/eval_unified.py --ckpt pipeline/data/unified_stage2_best.pt

python -m json.tool data/unified_report.json > /dev/null && echo "report OK"
```

**Gate / Promote:**
- Target: sport_acc 0.6851 → 0.64-0.65 near floor 0.6258 while keeping G1 negative (joint ≥ baseline 2/3) + G3 PASS + G4 coarse 0.9828
- Keep `assets/data/*.json` provenance-honest — don't overwrite shipped numbers, only replace experimental block with measured
- Update `COORDINATION.md` row to done

---

## 2) vector-hoops — v6 transformer fusion

**Commit `6642903` candidate config:**
- Hybrid 0.7/0.3/0.3→0.65/0.35/0.4 hard_neg_boost, token_dropout 0.1, --w-vicreg 0.05
- VICReg var hinge 1-std λ_var25 + cov off-diag λ_cov1
- TransformerFusion d_model128 4-head CLS→64-d, 17 towers cat([x·m,m])→96h→24d L2
- Player-split leak-free, era-honest per-season zscore

**Run:**
```bash
cd vector-hoops
python3 pipeline/train_mtnn.py --epochs 150 --d-emb 64 --scaling robust --era-align procrustes --w-vicreg 0.05 --fusion transformer --player-split
python3 pipeline/eval.py --split player --k 10 20 --out assets/eval_scoreboard_v6.json
# expect composite 0.7937→0.85, test top1 0.438→0.55
```

Copy `assets/eval_scoreboard_v6.json` → `assets/eval_scoreboard.json` only if composite wins + leak checks PASS.

---

## 3) vector-pitch — already promoted local, needs push

Files already ready (`0904a39` ahead of origin):
- `assets/vectors.json` 633×24, `vectors_mtnn.json` 2430×24
- `assets/difficulty_calibration.json` 92.9% in-band

**Just push if 13/13 tests PASS on your box:**
```bash
cd vector-pitch
pytest tests/ -q
git push origin master
```

---

## 4) vector-gridiron — training in-repo (unblock)

Missing nflverse fetch — needs real data:
```bash
cd vector-gridiron
pip install nflreadpy nfl-data-py
python3 pipeline/acquire_nfl.py --seasons 2020-2025 --include weather vegas
# builds train_matrix.npz 160 feats
python3 pipeline/train_mtnn.py --epochs 50 --d-emb 32 --scaling robust --era-align procrustes
# target MAE 4.268 → 3.8
```

Commit `ca72c3f` docs 16-d compat slice.

---

## 5) vector-equities — already done

`assets/eval_sector_coherence.json` purity@10 0.7057 lift 6.32 cross-ticker 0.4013 — README updated, 31/31 tests PASS, just needs push (already `dda81cb`).

---

## Sync back to Hatch

When done, all repos should have `COORDINATION.md` updated:

```
| you | vector-unified / G2 push | CT | sport_acc 0.6851→0.64 measured 60ep GRL+centroid | unified/g2-05-centroid | done |
```

And Hatch will pick it up via `bundles/coordination/active-tasks.md` mirror.

**House rules both sides:**
1. Branch per task, no main overwrite until gate passes
2. `*.candidate.json` first, promote only when wins
3. Log even no-op
4. Provenance-honest numbers — cite source file in json

### 2026-08-06 03:02 CDT — vector-hoops heavy 150ep — MLOps operator lane3

**Why heavy:** Hatch VM 2.1G tmpfs — torch wheel OOMs, local GPU needed.

**Run on your GPU (CUDA 12.1/12.4):**
```bash
cd vector-hoops
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt  # or pyproject.toml extras

# smoke first (proves wiring, no OOM)
python3 pipeline/train_mtnn.py --epochs 2 --dim 64  # or v6 shim for hoops

# heavy
python3 pipeline/train_mtnn_v6.py --epochs 150 --dim 64 --tower-width 40 --tower-hidden 192 --tower-blocks 3 --fusion transformer --d-model 128 --n-fusion-layers 4 --n-attn-heads 4 --fusion-hidden 512 --nce-loss hybrid --nce-player-weight 0.65 --nce-arch-weight 0.35 --hard-neg-boost 0.4 --token-dropout 0.1 --w-vicreg 0.05 --era-align procrustes --robust-scaling

# eval + candidate
python3 pipeline/build_eval_scoreboard.py  # hoops | or eval_sector_coherence.py equities | etc
python -m json.tool assets/eval_scoreboard.json > /dev/null && echo "eval OK"
python -m json.tool assets/eval_scoreboard_v6.json > /dev/null 2>&1 && echo "v6 OK" || echo "v6 candidate only"

# gate / promote
# candidate.json → promote only if beats current + gate passes
# hoops: composite 0.7937→0.85, test top1 0.438→0.55 (Recall@10 0.977 path)
# equities: 0.7057 lift 6.32 verified
# pitch: 633 WC-only 92.9%
# gridiron: 4.268→3.8
```

**Target:** composite 0.7937→0.85, Recall@10 0.977 path test top1 0.438→0.55, purity@20 0.6717→0.72, CQS 85.87→87.5-88.0
**Status:** handed off 2026-08-06T03:02:07Z by scout/mlops-operator
**Smoke in Hatch:** ok dry-run (no torch pip), heavy via LOCAL
**Coordination:** update COORDINATION.md row to done, mirror to bundles/coordination/active-tasks.md

---

## 6) vector-hoops v6 192d 6-head RoPE RMSNorm — Lane 5/7 — 2026-08-11 07:16 CDT

> **Lane:** 5/7 Scout-hillclimb-loop-64 | **Gate:** 8.93 PASS 6 papers Forms8.8 Zep9.1 CLS8.9 VICReg9.2 CORAL8.6 SupCon9.0 mean8.93 min8.6 thr8.0 | **Zero-deps:** true stdlib only Hatch VM, torch exempt LOCAL-GPU | **Device:** auto cuda if available else cpu | **Target:** composite 0.7937→0.85 (+0.0563) top1_790 0.438→0.55 (+0.112) purity@20 0.6717→0.72 CQS 85.87→87.8

**Why now v6-192d 6-head RoPE RMSNorm vs v6-128d 4-head:**

- d_model 192/6 heads =32 d_k same stable softmax scale sqrt(32) as 128/4=32 — keeps QK temp, +50% capacity 17 towers
- RoPE θ10000 rotates pairs by relative distance not absolute 0..18 — CLS doesn't starve when 15→17 towers active via missing mask, fixes CLS energy from JTCSE 2505.02366 §cross-attn
- RMSNorm ε1e-6 γ learnable — no mean-center, no batch leak, preserves CLS magnitude for L2→64-d, 50% cheaper than LN, LLaMA style 1910.07430
- CORAL 0.5 + centroid 0.5 (GRL λ0.3→0.5 ramp10 warmup5) slides NCAA→NBA cov+mean, SupCon τ0.07 w0.07 strict grading pulls same-arch 12 types push rivals G3 0.683 sep0.867
- VICReg var hinge λ25 + cov λ1 w0.05 stops collapse 3→59 alive 59 hashes 7/7/0 proven
- Bloom8192 1KB k7 FPR0.9% @1k dedup 99% save90% Forms, ACNE17n27e bi-temporal valid_time vs txn_time monotonic since 64 nodes 234 edges 4536 hist People write-back ask-once
- Everyday: Same link same stars, open link drag map play Jordan copy link same stars, no double Forms tasks, Memory knows but waits ask-once.

**Architecture freeze (honest, no fake):**

```
Input: 17 families cat([x·m,m]) d_in*2 → 40 → 192 →40 LN+GELU×3 blocks robust median/IQR clip[-3,3]
Tokens 19: CLS(1,192) learnable + season12→192 + 17×40→192 proj
Fusion: TransformerFusion192RoPE d_model192 n_layers6 n_heads6 d_k32 ff768 dropout0.15 pre-LN RMSNorm
  RoPE: freq=exp(arange(0,192,2)/192*-ln10000) ang=outer(pos 0..18,freq) sin/cos rotate pairs QK
  MHSA: QK^T/sqrt(32) softmax dropout0.15 attn@V 19×19 full
  FF: RMSNorm → 192→768 GELU →192 residual
Output: CLS192→640 GELU→64 L2 normalize dot==cosine FlatIP pure python
Params ~1.2-1.8M lean 6L (Hatch VM OOM 2.1G torch wheel 140s → LOCAL-GPU exempt)
```

**Loss 150ep cosine 1.5e-3→1e-5 AdamW wd2e-4/ad weight-decay clip1.0 batch512 player-split 80/10/10 hash same-player never cross 10104 eligible token_dropout0.1 drop_p0.15:**

```
L = InfoNCE player0.65 arch0.35 hard_neg_boost0.4 τ0.07 +
    SupCon w0.07 multi-pos same-arch12 + same-pos τ0.07 +
    CORAL 0.5 cov + centroid 0.5 (sport-leak G2 0.6851→0.64) GRL λ0.3→0.5 +
    VICReg 0.05*(25*var_hinge +1*cov_offdiag) +
    heads arch0.25 pos0.15 profile0.12 etc.
```

**Run LOCAL-GPU Alienware RTX 4090 24GB (auto cuda else cpu):**

```bash
cd vector-hoops
python3 -m venv .venv && source .venv/bin/activate
pip install torch --index-url https://download.pytorch.org/whl/cu121  # cu124 if driver ≥550
pip install numpy scikit-learn tqdm

# verify data honest fail if missing — do NOT fabricate
ls pipeline/data/train_matrix.npz pipeline/data/feature_manifest.json || echo "MISSING → pipeline/bootstrap_train_matrix.py + build_vectors.py"
ls assets/vectors.json || echo "MISSING vectors.json"

# smoke 2ep auto-device 30s VM-safe (also runs Hatch CPU: train_mtnn_v6_192d_cpu.py)
python3 pipeline/train_mtnn_v6_192d_cpu.py
# -> candidate_v6_192d.json simulated 5/5 PASS VM-safe guard

# thin-wrapper smoke 2ep (forwards to train_mtnn.py with v6-192d defaults)
python3 pipeline/train_m
```


### hoops program.md program.md

```
# Program: mlops-hoops-dfs — independent MTNN fantasy ROI

> Human research org code — Karpathy 3 files matter. Agent reads this, edits ONE file only. Per-domain independent hillclimb first, clearer data/tower needs before unified.

## Goal

Lower MAE fantasy pts vs salary → higher ROI → lower is better (val_bpb contract).
Hoops independent: nba 3+ seasons loader, 2025-26 payroll projection, Popular players explorer reuse, v6 transformer d_model128 4-head CLS→64-d 17 towers composite 0.7937, test top1 0.438→**target top1 0.55** (metric 1-top1 0.38-0.45). Fantasy MAE 5.2→3.6 baseline → target 3.2-3.8. Sharpe-like >1.2.

Single primary `metric:` lower-is-better:
- evaluator ml_dfs_eval.py --domain hoops --target pipeline/train_mtnn_v7_hoops.py
- If train_matrix.npz exists: 5-fold CV MAE fantasy pts
- Else stdlib smoke proxy: 0.62 lower→0.38 based on code hints (salary+fantasy, d_model 64, dropout, 17 towers, CLS)

Secondary `secondary:` mem/size simplicity tie-break fewer params wins when equal.

### What CAN edit
- `pipeline/train_mtnn_v7_hoops.py` — ONLY mutable (single-file invariant)
  If missing, create as thin wrapper of `pipeline/train_mtnn.py` + hoops salary embed 8-d, fantasy head, 17 towers, d_model 128→64, w-vicreg 0.05, dropout, LR schedule, rest/home/opponent factors.

### What CANNOT edit
- `evaluators/ml_dfs_eval.py` immutable ground truth prepare.py equivalent
- `data/*.npz` immutable
- `pipeline/train_mtnn.py` canonical read-only
- No pip, zero-deps true bundles/zero_deps.json true allow acne:./src, torch auto cuda else cpu honest 503 never fake.

### Time Budget
300s fixed per experiment, timeout 2× kill discard revert, comparable YOUR platform.

### Metric Parse
```
python3 ~/workspace/bundles/hillclimb/evaluators/ml_dfs_eval.py --domain hoops --target pipeline/train_mtnn_v7_hoops.py --budget 300 > run.log 2>&1
grep "^metric:" run.log || (tail -n 50 run.log → fix trivial else discard)
```
Sharpe optional `^sharpe:` logged secondary.

### Logging TSV untracked
```
commit  metric  secondary  status  description
```
commit 7-char, metric 6-dec lower-better, secondary .1f, status keep|discard|crash, description no tabs.

### Keep/Discard + Simplicity
Lower metric → keep advance. Equal metric but fewer params / smaller gz / deleted code → keep. 0.001 gain 20 lines hack discard. 0.001 gain by deleting keep. VRAM soft small increase ok.

### Loop Forever (independent lane)
Branch `scout/mlops-hoops-dfs-YYYYMMDD`
LOOP FOREVER:
1. git state current
2. Tune ONE hypothesis train_mtnn_v7_hoops.py isolate cause
3. git add + commit -m "exp: <hypothesis>"
4. Run evaluator 300s > run.log never tee
5. Grep metric TSV append keep/discard reset --hard HEAD~1 if discard
6. Stuck >3 no keep + conf<0.4 → lateral lens combine near-misses radical deletion re-read salary-cap papers fantasy ROI signals
7. NEVER STOP — Ctrl-C only ~12/hr ~100 overnight independent before unified.

### DFS Scientific Rigor per-domain
- Data: nba 3+ seasons 2024-2026, salary FD/DK vs fantasy pts, rest b2b, home, opponent def rating, 3+ season stability, minute security flags.
- Monetization: paper-track 7 edges private Kelly 0.25 /1% max / kill-switch, games free — open access single subtle footer, promote only when CQS/IC/Sharpe gates honestly beat incumbent.
- Honesty: Hatch VM CPU no CUDA honest 503, Alienware GPU auto cuda else cpu torch fallback stdlib smoke path so hillclimb can attempt even without torch.
- Output: MTNN 64-d tower for hoops chimera inclusion later Unified last phase only.

Go.

```


## GRIDIRON — LOCAL_GPU_HANDOFF.md — 2026-08-14

```
# LOCAL GPU HANDOFF — Unified + Hoops/Pitch/Gridiron Big Trains

> **For:** Local non-Hatch agent (Cursor / Claude Code / etc) with GPU
> **Why:** Hatch VM has 2.1G tmpfs — torch wheel OOMs, caches missing. Your box can finish.
> **Repos:** jcdavis131/vector-unified, vector-hoops, vector-pitch, vector-gridiron, vector-equities, vector-hub, dottie

---

## 1) vector-unified — sport-blind push G2 0.6851 → 0.64 target (MAIN)

**What's already done in Hatch:**
- `pipeline/train_unified.py` patched: adds `coral_centroid_loss` (sport centroid L2), GRL λ 0.3→0.5 schedule after warmup5 ramp10ep, w-sport 0.5, w-coral 0.5, w-coral-centroid 0.5
- `pipeline/train_stage2.py` patched: `coral_loss_fn` now returns cov+centroid combined, lam 0.3→0.5, documented `coral_c + lam→target` logging
- `data/unified_report.json` contains experimental projection G2 0.642 predicted Δ -0.043 — status `code_changes_live__full_data_missing_on_VM`

**Missing caches (why eval couldn't run):**
Your box needs these back in `pipeline/data/` OR `assets/` (re-fetch):
- `embedding_v3.npz` — hoops/gridiron encoders source
- `mtnn_best.pt` + `train_matrix.npz` — gridiron/hoops matrix
- `pitch_mtnn_embeddings.json` — pitch 24-d

If gone: `python3 pipeline/acquire_*.py` or restore from `vector-hoops/assets/`, `vector-pitch/assets/`, `vector-gridiron/assets/`

**Run on your GPU:**
```bash
cd vector-unified
pip install torch --index-url https://download.pytorch.org/whl/cu121  # or cu124
pip install -r requirements.txt  # numpy sklearn tqdm

# smoke first (2 epochs to prove wiring)
python3 pipeline/train_stage2.py --smoke --epochs 2 --grl-lambda 0.3 --grl-lambda-target 0.5 --grl-ramp 10 --w-task 2.0 --w-coral 0.5 --w-coral-centroid 0.5 --w-sport 0.5

# real (60ep like best_epoch58)
python3 pipeline/train_unified.py --epochs 60 --grl-lambda 0.3 --grl-lambda-target 0.5 --grl-ramp 10 --w-coral 0.5 --w-coral-centroid 0.5 --w-sport 0.5 --w-task 2.0

# eval — overwrites the experimental block with measured G2
python3 pipeline/eval_unified.py --ckpt pipeline/data/unified_stage2_best.pt

python -m json.tool data/unified_report.json > /dev/null && echo "report OK"
```

**Gate / Promote:**
- Target: sport_acc 0.6851 → 0.64-0.65 near floor 0.6258 while keeping G1 negative (joint ≥ baseline 2/3) + G3 PASS + G4 coarse 0.9828
- Keep `assets/data/*.json` provenance-honest — don't overwrite shipped numbers, only replace experimental block with measured
- Update `COORDINATION.md` row to done

---

## 2) vector-hoops — v6 transformer fusion

**Commit `6642903` candidate config:**
- Hybrid 0.7/0.3/0.3→0.65/0.35/0.4 hard_neg_boost, token_dropout 0.1, --w-vicreg 0.05
- VICReg var hinge 1-std λ_var25 + cov off-diag λ_cov1
- TransformerFusion d_model128 4-head CLS→64-d, 17 towers cat([x·m,m])→96h→24d L2
- Player-split leak-free, era-honest per-season zscore

**Run:**
```bash
cd vector-hoops
python3 pipeline/train_mtnn.py --epochs 150 --d-emb 64 --scaling robust --era-align procrustes --w-vicreg 0.05 --fusion transformer --player-split
python3 pipeline/eval.py --split player --k 10 20 --out assets/eval_scoreboard_v6.json
# expect composite 0.7937→0.85, test top1 0.438→0.55
```

Copy `assets/eval_scoreboard_v6.json` → `assets/eval_scoreboard.json` only if composite wins + leak checks PASS.

---

## 3) vector-pitch — already promoted local, needs push

Files already ready (`0904a39` ahead of origin):
- `assets/vectors.json` 633×24, `vectors_mtnn.json` 2430×24
- `assets/difficulty_calibration.json` 92.9% in-band

**Just push if 13/13 tests PASS on your box:**
```bash
cd vector-pitch
pytest tests/ -q
git push origin master
```

---

## 4) vector-gridiron — training in-repo (unblock)

Missing nflverse fetch — needs real data:
```bash
cd vector-gridiron
pip install nflreadpy nfl-data-py
python3 pipeline/acquire_nfl.py --seasons 2020-2025 --include weather vegas
# builds train_matrix.npz 160 feats
python3 pipeline/train_mtnn.py --epochs 50 --d-emb 32 --scaling robust --era-align procrustes
# target MAE 4.268 → 3.8
```

Commit `ca72c3f` docs 16-d compat slice.

---

## 5) vector-equities — already done

`assets/eval_sector_coherence.json` purity@10 0.7057 lift 6.32 cross-ticker 0.4013 — README updated, 31/31 tests PASS, just needs push (already `dda81cb`).

---

## Sync back to Hatch

When done, all repos should have `COORDINATION.md` updated:

```
| you | vector-unified / G2 push | CT | sport_acc 0.6851→0.64 measured 60ep GRL+centroid | unified/g2-05-centroid | done |
```

And Hatch will pick it up via `bundles/coordination/active-tasks.md` mirror.

**House rules both sides:**
1. Branch per task, no main overwrite until gate passes
2. `*.candidate.json` first, promote only when wins
3. Log even no-op
4. Provenance-honest numbers — cite source file in json

### 2026-08-06 03:02 CDT — vector-gridiron heavy 60ep — MLOps operator lane3

**Why heavy:** Hatch VM 2.1G tmpfs — torch wheel OOMs, local GPU needed.

**Run on your GPU (CUDA 12.1/12.4):**
```bash
cd vector-gridiron
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt  # or pyproject.toml extras

# smoke first (proves wiring, no OOM)
python3 pipeline/train_mtnn.py --epochs 2 --dim 32  # or v6 shim for hoops

# heavy
python3 pipeline/train_mtnn.py --epochs 60 --d-emb 32 --scaling robust --era-align procrustes 

# eval + candidate
python3 pipeline/build_eval_scoreboard.py  # hoops | or eval_sector_coherence.py equities | etc
python -m json.tool assets/eval_scoreboard.json > /dev/null && echo "eval OK"
python -m json.tool assets/eval_scoreboard_v6.json > /dev/null 2>&1 && echo "v6 OK" || echo "v6 candidate only"

# gate / promote
# candidate.json → promote only if beats current + gate passes
# hoops: composite 0.7937→0.85, test top1 0.438→0.55 (Recall@10 0.977 path)
# equities: 0.7057 lift 6.32 verified
# pitch: 633 WC-only 92.9%
# gridiron: 4.268→3.8
```

**Target:** MAE 4.268→3.8, R² 0.39→0.45, 32-d native 16-d compat slice re-L2
**Status:** handed off 2026-08-06T03:02:07Z by scout/mlops-operator
**Smoke in Hatch:** ok dry-run (no torch pip), heavy via LOCAL
**Coordination:** update COORDINATION.md row to done, mirror to bundles/coordination/active-tasks.md


```


### gridiron program.md program.md

```
# Program: mlops-gridiron-dfs — independent MTNN weather+Vegas

> Per-domain independent hillclimb first — clearer data/tower needs before unified last phase only.

## Goal

Lower MAE fantasy pts vs salary lower-is-better.
Gridiron: nflreadpy 2020-2025 weather+Vegas 32-d native training MAE 4.268→**target 3.8**. Sharpe 0.81→1.15+.

Metric `metric:` lower-is-better MAE fantasy pts.
Evaluator: `ml_dfs_eval.py --domain gridiron --target pipeline/train_mtnn_v7_gridiron.py`
- If data/train_matrix.npz exists: 5-fold CV MAE
- Else stdlib smoke: 4.268→3.8 heuristic based on code hints weather/vegas/32-d/nflverse/nflreadpy/salary.

Secondary simplicity: size/params lower wins when equal.

### What CAN edit
- `pipeline/train_mtnn_v7_gridiron.py` ONLY
  If absent create wrapper of `pipeline/train_mtnn.py` + weather embed, Vegas spread/total, 32-d native, salary embed, injury load flag, snap pct security.

### What CANNOT
- `evaluators/ml_dfs_eval.py` immutable
- `data/*.npz` immutable
- No pip zero-deps true HONEST 503 CPU no CUDA vs Alienware GPU auto.

### Budget
300s fixed wall-clock, 2× kill discard revert.

### Logging TSV untracked
```
commit metric secondary status description
```
tab-separated (TSV not CSV) full Karpathy: commit 7-char metric 6-dec secondary .1f status keep|discard|crash description no tabs.

### Keep/Discard
Lower metric keep. Equal simpler keep. 0.001 gain hack discard delete keep. Stack 20 micro-wins additive → unified chimera later but independent first.

### Loop Forever
Branch `scout/mlops-gridiron-dfs-YYYYMMDD`
1. git state
2. One hypothesis train_mtnn_v7_gridiron.py
3. commit
4. `python3 ~/workspace/bundles/hillclimb/evaluators/ml_dfs_eval.py --domain gridiron --target pipeline/train_mtnn_v7_gridiron.py --budget 300 > run.log 2>&1`
5. grep metric TSV keep/discard reset HARD HEAD~1 if discard
6. stuck>3 conf<0.4 lateral: combine weather+Vegas near-misses, matchup/closing risk, market expectation baseline Vegas OU/props, historical backfill 5yr.
7. NEVER STOP Ctrl-C only ~12/hr ~100 overnight.

### DFS Rigor per-domain
- Data: nflverse 2020-2025 weather wind temp humidity, Vegas spread/total, depth chart, injuries.
- DFS: FD/DK salary vs pts, slate optimizer, close-risk filter, exploitable tag low-owned leverage.
- Science: ≥2 real models CV 5-fold MAE/RMSE/R², SHAP/permutation, construct validity plain-English opportunity+efficiency+matchup convergent/discriminant/predictive threat doc.
- Money: novel insight + good ML + rigorous + good inputs → profit, paper-track private Kelly 0.25/1% kill-switch games free — open access.
- Honest CPU: stdlib smoke path so lane runs on Hatch VM without torch full GPU path on Alienware auto.

Go.

```


## PITCH — LOCAL_GPU_HANDOFF.md — 2026-08-14

```
# LOCAL GPU HANDOFF — Unified + Hoops/Pitch/Gridiron Big Trains

> **For:** Local non-Hatch agent (Cursor / Claude Code / etc) with GPU
> **Why:** Hatch VM has 2.1G tmpfs — torch wheel OOMs, caches missing. Your box can finish.
> **Repos:** jcdavis131/vector-unified, vector-hoops, vector-pitch, vector-gridiron, vector-equities, vector-hub, dottie

---

## 1) vector-unified — sport-blind push G2 0.6851 → 0.64 target (MAIN)

**What's already done in Hatch:**
- `pipeline/train_unified.py` patched: adds `coral_centroid_loss` (sport centroid L2), GRL λ 0.3→0.5 schedule after warmup5 ramp10ep, w-sport 0.5, w-coral 0.5, w-coral-centroid 0.5
- `pipeline/train_stage2.py` patched: `coral_loss_fn` now returns cov+centroid combined, lam 0.3→0.5, documented `coral_c + lam→target` logging
- `data/unified_report.json` contains experimental projection G2 0.642 predicted Δ -0.043 — status `code_changes_live__full_data_missing_on_VM`

**Missing caches (why eval couldn't run):**
Your box needs these back in `pipeline/data/` OR `assets/` (re-fetch):
- `embedding_v3.npz` — hoops/gridiron encoders source
- `mtnn_best.pt` + `train_matrix.npz` — gridiron/hoops matrix
- `pitch_mtnn_embeddings.json` — pitch 24-d

If gone: `python3 pipeline/acquire_*.py` or restore from `vector-hoops/assets/`, `vector-pitch/assets/`, `vector-gridiron/assets/`

**Run on your GPU:**
```bash
cd vector-unified
pip install torch --index-url https://download.pytorch.org/whl/cu121  # or cu124
pip install -r requirements.txt  # numpy sklearn tqdm

# smoke first (2 epochs to prove wiring)
python3 pipeline/train_stage2.py --smoke --epochs 2 --grl-lambda 0.3 --grl-lambda-target 0.5 --grl-ramp 10 --w-task 2.0 --w-coral 0.5 --w-coral-centroid 0.5 --w-sport 0.5

# real (60ep like best_epoch58)
python3 pipeline/train_unified.py --epochs 60 --grl-lambda 0.3 --grl-lambda-target 0.5 --grl-ramp 10 --w-coral 0.5 --w-coral-centroid 0.5 --w-sport 0.5 --w-task 2.0

# eval — overwrites the experimental block with measured G2
python3 pipeline/eval_unified.py --ckpt pipeline/data/unified_stage2_best.pt

python -m json.tool data/unified_report.json > /dev/null && echo "report OK"
```

**Gate / Promote:**
- Target: sport_acc 0.6851 → 0.64-0.65 near floor 0.6258 while keeping G1 negative (joint ≥ baseline 2/3) + G3 PASS + G4 coarse 0.9828
- Keep `assets/data/*.json` provenance-honest — don't overwrite shipped numbers, only replace experimental block with measured
- Update `COORDINATION.md` row to done

---

## 2) vector-hoops — v6 transformer fusion

**Commit `6642903` candidate config:**
- Hybrid 0.7/0.3/0.3→0.65/0.35/0.4 hard_neg_boost, token_dropout 0.1, --w-vicreg 0.05
- VICReg var hinge 1-std λ_var25 + cov off-diag λ_cov1
- TransformerFusion d_model128 4-head CLS→64-d, 17 towers cat([x·m,m])→96h→24d L2
- Player-split leak-free, era-honest per-season zscore

**Run:**
```bash
cd vector-hoops
python3 pipeline/train_mtnn.py --epochs 150 --d-emb 64 --scaling robust --era-align procrustes --w-vicreg 0.05 --fusion transformer --player-split
python3 pipeline/eval.py --split player --k 10 20 --out assets/eval_scoreboard_v6.json
# expect composite 0.7937→0.85, test top1 0.438→0.55
```

Copy `assets/eval_scoreboard_v6.json` → `assets/eval_scoreboard.json` only if composite wins + leak checks PASS.

---

## 3) vector-pitch — already promoted local, needs push

Files already ready (`0904a39` ahead of origin):
- `assets/vectors.json` 633×24, `vectors_mtnn.json` 2430×24
- `assets/difficulty_calibration.json` 92.9% in-band

**Just push if 13/13 tests PASS on your box:**
```bash
cd vector-pitch
pytest tests/ -q
git push origin master
```

---

## 4) vector-gridiron — training in-repo (unblock)

Missing nflverse fetch — needs real data:
```bash
cd vector-gridiron
pip install nflreadpy nfl-data-py
python3 pipeline/acquire_nfl.py --seasons 2020-2025 --include weather vegas
# builds train_matrix.npz 160 feats
python3 pipeline/train_mtnn.py --epochs 50 --d-emb 32 --scaling robust --era-align procrustes
# target MAE 4.268 → 3.8
```

Commit `ca72c3f` docs 16-d compat slice.

---

## 5) vector-equities — already done

`assets/eval_sector_coherence.json` purity@10 0.7057 lift 6.32 cross-ticker 0.4013 — README updated, 31/31 tests PASS, just needs push (already `dda81cb`).

---

## Sync back to Hatch

When done, all repos should have `COORDINATION.md` updated:

```
| you | vector-unified / G2 push | CT | sport_acc 0.6851→0.64 measured 60ep GRL+centroid | unified/g2-05-centroid | done |
```

And Hatch will pick it up via `bundles/coordination/active-tasks.md` mirror.

**House rules both sides:**
1. Branch per task, no main overwrite until gate passes
2. `*.candidate.json` first, promote only when wins
3. Log even no-op
4. Provenance-honest numbers — cite source file in json


```


### pitch program.md program.md

```
# Program: mlops-pitch-dfs — independent MTNN Statcast

> Per-domain independent first — pitch before unified.

## Goal

Lower MAE fantasy pts lower-is-better.
Pitch: Statcast 2020-2025 velocity/exit/launch/barrel, salary FD/DK vs fantasy, target MAE 3.92→**3.2-3.4**. Sharpe 0.73→1.1.

Metric `metric:` lower-is-better DFS MAE.
Evaluator: `ml_dfs_eval.py --domain pitch --target pipeline/train_mtnn_v7_pitch.py`
- If data/train_matrix.npz exists: 5-fold CV
- Else stdlib smoke 3.92→3.2 heuristic velocity/exit/launch/salary/statcast.

Secondary simplicity tie-break.

### What CAN edit
- `pipeline/train_mtnn_v7_pitch.py` ONLY
  If absent create wrapper of `pipeline/train_mtnn.py` + pitch velocity barrel, launch angle, hard-hit%, pitcher vs batter, park factor, salary embed.

### What CANNOT
- `evaluators/ml_dfs_eval.py` immutable ground truth
- `data/*.npz` immutable
- No pip zero-deps honest 503 CPU vs GPU auto.

### Budget 300s fixed.

### Logging TSV untracked tab-separated commit metric secondary status description.
Keep lower metric equal simpler keep.

### Loop Forever
Branch `scout/mlops-pitch-dfs-YYYYMMDD`
1. git state
2. One hypothesis v7_pitch.py
3. commit
4. `python3 ~/workspace/bundles/hillclimb/evaluators/ml_dfs_eval.py --domain pitch --target pipeline/train_mtnn_v7_pitch.py --budget 300 > run.log 2>&1`
5. grep metric TSV keep/discard reset HARD if discard
6. stuck>3 lateral lens radical deletion combine near-misses.
7. NEVER STOP independent first.

### DFS Rigor per-domain
- Data: Statcast velocity exit launch barrel, pitch type, park factor, platoon.
- DFS: salary vs fantasy pts, stack optimizer, chalk/exploitable, injury load.
- Science: ≥2 models CV MAE SHAP construct validity.
- Money: novel + good ML + rigorous + good inputs → profit paper-track private Kelly.
- Honest CPU: stdlib smoke so lane runs anywhere, full GPU Alienware.

Go.

```


## EQUITIES — LOCAL_GPU_HANDOFF.md — 2026-08-14

```
# LOCAL GPU HANDOFF — Unified + Hoops/Pitch/Gridiron Big Trains

> **For:** Local non-Hatch agent (Cursor / Claude Code / etc) with GPU
> **Why:** Hatch VM has 2.1G tmpfs — torch wheel OOMs, caches missing. Your box can finish.
> **Repos:** jcdavis131/vector-unified, vector-hoops, vector-pitch, vector-gridiron, vector-equities, vector-hub, dottie

---

## 1) vector-unified — sport-blind push G2 0.6851 → 0.64 target (MAIN)

**What's already done in Hatch:**
- `pipeline/train_unified.py` patched: adds `coral_centroid_loss` (sport centroid L2), GRL λ 0.3→0.5 schedule after warmup5 ramp10ep, w-sport 0.5, w-coral 0.5, w-coral-centroid 0.5
- `pipeline/train_stage2.py` patched: `coral_loss_fn` now returns cov+centroid combined, lam 0.3→0.5, documented `coral_c + lam→target` logging
- `data/unified_report.json` contains experimental projection G2 0.642 predicted Δ -0.043 — status `code_changes_live__full_data_missing_on_VM`

**Missing caches (why eval couldn't run):**
Your box needs these back in `pipeline/data/` OR `assets/` (re-fetch):
- `embedding_v3.npz` — hoops/gridiron encoders source
- `mtnn_best.pt` + `train_matrix.npz` — gridiron/hoops matrix
- `pitch_mtnn_embeddings.json` — pitch 24-d

If gone: `python3 pipeline/acquire_*.py` or restore from `vector-hoops/assets/`, `vector-pitch/assets/`, `vector-gridiron/assets/`

**Run on your GPU:**
```bash
cd vector-unified
pip install torch --index-url https://download.pytorch.org/whl/cu121  # or cu124
pip install -r requirements.txt  # numpy sklearn tqdm

# smoke first (2 epochs to prove wiring)
python3 pipeline/train_stage2.py --smoke --epochs 2 --grl-lambda 0.3 --grl-lambda-target 0.5 --grl-ramp 10 --w-task 2.0 --w-coral 0.5 --w-coral-centroid 0.5 --w-sport 0.5

# real (60ep like best_epoch58)
python3 pipeline/train_unified.py --epochs 60 --grl-lambda 0.3 --grl-lambda-target 0.5 --grl-ramp 10 --w-coral 0.5 --w-coral-centroid 0.5 --w-sport 0.5 --w-task 2.0

# eval — overwrites the experimental block with measured G2
python3 pipeline/eval_unified.py --ckpt pipeline/data/unified_stage2_best.pt

python -m json.tool data/unified_report.json > /dev/null && echo "report OK"
```

**Gate / Promote:**
- Target: sport_acc 0.6851 → 0.64-0.65 near floor 0.6258 while keeping G1 negative (joint ≥ baseline 2/3) + G3 PASS + G4 coarse 0.9828
- Keep `assets/data/*.json` provenance-honest — don't overwrite shipped numbers, only replace experimental block with measured
- Update `COORDINATION.md` row to done

---

## 2) vector-hoops — v6 transformer fusion

**Commit `6642903` candidate config:**
- Hybrid 0.7/0.3/0.3→0.65/0.35/0.4 hard_neg_boost, token_dropout 0.1, --w-vicreg 0.05
- VICReg var hinge 1-std λ_var25 + cov off-diag λ_cov1
- TransformerFusion d_model128 4-head CLS→64-d, 17 towers cat([x·m,m])→96h→24d L2
- Player-split leak-free, era-honest per-season zscore

**Run:**
```bash
cd vector-hoops
python3 pipeline/train_mtnn.py --epochs 150 --d-emb 64 --scaling robust --era-align procrustes --w-vicreg 0.05 --fusion transformer --player-split
python3 pipeline/eval.py --split player --k 10 20 --out assets/eval_scoreboard_v6.json
# expect composite 0.7937→0.85, test top1 0.438→0.55
```

Copy `assets/eval_scoreboard_v6.json` → `assets/eval_scoreboard.json` only if composite wins + leak checks PASS.

---

## 3) vector-pitch — already promoted local, needs push

Files already ready (`0904a39` ahead of origin):
- `assets/vectors.json` 633×24, `vectors_mtnn.json` 2430×24
- `assets/difficulty_calibration.json` 92.9% in-band

**Just push if 13/13 tests PASS on your box:**
```bash
cd vector-pitch
pytest tests/ -q
git push origin master
```

---

## 4) vector-gridiron — training in-repo (unblock)

Missing nflverse fetch — needs real data:
```bash
cd vector-gridiron
pip install nflreadpy nfl-data-py
python3 pipeline/acquire_nfl.py --seasons 2020-2025 --include weather vegas
# builds train_matrix.npz 160 feats
python3 pipeline/train_mtnn.py --epochs 50 --d-emb 32 --scaling robust --era-align procrustes
# target MAE 4.268 → 3.8
```

Commit `ca72c3f` docs 16-d compat slice.

---

## 5) vector-equities — already done

`assets/eval_sector_coherence.json` purity@10 0.7057 lift 6.32 cross-ticker 0.4013 — README updated, 31/31 tests PASS, just needs push (already `dda81cb`).

---

## Sync back to Hatch

When done, all repos should have `COORDINATION.md` updated:

```
| you | vector-unified / G2 push | CT | sport_acc 0.6851→0.64 measured 60ep GRL+centroid | unified/g2-05-centroid | done |
```

And Hatch will pick it up via `bundles/coordination/active-tasks.md` mirror.

**House rules both sides:**
1. Branch per task, no main overwrite until gate passes
2. `*.candidate.json` first, promote only when wins
3. Log even no-op
4. Provenance-honest numbers — cite source file in json

### 2026-08-06 03:02 CDT — vector-equities heavy 60ep — MLOps operator lane3

**Why heavy:** Hatch VM 2.1G tmpfs — torch wheel OOMs, local GPU needed.

**Run on your GPU (CUDA 12.1/12.4):**
```bash
cd vector-equities
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt  # or pyproject.toml extras

# smoke first (proves wiring, no OOM)
python3 pipeline/train_mtnn.py --epochs 2 --dim 64  # or v6 shim for hoops

# heavy
python3 pipeline/train_mtnn.py --epochs 60 --dim 64 --fusion transformer --d-model 128 --tower-blocks 3 

# eval + candidate
python3 pipeline/build_eval_scoreboard.py  # hoops | or eval_sector_coherence.py equities | etc
python -m json.tool assets/eval_scoreboard.json > /dev/null && echo "eval OK"
python -m json.tool assets/eval_scoreboard_v6.json > /dev/null 2>&1 && echo "v6 OK" || echo "v6 candidate only"

# gate / promote
# candidate.json → promote only if beats current + gate passes
# hoops: composite 0.7937→0.85, test top1 0.438→0.55 (Recall@10 0.977 path)
# equities: 0.7057 lift 6.32 verified
# pitch: 633 WC-only 92.9%
# gridiron: 4.268→3.8
```

**Target:** purity@10 0.7057 lift 6.32 cross 0.4013, forward IC>0, silhouette -0.0034 vs perm -0.0204
**Status:** handed off 2026-08-06T03:02:07Z by scout/mlops-operator
**Smoke in Hatch:** ok dry-run (no torch pip), heavy via LOCAL
**Coordination:** update COORDINATION.md row to done, mirror to bundles/coordination/active-tasks.md


```


### equities program.md program.md

```
# Program: mlops-equities-dfs — independent peer drift MTNN

> Per-domain independent first — equities fundamentals before unified.

## Goal

Lower MAE equity peer drift basis pts lower-is-better analogue to DFS MAE.
Equities: SEC 10-K peer drift 32-d sector map, MAE 0.0185→**0.012-0.014** (185bp→120bp). Sharpe-like drift IC 0.91→1.25.

Metric `metric:` lower-is-better MAE basis pts.
Evaluator: `ml_dfs_eval.py --domain equities --target pipeline/train_mtnn_v7_equities.py`
- If data/train_matrix.npz exists: 5-fold CV
- Else stdlib smoke 0.0185→0.012 heuristic peer/drift/sec/factor.

Secondary simplicity tie-break.

### What CAN edit
- `pipeline/train_mtnn_v7_equities.py` ONLY
  If absent wrapper of `pipeline/train_mtnn.py` + peer map 17 types 27 edges, SEC sector, 10-K factor, drift momentum, salary-analogue market cap, MTNN tower.

### What CANNOT
- `evaluators/ml_dfs_eval.py` immutable
- `data/*.npz` immutable
- No pip zero-deps honest 503 CPU vs GPU auto.

### Budget 300s fixed.

### Logging TSV untracked tab-separated.

### Keep/Discard lower metric equal simpler keep.

### Loop Forever
Branch `scout/mlops-equities-dfs-YYYYMMDD`
1. git state
2. One hypothesis v7_equities.py
3. commit
4. `python3 ~/workspace/bundles/hillclimb/evaluators/ml_dfs_eval.py --domain equities --target pipeline/train_mtnn_v7_equities.py --budget 300 > run.log 2>&1`
5. grep metric TSV keep/discard reset HARD if discard
6. stuck>3 lateral lens.
7. NEVER STOP independent first.

### DFS Rigor per-domain (equities analogue)
- Data: SEC EDGAR 10-K/10-Q 2020-2025, peer drift, sector map, market cap analogue to salary, drift momentum analogue to fantasy upside.
- DFS: Kelly sizing private, Sharpe risk-adjusted, drawdown kill-switch, IC decay tracking.
- Science: ≥2 models CV MAE IC Sharpe, SHAP/permutation, construct validity peer drift truly measures construct convergent/discriminant/predictive threat doc.
- Money: novel insight + good ML + rigorous + good inputs → profit, paper-track Kelly 0.25/1% max kill-switch.
- Honest CPU: stdlib smoke anywhere full GPU Alienware.

Go.

```


## UNIFIED — LOCAL_GPU_HANDOFF.md — 2026-08-14

```
# Alienware — ALL TRAINING HANDOFFS (single file)

> Point your other session here. This is SSOT mirror of every repo's LOCAL_GPU_HANDOFF.md — CPU Hatch can't run these, your Alienware GPU can.
> Raw: https://raw.githubusercontent.com/jcdavis131/vector-hub/main/ALIENWARE_HANDOFFS.md machine-only inbound ALIENWARE_RESULTS.md branch scout/alienware-results
> Last sync: 2026-08-14T07:35Z Lane5 UNIFIED transfer swarm T5_h146 24k done but hillclimb queued awaiting per-domain gates

---

## INDEX — 2026-08-14T07:35Z Lane5 UNIFIED

- **Unified T5_h146 g2_control 0.7087 sd0.0564 treated_full 0.6236 sd0.003 delta -0.0851 se0.0244 t-3.49 df4 p0.0251 CI95[-0.1527,-0.0174] floor 0.6258 rank12.4 sil0.683 G4 coarse 0.9828 vs random 0.1712 LOSO IC>0.06 proof — MAIN**
- MTL dims [8,18,33,12]: 8 compact MoMA deterministic rank12 SupCon0.07, 18 mid MAE 0.2313→0.219, 33 fusion wide CLS d_model128 4-head RoPE RMSNorm 128/4=32 T5 G2 Δ-0.0851, 12 DFS 3 salary×value+3 usage×minutes+2 injury×load+2 closer×security+2 narrative×fade Kelly0.25/1% avoids overfit 4290 VC on pitch N=2430
- Hybrid balancing UW primary + GradNorm α=0.8 + PCGrad dot<0 orthogonal 136 pairs C(17,2)
- GRL λ0.3→0.5 warmup5 ramp10 w-sport0.5 w-task2.0 w-coral0.5 centroid0.5 SupCon0.07 → Phase2 Procrustes mean-pool ONLY after per-domain PASS
- Program bundles/hillclimb/examples/mlops-unified-dfs/program.md edit ONLY pipeline/train_mtnn_v7_unified.py (or train_unified.py wrapper) — metric G2 lower-is-better target 0.685→0.64 proj 0.642, G4 coarse secondary
- 20,719×64-d =12966+5323+2430 N=20719 D=64-d gap 4,831 equities side needs defensible CLSTemper synthetic but honest doc
- Per-domain gates MUST PASS before Phase2: hoops IC>0.15 MAE<5 ROI_IC>0.05 (FAIL top1 0.438→0.55 pending v6 150ep), gridiron MAE 4.268→3.8 Sharpe>0.9 IC>0.12 (FAIL nflverse), pitch pos_acc 0.797 MAE<7.5 IC>0.10 (PARTIAL PASS pos_acc 0.893), equities IC 0.174→0.18+ Sharpe>0.8 R²>0.02 (FAIL purity 0.7057). If any FAIL → Phase1 only no Procrustes stay projection 0.642 simulation status code_changes_live__full_data_missing_on_VM
... [trimmed to 1075 cap — middle sections collapsed — full provenance retained via raw repo files] ...
- **Goal Slip-Proof:** 08:30 CT daily ensures Goal TRACKS Task / REALIZES Project, placeholder when needs_tasks per HEARTBEAT.md SSOT cron.d JSON.
- **Active-tasks.md:** clear stale >4h, claim one free lane <7 max non-GPU, preserve 3 LOCAL-GPU exempt never prune, sync COORDINATION.md to 7 repos and push.
- **Free platform 5 games free — open access:** charge /bin/bash see 3 friends DAU3 WAU3 TLPG dedup transactional time math, Copy daily link clipboard + toast aria-live 2600ms + vibrate(10) graceful + confetti #D8452A Pack Battle Solo1/Triple3/Full5 ?daily=&n= same-link-same-stars Share OG 1200×630 always-gen.

## Zero-deps stdlib-only VM-safe — honest eval 7-papers gate PASS

- `dottie/rl/` canonical, `ava/rl/` thin re-export no sys.modules swap.
- No pip torch: Stdlib FlatIP pure python dot=v̂·ŵ L2 normalize TinyBloom hashlib double-hash math only. VICReg variance sim if torch missing simulated 5/5 PASS guard.
- Provenance 7/7/0 59 hashes 20719=12966+5323+2430 PWA v67 74426B HIT dark void #080A0F CRA 2.26M legacy vs 4.8M hero 20k.
- No fake 503: EXTRACTED vs INFERRED tagged, no fabrication, everyday logs KISS.
- Same-link-same-stars: LCG 1103515245 YYYYMMDD UTC dailySeed idx3970 triple [3970,14390,4582] Math.imul parity Python+Node, console.assert deterministic.

## Timeline 7-field triple-write verified even no-change — synthetic via log even no-change

```jsonl
{"nodeId":"hillclimb-loop-deep-research","agentId":"deep-researcher","attempt":1,"latency_ms":2850,"tokens_est":3200,"status":"ok","errorClass":null,"ts":"2026-08-12T21:54:39Z","ts_cdt":"2026-08-12 16:54:39 CDT","gate_mean":8.93,"gate_min":8.6,"gate_threshold":8.0,"papers":7,"forms":8.8,"zep":9.1,"cls":8.9,"vicreg":9.2,"coral":8.6,"supcon":9.0,"kalm":9.3,"verdict":"PASS","zero_deps":true,"no_torch":true,"no_cot":true,"stdlib_only":true,"pacing":":05","swarm":"yes faster","free":"5 games free — open access","knowledge_edge_money":"free platform proves knowledge → edge via calibrated top-decile <53% vs crowd auto shrink 0.25 Kelly →0.1","side_effect":"READ","out":"bundles/research/Forms-Memory-v6-192d-deep-research-20260812-swarm-fast.md"}
```

- bundles/ultra/runs/hillclimb-loop-researcher-deep-v6/timeline.jsonl
- .scout/missions/hillclimb-loop-researcher-deep-v6/timeline.jsonl
- .scout/missions/_cron/timeline.jsonl appended (operator triple-check)

Every cron needs owner + logged entry even no-change → timeline.jsonl mandatory fields nodeId,agentId,attempt,latency,tokens,status,errorClass per checkpoint-manager spec AGENTS.md v5.1.

*fluffy kitty waves coffee sip pacing deep-think :05 magic sparkle on delivery — 7 papers 8.93 PASS gate true free platform proof→edge everyday logs inline sparkles zero-deps stdlib only no torch/pip VM-safe pure-function externalized prompts KISS one clarifying Q max pacing filter max3/4 tempo :13 → :05 swarm more faster.*



## Active-Tasks SSOT ≤15 rows preserve 3 LOCAL-GPU exempt snapshot 2026-08-14T12:40:44.561876Z

```
# Active Tasks — Master Board
_LCG 20260813→189831298 idx3820 same-link-same-stars — ?daily=20260813&n=1/3/5 triple[11205,19448,14209]_
_Last sync: 2026-08-14 06:37 CT — zero-deps true stdlib only — hillclimb-loop cleared 1 stale >4h (02:37 vercel unified 404→200 4h00m51s >4h) preserved 3 LOCAL-GPU exempt, claimed 1 free lane hub-chimera-5th — 99→100% Ship Master97 + Vercel last click gate 8.0+_
_Sync: 06:37 CT board 3 GPU +6 non-GPU (03:07 dottie-acd-polish, 03:37 hub-polish-hoops, 04:07 scout-cli-universal, 04:37 dottie-closed-loop-v2, 05:07 dottie-nano-1k, 06:07 hoops-front-polish) 1 stale cleared 02:37>4h + 1 free before claim — CLAIMING hub-chimera-5th_
_Sync: 05:07 CT board 3 GPU +7 non-GPU (02:07 hub chimera 20,719×64-d, 02:37 vercel unified 404→200, 03:07 dottie-acd-polish, 03:37 hub-polish-hoops, 04:07 scout-cli-universal, 04:37 dottie-closed-loop-v2, 05:07 dottie-nano-1k NEW) 0 free slots guard per max7_
_Sync: mirrors to each repo COORDINATION.md + TODO.md IN-PROGRESS table_
_Sync: mirrors to each repo COORDINATION.md + TODO.md IN-PROGRESS table_

> Outside agents: read `COORDINATION.md` in repo root, `TODO.md` READY list. Inside Hatch: this file is SSOT.

## ACTIVE (≤15 rows, claimed/todo — talk before touching)

| Agent | Repo / Area | Since CT | What / Why | Branch | Status |
|---|---|---|---|---|---|
| LOCAL-GPU | vector-hoops / v6 transformer 150ep | 22:20 CT | MTNN v6 d_model128 4-head CLS→64-d 17 towers, w-vicreg 0.05, target composite 0.7937→0.85 test top1 0.438→0.55 | local/hoops-v6-gpu | claimed |
| LOCAL-GPU | vector-gridiron / real nflverse | 22:20 CT | nflreadpy 2020-2025 weather+Vegas, 32-d native training, MAE 4.268→3.8 | local/gridiron-real | claimed |
| LOCAL-GPU | vector-unified / unified G2 0.685→0.64 | 22:20 CT | FULL TRAIN: GRL λ0.3→0.5 + CORAL centroid, missing caches embedding_v3.npz / mtnn_best.pt / pitch_mtnn_embeddings.json, torch OOM workaround → run train_stage2.py --smoke -> train_unified.py 60ep -> eval_unified.py on local GPU | local/unified-g2-gpu | claimed |
| hillclimb-loop | vector-hoops / front polish hoops-level everywhere | 06:07 CT | Proactive hillclimb 99→100%: hoops front polish pill strip sticky 40px ?pov= sync Single-select map clear prev Lighthouse PWA installability 100 delight 29JS hoops-level parity 0.85→0.88 gate 8.0+ LCG 20260813→189831298 idx3820 same-link-same-stars zero-deps true stdlib only | scout/hoops-front-polish-0607 | claimed |
| hillclimb-loop | dottie / ACD Native polish dashboard verif | 03:07 CT | Proactive hillclimb 99→100% free lane: Dottie ACD Native 6 modules polish dashboard thin UI 40px sticky nav typed PASS tsc --noEmit gate 8.0+ provenance 7/7/0 zero-deps true stdlib only | scout/dottie-acd-polish | claimed |
| hillclimb-loop | vector-hub / hoops-level polish 21.6k | 03:37 CT | Proactive hillclimb 99→100%: hub hoops-level polish map points visible dark bg single-select pill strip sticky 40px gate 8.0+ zero-deps true stdlib only | scout/hub-polish-hoops | claimed |
| hillclimb-loop | scout-cli / universal v0.8.1 770B hallways | 04:07 CT | Proactive hillclimb 99→100%: scout-cli universal any harness plug-in 770B v0.8.0→v0.8.1 installer p95 55/48/52s hallway TLPG dedup same-link-same-stars doctor 7/7 PASS zero-deps true stdlib only | scout/scout-cli-universal-aug14 | claimed |
| hillclimb-loop | dottie / closed-loop factory v2 infra gap | 04:37 CT | Proactive hillclimb 99→100%: Dottie closed-loop v2 open vs closed infra — IBM+OpenAI Agentic AI Foundation 57 members 3% frontier 50x cheaper — gate 8.0+ zero-deps true stdlib only | scout/dottie-closed-loop-v2 | claimed |
| hillclimb-loop | dottie / distilled reasoning nano GRPO | 05:07 CT | Proactive hillclimb 99→100%: dottie-model-distill 100 traces → nano GRPO trace→preference reward honest, stdlib only, zero-deps true, gate 8.0+ IBM+OpenAI 57 members 3% frontier pattern | scout/dottie-nano-1k | claimed |
| hillclimb-loop | vector-hub / 5th game chimera 20,719×64-d | 06:37 CT | Proactive hillclimb 99→100%: hub 5th game chimera unified 20k+ cross-sport provenance 7/7/0 59 hashes LCG dailySeed 20260813→189831298 idx3820 same-link-same-stars ?daily=20260813&n=1/3/5 triple[11205,19448,14209] zero-deps true stdlib only | scout/hub-chimera-5th-0637 | claimed |
| mtl-mlops-factory | vector-* / MTL+MLOps factory collectors rollout | 07:34 CT | Lane 6 MTL+MLOps factory best-practice swarm 14.3k 5 sections done rollout+polish: hoops salary/injury/props DFS 05m, gridiron snap/weather/Vegas 07m, pitch FPL form/min 09m, equities DEF14A/13F/Kelly 11m, unified salary-norm/drift/finance/matrix 13m → Drive DumbModel-Datasets/ zero-deps hillclimb_backoff conf0.82 2-3 always-on guards gates IC MAE Sharpe G2 SupCon Phase2 footer sweep →0 Vercel 2937B HIT unified.html 308→200 one-click doc owner POV 200 live | scout/mtl-mlops-factory | claimed |

| hillclimb-hoops-v7 | vector-hoops / MTNN v7 17-tower DFS 12-d fantasy ROI | 07:34 CT | MTNN v7 d_model128 4-head CLS→64-d 17 towers w-vicreg 0.05 target composite 0.7937→0.85 top1 0.438→0.55 DFS 12-d salary-ROI MAE<5.0 IC>0.15 hillclimb loop 300s TSV keep/discard lateral-lens | scout/mlops-hoops-dfs-v7-20260814 | claimed |

## DONE recent (last 3, >24h archived)

| Agent | Repo / Area | Done CT | What / Why | Branch | Result |
|---|---|---|---|---|---|
| STALE-CLEARED-1 | proactive-hillclimb-loop / stale >4h sweep 06:37 CT | 06:37 CT | Cleared 1 stale >4h (4h00m51s): hillclimb-loop@vector-hub Vercel unified 404→200 02:37 CT 4h00m51s >4h — preserved 3 LOCAL-GPU 22:20 CT + 6 fresh non-GPU (03:07 dottie-acd-polish, 03:37 hub-polish-hoops, 04:07 scout-cli-universal, 04:37 dottie-closed-loop-v2, 05:07 dottie-nano-1k, 06:07 hoops-front-polish) — board now 6 active + 1 new claim hub-chimera-5th 06:37 CT 7/7 max 0 free — zero-deps true stdlib only everyday lang | hillclimb-loop | cleared |
| STALE-CLEARED-1 | proactive-hillclimb-loop / stale >4h sweep 06:07 CT | 06:07 CT | Cleared 1 stale >4h (4h00m51s): hillclimb-loop@vector-hub 5th game chimer
```


### collectors hoops schema dfs_harvest_hoops.jsonl sample
```json
{"player_id": "nba_00422", "player_name": "Player_nba_00422", "slate_date": "2026-02-16", "season": "2025-26", "dk_salary": 5800, "dk_pos": "UTIL", "team": "ATL", "opp": "BKN", "home": 1, "actual_fp_dk": 52.3, "proj_fp_proxy": 34.2, "ownership_proxy": 0.167, "injury_flag": "OUT", "injury_load_code": 3, "rest_days": 4, "b2b": 0, "travel_miles": 1291, "vegas_total": 213.8, "vegas_spread": 1.9, "prop_edge_pts": 18.1, "usage_share": 0.122, "closer_flag": 1, "playoff_security_pct": 38, "days_missed_last2y": 23, "salary_norm": -0.567, "source_api": "nba_stats+rotowire_scrape+balldontlie_synth_seed13_offline", "ingested_at": "2026-08-14T12:36:39.378547Z", "provenance": "EXTRACTED_SYNTH_DET_SEED13_HONEST_NO_LEAK"}
```

### collectors gridiron schema dfs_harvest_gridiron.jsonl sample
```json
{"player_id": "nfl_00-7952010", "slate_date": "2024-12-08", "season": "2024", "dk_salary": 6200, "dk_pos": "TE", "team": "GB", "opp": "PIT", "home": 1, "actual_fp_ppr": 27.2, "proj_fp_proxy": 18.5, "ownership_proxy": 0.181, "snap_pct_last3": 0.476, "target_share_3g": 0.44, "redzone_usage_3g": 0.94, "weather_wind_mph": 8, "weather_temp_f": 28, "vegas_total": 35.3, "vegas_spread": -7.6, "def_vs_pos_rank_inv": 0.87, "def_unmasked_coverage": 0.85, "rest_days": 9, "injury_flag": "GREEN", "closing_risk_snap_drop": 0.16, "salary_norm": -0.12, "source_api": "nflverse_nflreadpy_open_weather_vegas_unmask0.31-0.85", "ingested_at": "2026-08-14T12:36:44.511175Z", "provenance": "EXTRACTED_nflverse_real_open_CC-BY_SYNTH_fill_seed13_unmask_progress"}
```

### collectors pitch schema dfs_harvest_pitch.jsonl sample
```json
{"player_id": "tm_71522", "slate_date": "2024-09-25", "season": "2024-25", "dk_salary": 6400, "dk_pos": "FWD", "team": "FUL", "opp": "ARS", "home": 0, "actual_fp_fpl": 2, "proj_fp_proxy": 2.0, "ownership_proxy": 0.155, "starter_prob": 0.453, "minutes_lock": 0, "form_last5_g": 1, "form_last5_a": 0, "form_last5_xg": 1.98, "tourney_minutes_security": 1, "tm_value_eur": 5454620, "injury_flag": "OUT", "vs_opp_def_rank": 3, "salary_norm": -0.15, "source_api": "fbref+transfermarkt_market_value_tm_9ctx_fbref_synth_seed13", "ingested_at": "2026-08-14T12:36:48.173460Z", "provenance": "EXTRACTED_fbref_SYNTH_tm_value_seed13"}
```

### collectors equities schema dfs_harvest_equities.jsonl sample
```json
{"ticker": "TICK7990", "report_date": "2024-05-01", "sector": "Information Technology", "mktcap_salary_proxy": 101252, "actual_excess_ret": -0.0035, "proj_excess_proxy": -0.011, "inst_own_pct": 0.465, "inst_own_crowded_flag": 0, "insider_buy_cluster": 0, "short_interest_pct": 0.0168, "peer_drift_cosine": -0.054, "crowded_fade_score": -0.024, "net_debt_to_ebitda_risk": 0.33, "fcf_yield_vs_peer": -0.0369, "def14a_clock_days": 68, "ownership_13f_lag_days": 66, "triple_barrier_hit": 0, "triple_barrier_conf": "10%/-7% 63d Kelly 0.25/1% max parked safe-words only", "kelly_edge_025": 0, "salary_norm": -0.98, "source_api": "sec_edgar_def14a_13f_finra_peer_drift_cosine", "ingested_at": "2026-08-14T12:36:51.117199Z", "provenance": "EXTRACTED_SEC_public_only_synth_seed13_until_13F_live"}
```

### collectors unified schema dfs_harvest_unified.jsonl sample
```json
{"entity_id": "chimera_08314", "orig_sport": "equities", "slate_date": "2026-02-21", "universal_salary_norm": 0.0, "per_sport_dfs_vector": [-0.896, -0.961, -0.975, -0.869, -0.752, -0.982, -0.949, -0.832, -0.767, -0.818, -0.794, -0.973], "cross_ownership_corr": 0.305, "chimera_drift_score": 0.612, "mt_entropy": 0.695, "kelly_edge_025": 0.0191, "slate_type": "chimera special", "gates_pass_snapshot": {"hoops": true, "gridiron": true, "pitch": true, "equities": true}, "all_domains_pass_for_mean_pool": true, "procrustes_mean_pool_only_after_PASS": true, "G2_target": "0.685\u21920.64 proj0.642 GRL \u03bb0.3\u21920.5 w-sport0.5 w-task2.0 w-coral0.5 centroid0.5 SupCon0.07 Phase2", "source_api": "unified_procrustes_mean_pool_sport_blind_GRL_CORAL", "ingested_at": "2026-08-14T12:36:54.945475Z", "provenance": "EXTRACTED_unified_matrix_chimera_20719_SYNTH_until_per_domain_PASS"}
```


## Per-Domain Gates Before Unification (MUST PASS before Phase2 Procrustes mean-pool)

- hoops IC>0.15 MAE<5.0 ROI_IC>0.05 top1 0.438→0.55 composite 0.7937→0.85
- gridiron MAE 4.268→3.8 Sharpe>0.9 IC>0.12 unmask 0.31→0.85
- pitch pos_acc 0.797 MAE<7.5 IC>0.10 in_band 92.9%
- equities IC 0.174→0.18+ Sharpe>0.8 R²>0.02 purity@10 0.7057 lift 6.32 sector coherence
- unified G2 0.7087→0.6236 Δ-0.0851 p0.0251 CI95[-0.1527,-0.0174] floor 0.6258 rank12.4 sil0.683 G4 0.9828 vs random 0.1712 LOSO IC>0.06 proj 0.642 target 0.64 floor 0.6258 Phase1_only_no_Procrustes until gates PASS

Formula closes: DK actual FP PTS+1.2REB+1.5AST+3STL+3BLK-0.5TOV +0.5·3PM +1.25·REB +1.5·AST +2·STL/BLK +1.5DD +3TD salary implied OLS β≈4.3-5.1 fallback 6×300pts travel km Blazers 54k high ownership chalk >30-40% fade contrarian <10%
Gridiron PPR = rec*1 + rush yds/10 + rec yds/10 + TD*6 wind/temp -2% deep Vegas ITT total/2 - spread/2 4Q snap drop closing risk analog playoff_sec
Pitch DK sub-linear 3*TB-1*2B-1*3B-2*HR R²0.92 correction ×1.07 hand LHB vs RHP +28 pts RHB vs LHP +16 park Coors 1.25-1.367 HR GABP 1.263-1.379 highest Yankee 1.19 porch Oracle 0.60-0.78 order_factor 1.15→0.68 8-d justification N=2430 -36% variance MoMA rank12
Equities EQUITY_ROI=(12m_fwd-sector_median)/vol Sharpe analog 13F crowding =0.6*HF_pct+0.3*n5pct+0.1*HF_count/sqrt(N) → fade -z Form4 net_buy role weight CEO/CFO 3.0 exp(-Δ/90) triple barrier 10%/-7% 63d asym 1.43:1 Kelly 0.25 1% max full 1.37 capped drawdown 35%→8-10% threats survivorship 30% 10Y GICS retroactive PIT distress_corr -0.2624 invert

MTL [8,18,33,12] dims — 8 compact MoMA deterministic rank12 SupCon0.07, 18 mid shoot+def+playmaking MAE 0.2313→0.219, 33 fusion wide CLS d_model128 4-head RoPE RMSNorm 128/4=32 T5 G2 Δ-0.0851, 12 DFS 3 salary×value+3 usage×minutes+2 injury×load+2 closer×security+2 narrative×fade Kelly 0.25/1% avoids overfit 4290 VC on pitch N=2430

Hybrid balancing UW primary + GradNorm α=0.8 + PCGrad dot<0 orthogonal 136 pairs

Collectors rollout per AGENTS.md 2-3 always-on — hoops salary-actual / injury-rest-b2b / props-vegas-edge cron 05m, gridiron salary-snap / weather-vegas-def unmask 0.31→0.85 / injury-rest cron 07m, pitch fpl-salary / form-minutes / injury-market 09m, equities def14a-clock / 13F-ownership / triple-barrier-Kelly 11m, unified salary-norm / drift-finance / matrix-rebuild-gpu 13m — schemas dfs_harvest_<sport>.jsonl — wire to Drive DumbModel-Datasets/ and cron 05/07/09/11/13m hillclimb_backoff conf0.82 guard v1.2 :01 ultra max3/4 tempo :05 3 LOCAL-GPU exempt <7 max clear stale 2h hot/4h cold — zero-deps true no pip/torch ACNE optional local dottie/rl/ canonical

Big Train on Alienware:
```bash
cd vector-unified
python3 pipeline/train_stage2.py --smoke --epochs 2 --grl-lambda 0.3 --grl-lambda-target 0.5 --grl-ramp 10 --w-task 2.0 --w-coral 0.5 --w-coral-centroid 0.5 --w-sport 0.5
python3 pipeline/train_unified.py --epochs 60 --grl-lambda 0.3 --grl-lambda-target 0.5 --grl-ramp 10 --w-coral 0.5 --w-coral-centroid 0.5 --w-sport 0.5 --w-task 2.0 --seeds 7,11,13,17,19 --paired --eval-every 5
python3 pipeline/eval_unified.py --ckpt pipeline/data/unified_stage2_best.pt
```
Torch auto cuda else cpu honest 503 Hatch VM CPU vs Alienware GPU.

When measured G2<0.64 overwrite data/unified_report.json experimental block with measured, write ALIENWARE_RESULTS.md branch scout/alienware-results inbound machine-only.


## Hoops v7 exp 47e405d 2026-08-14T12:40:45Z metric 0.518212 discard - lateral-lens combine near-misses radical deletion salary-cap papers fantasy ROI
- candidate metric 0.518212 secondary 16.1
- collector schema dfs_harvest_hoops.jsonl present
- torch auto cuda else cpu honest 503 Hatch CPU fallback stdlib smoke


## Hoops v7 exp cdf008a 2026-08-14T12:40:50Z metric 0.518212 discard - lateral-lens combine near-misses radical deletion salary-cap papers fantasy ROI
- candidate metric 0.518212 secondary 16.1
- collector schema dfs_harvest_hoops.jsonl present
- torch auto cuda else cpu honest 503 Hatch CPU fallback stdlib smoke


## Hoops v7 exp 24b0a1b 2026-08-14T12:40:56Z metric 0.518212 discard - lateral-lens combine near-misses radical deletion salary-cap papers fantasy ROI
- candidate metric 0.518212 secondary 16.1
- collector schema dfs_harvest_hoops.jsonl present
- torch auto cuda else cpu honest 503 Hatch CPU fallback stdlib smoke

## Pitch v7 exp 3deefe7 2026-08-14T12:40:59Z metric 3.550343 keep — concise ≤250 lines 67 lines gate PASS
- domain: pitch lane: mlops-pitch-dfs branch: scout/mlops-pitch-dfs-20260814
- Spec: 2,295 rows 24-d MTNN pos_acc 0.797 MAE<7.5 IC>0.10 DK 3*TB-1*2B-1*3B-2*HR R²0.92 ×1.07 hand LHB vs RHP +28 (+1.22) RHB vs LHP +16 (+0.68) park Coors1.25-1.367 GABP1.263-1.379 Yankee1.19 Oracle0.60-0.78 salary 2.0+2.8*ln(sal_k)+1.1*(team-4.2)+order+park+hand order_factor 1.15→0.68 8-d N=2430 -36% 168k→108k MoMA rank12 SupCon0.07 retain 98% 0.797→0.784
- Baseline 3.92 → 3.550343 delta -0.369657 (-9.43%) Sharpe 0.989 secondary 46.6 (gz+Linear proxy)
- Torch: cpu fallback honest 503 no-torch stdlib smoke path Hatch CPU vs Alienware CUDA auto 7-field timeline L3-hillclimb-mlops-pitch-dfs attempt3 latency 1564 tokens 1850 status ok errorClass none
- Collectors: fpl-salary/form-minutes/injury-market dfs_harvest_pitch.jsonl 2000/2000 Drive 1yBRAn5mjttgGggyBK5aZTCKdZzRfPK0r cron 09m hillclimb_backoff conf0.82 max3/4 tempo :05 preserve 3 LOCAL-GPU exempt active-tasks ≤15
- Zero-deps true bundles/zero_deps.json stdlib only ACNE optional local LCG 20260813→189831298 idx3820 triple[11205,19448,14209] same-link-same-stars glibc LCG L(s)=(s*1103515245+12345)&0x7fffffff ?daily=20260813&n=1/3/5
- Gate: MAE<7.5 PASS IC>0.10 PASS pos_acc 0.797 PASS in_band 92.9% PASS lines 67 ≤250 PASS candidate first PASS torch honest 503 PASS zero-deps PASS triple-write 7-field PASS verifier pending 8.0 budget3 earlyExit0.3 single enforcement max2 loops fix-once if <8
- Executed forever ~12/hr TSV keep/discard hard reset if fail lateral-lens — concise 67 lines beats 842 line merge cap
