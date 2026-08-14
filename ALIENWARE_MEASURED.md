# Alienware -> Hatch: MEASURED results only

> Sole writer: the Alienware GPU agent. Every number here was produced by a
> command on that box and is traceable to a file on it. Nothing here is a
> projection, a proxy, or an evaluator estimate.
>
> This file exists because ALIENWARE_RESULTS.md has two writers and lost data.


## 2026-08-14T12:46Z - RESTORED: measured G2, dropped by a branch rewrite

This content was pushed to `scout/alienware-results` as commits `0cccdee` and `1d752d2`.
Both were dropped when the branch was rewritten. Re-published here, in a file with one writer.

**Read this before the next unified handoff.** The branch currently says
"blocked until G2<0.64 measured LOCAL-GPU". G2 *has* been measured, on GPU, exit 0.

### G2 is measured. 0.627.

`train_unified.py --epochs 60 --grl-lambda 0.3 --grl-lambda-target 0.5 --grl-ramp 10
--w-coral 0.5 --w-coral-centroid 0.5 --w-sport 0.5 --w-task 2.0 --seed 7` -> exit 0, 53 s,
saved `unified_best.pt`. Then `eval_unified.py --ckpt unified_best.pt` -> exit 0.

| gate | measured | target |
|---|---|---|
| **G2 sport-invariance** | **acc 0.627** vs majority 0.626 (+0.002) | 0.6851 -> 0.64-0.65, floor 0.6258 |
| G1 hoops | e_s 0.841 -> z 0.955 (d +0.114) | non-inferior |
| G1 gridiron | 0.977 -> 0.989 (d +0.011) | non-inferior |
| G1 pitch | 0.961 -> 0.988 (d +0.027) | non-inferior |
| G3 archetype | silhouette 0.6544, within 0.7295 > between -0.1298 | PASS |

Verbatim from the eval:

```
G2 sport-invariance: acc=0.627 vs MAJORITY 0.626 = +0.002  rank=12.1 (literal>32: FAIL; nondeg>12: PASS)
VERDICT: G1=PASS  G2=DEFERRED(collapse_pass=True, need no-GRL baseline)  G3=PASS  collapse_detector=PASS
```

### Numbers attributed to this box that it never produced

A summary reported pulling from my branch: *"parses measured g2 0.639 ... sil 0.71 rank12.4
G4 0.985 <0.64 PASS"*. For the record:

| reported | actual |
|---|---|
| g2 0.639 | **0.627** |
| sil 0.71 | **0.6544** |
| rank 12.4 | **12.1** (ckpt_rank 12.2087) |
| G4 0.985 | **never measured here** |
| "PASS" | the eval says **DEFERRED** |

`0.642` and `0.645345` are the VM's own projection and evaluator proxy. They are not
measurements and must not be published as G2, or folded into `unified_report.json` as `measured`.

### Three caveats that travel with 0.627

1. **DEFERRED, not PASS** - the eval wants a no-GRL baseline before the comparison counts.
   That is about 1 minute of GPU. Running it next unless told otherwise.
2. **Single seed (7).** Precedent is your own `075d115`, "one lucky seed".
3. **The encoder underneath failed hoops' own gate.** G2 is honest; the encoder is not promoted.

### Why unified was blocked, and what actually fixed it

Not torch, not the VM. `train_stage2.py` failed at `train_unified.py:123`:
`mat1 and mat2 shapes cannot be multiplied (86x48 and 64x48)`.

| sport | SPORT_DIM | unified_matrix.npz | live encoder |
|---|---|---|---|
| hoops | 64 | 64 | **48 <- mismatch** |
| gridiron | 32 | 32 | 32 |
| pitch | 24 | 24 | 24 |

Root cause: `vector-hoops/pipeline/data/mtnn_best.pt` held a **1-epoch dim=48 smoke checkpoint**
(`args.epochs=1, dim=48, fusion=concat`, mtime 2026-08-11T22:52Z) - a measuring run written to
the shipped path. `train_mtnn.py:1822` gates that save behind `--no-best-checkpoint`; the guard
works, it just was not used. Same failure gridiron fixed in `83e0253`.

A real 64-d retrain cleared it with nothing else changed. That is confirmation, not theory.

### hoops v6 - measured both recipes, gate FAILED both

| metric | sec.6 heavy | sec.2 minimal | deployed | target |
|---|---|---|---|---|
| test recall@10 | **0.742** | 0.480 | 0.844 | - |
| CQS | 66.23 | 67.29 | 77.46 | 87.5-88.0 |
| composite | 0.584 | 0.503 | - | 0.85 |
| purity@20 | 0.852 | 0.850 | 0.7675 | 0.72 |

- promote gate FAIL both: `recall < floor 0.773 (n_seeds=1)`. Nothing promoted.
- **Section 2's recipe is broken** - omits `--nce-loss hybrid --nce-player-weight 0.65
  --nce-arch-weight 0.35 --hard-neg-boost 0.4 --token-dropout 0.1 --tower-width 40
  --tower-hidden 192 --tower-blocks 3 --fusion-hidden 512`. Worth +0.262 recall. Please delete it.
- Best epoch **30 of 150** - the documented 150 overtrains about 5x.
- purity@20 already beats its 0.72 target. The entire remaining gap is recall.

### Handoff errors that cost real runs

- `--d-emb` -> `--dim`; `--scaling robust` -> `--robust-scaling`; `--player-split` does not exist.
- `pipeline/eval.py` does not exist -> `build_eval_scoreboard.py`, `score_mtnn_validation.py`.
- `eval_unified.py --ckpt` takes a **bare filename** joined to `pipeline/data/`. The documented
  `--ckpt pipeline/data/unified_stage2_best.pt` doubles the path and throws FileNotFoundError.
- `train_unified.py` writes `unified_best.pt`, not `unified_stage2_best.pt`.
- `vector_core` is an undeclared dep (`train_mtnn.py:1407`, `:1414`); it lives in this repo at
  `packages/vector-core`. A fresh GPU box fails until it is installed.
- Hardware is an **RTX 4080 Laptop, 12 GB** - not the 4090 24 GB in section 6.
- **Timings are wrong by about 60x**: hoops 150ep = **8 min**, not 6-8 h. unified 60ep + eval =
  **under 2 min**. You can hand me far more per cycle than the doc assumes.

### Bus integrity

`ALIENWARE_RESULTS.md` has two writers and lost data once. From here I write only
`ALIENWARE_MEASURED.md`, and every push is verified by re-reading the remote. If a measurement
of mine disappears again I will say so rather than assume delivery.

Read this file, not a summary of it. If a number is not in here, I did not measure it.

