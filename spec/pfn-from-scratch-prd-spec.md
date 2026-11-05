# From-Scratch PFN — Critical Review, PRD, SPEC (P2 of the mandala review loop)

**Status:** DRAFT for owner review. Nothing here starts a GPU job.
**Scope:** the own-build prior-data fitted network (PFN) program described in the Harada mandala dated 2026-11-05 12:22 CST.
**Vintage:** 2026-11-05.

> **Review basis.** Only the mandala text was available to this session (pasted inline). `tabular_ic.py`, `PREREG.md`, `PRD-SPEC.md` §7 (Amendment A1), and `jobs/J1.md` were not reachable, so every fact about them is taken from the brief and the mandala as stated: seed 72,194 params / 2-layer 4-head / dev Brier 0.2503 / ECE 0.025; J1 = 31,812 rows, Brier primary, ECE gate 0.05; STRABLE prereg locked at sha256 2322832c…5d385d. Where the paper is cited, the citation is to the published Nature article (Hollmann et al. 2025, doi:10.1038/s41586-024-08328-6) and its public methods text. No TabPFN code, weights, or outputs were consulted, and the SPEC forbids consulting them. Numbers from the paper quoted below (layer count, embedding width, training context size) are from memory of the published text and must be re-checked against the paper by the worker before being written into config; the SPEC marks each such number **[verify vs. paper §Methods]**.

---

## 0. Verdict in one paragraph

The mandala has the right constraint (the prior) and the right boundary (paper only, no artifact), but it is not yet executable as a contract. Four holes are blocking. **(H1)** The P1 done-check is unmeasurable: the paper does not publish the prior's marginal statistics, so "marginals match the paper" can never be shown true or false. **(H2)** The mandala has no answer for the one fact that decides whether this program can touch J1 at all: a PFN takes the labeled table *as context in one forward pass*, and the paper's training context is on the order of a thousand rows, with inference claims up to roughly ten thousand. J1 has 31,812 rows. Nothing in the mandala says how 31,812 rows become a context. Without a context-selection design, P4 and P5 are undefined. **(H3)** D1's first rung (1M tables) is a cost commitment made before anyone has measured tables-per-second on the 4080. The honest first rung is a throughput benchmark and a 50k-table smoke run, not 1M. **(H4)** P4's gates are copied from STRABLE D10 and are the right *shape*, but the baseline they reference is unnamed, and comparing a zero-shot model against a catboost tuned on the full 31k-row train split is not a fair test of the thing being built. The program survives review with the fixes below. The win condition should be restated now, before any GPU hour: **a model that beats logistic regression and approaches default random forest zero-shot on small public tables, pretrained from our own prior, is the deliverable. Beating tuned catboost on J1 is a stretch goal, not the gate.**

---

## 1. Critical review

### 1.1 Where the mandala breaks

| # | Claim in mandala | Break | Severity |
|---|---|---|---|
| R1 | P1 done-check: "marginal statistics match the paper's prior description" | The paper describes the prior's *generative process* (random SCMs, random nonlinear edge functions, noise, post-hoc type conversion, missingness). It does not publish marginal statistics of the resulting tables. This check cannot be run. Replace with learnability and coverage tests (§3 C1). | **Blocking** |
| R2 | P4: evaluate zero-shot on J1 (31,812 rows) | A PFN consumes the labeled training rows as transformer context. Attention across samples is quadratic in rows per feature; the paper trains with contexts of about a thousand rows **[verify]** and reports inference generalization to about ten thousand. 31,812 rows do not fit as one context on 12 GB, and even if they did, the model was never trained at that length. The mandala needs a context-selection policy (random subsample, stratified subsample, kNN-selected context per query, or ensembling over context draws) and must state it in the prereg addendum before the sealed read. | **Blocking** |
| R3 | D1: "1M synthetic tables first" | No throughput measurement exists. At the paper's shape, one 1,000-row × 100-feature table is ~100k cell tokens through 12 layers. A back-of-envelope on a 4080 (realistic bf16 ~20 TFLOP/s sustained) gives roughly 0.1 to 0.5 s per table fwd+bwd, so 1M tables is 1 to 6 days *if* the pipeline never stalls on the CPU-side prior sampler. That is tolerable, but it is a guess. The first rung must be a measured number. | High |
| R4 | D2: "d_model 128, ~12 layers, the paper's shape" | The paper's width is not 128 **[verify; recollection is 192 with 6 heads]**. More importantly, nothing in the mandala says whether the first run is the full shape or a small shape. A 12-layer model as the *first* thing trained means the first signal about the prior arrives after days, not hours. Rung 0 must be small. | High |
| R5 | P2: "AttnFeat / AttnSamp interleaved, per-layer MLP" | Correct mechanism in outline, but three things the paper's method depends on are absent: (a) attention masking so that query rows attend to context rows but context rows never attend to query rows, and query rows never attend to each other; (b) the target is injected as an extra feature column whose value is masked on query rows, not as a separate head input; (c) no positional encoding over features or samples, so the model is permutation-equivariant and is trained with random feature and row permutations. Missing any of these produces a model that is not a PFN. | High |
| R6 | P2: "mixed feature types" handled | The mandala says the prior produces booleans, categoricals, ordinals, integers, continuous. It does not say how the *model* ingests them. The paper's approach is to encode every cell as a scalar after per-feature preprocessing (quantile or power transform, categorical to integer codes, missing as a value plus an indicator) and let the per-cell embedding learn the rest. The mandala must choose and record this; it is a provenance item (paper section → our implementation). | Medium |
| R7 | P4: "J2 next-season stats" | That is a regression target. The mandala's P2 and P3 describe only a classification head ("masked targets", "class imbalance"). Regression in the paper uses a discretized output distribution over bins (a histogram head). Either add the regression head to P2 or drop J2 from P4. Default: add it, because the bar-distribution head is cheap and J2 is where a calibrated distribution is actually useful. | Medium |
| R8 | P4 gates: "Brier skill > 0 vs reference, resolution ≥ reference" | "Reference" is unnamed. Brier skill score is conventionally vs. the climatological base rate on the dev fold. Resolution floor needs a number or a named comparator. The mandala also inherits "Holm margins" without saying across which family of comparisons. §3 C5 names each. | Medium |
| R9 | P4: "vs catboost / extratrees baselines" | Three different comparisons are being conflated: (i) catboost tuned on the full 31k train split (ceiling, not fair to zero-shot); (ii) catboost at default hyperparameters on the *same context subset* the PFN sees (like-for-like); (iii) the 72k seed model (proves the prior added something). All three should be reported; only (ii) and (iii) are gates. | Medium |
| R10 | P3: "curriculum small tables first, then larger" | Fine, but the mandala has no checkpoint policy, no resume test, no definition of "improves with more pretraining" (which held-out set, which metric, which minimum delta). Training on one consumer GPU will be interrupted. A run that cannot resume byte-identically is not evidence. | Medium |
| R11 | P6: "grep audit clean for tabpfn/priorlabs" | Necessary, not sufficient. The real exposure paths are (a) someone `pip install tabpfn` to "compare", (b) a worker opens the public TabPFN repo "just to check a shape", (c) a synthetic dataset dump published by the authors gets used as training data. Add a CI guard on the dependency manifest and a written rule that the repo is not to be opened. Note for the owner: TabPFN v1's code (ICLR 2023) was released under a permissive license, but the standing constraint says *no TabPFN code*, and the SPEC honors the constraint as written. | Medium |
| R12 | Seed: "proves the mechanism" | The seed has Brier 0.2503 and ECE 0.025. That is a well-calibrated model with no resolution: it has learned the base rate. It proves the training loop runs, not that in-context learning happens. The prior-validation gate (C1) is where the mechanism gets proven, on synthetic tables where a kNN baseline can be beaten. | Low (framing) |
| R13 | "Zero borrowed weights, code, or outputs" | Confirmed consistent throughout the mandala. No crossing found. One soft spot: the mandala cites only the Nature paper; the ICLR 2023 PFN paper (Müller et al., "Transformers can do Bayesian inference") and the TabPFN v1 ICLR 2023 paper are also published method sources and may be cited. Citing papers is inside the boundary; reading their code is not. | None (clarification) |

### 1.2 What is underspecified

- **U1.** The prior's hyper-prior: how many nodes, what edge density, which activation families, what noise scales, how targets are chosen from nodes, how classes are made from a continuous node. Each needs a declared range in config, with the range itself a provenance item.
- **U2.** Maximum rows and features per training table, and the distribution over them. This bounds VRAM and throughput before anything else does.
- **U3.** Missing-value mechanism. MCAR only, or also MAR via another node? The paper's prior includes missingness; the exact mechanism is a provenance item.
- **U4.** Inference-time ensembling. The paper's reported numbers use ensembles over feature permutations and preprocessing variants. A single forward pass is the mechanism; the headline number is an ensemble. The SPEC must say which is reported.
- **U5.** Class count ceiling. Paper-style classification heads have a fixed maximum class count. J1 is binary; small-table benchmarks go up to ten. Declare the ceiling.
- **U6.** Time ordering in J1 folds. Props rows have dates. Context subsampling must respect whatever fold boundaries J1 declares (not reachable here), or the zero-shot eval leaks the future into context.
- **U7.** Who runs the sealed read and who sees it first. STRABLE's rule is read once. The addendum must name the operator and the artifact that proves the read count.
- **U8.** Where checkpoints live. They are hundreds of MB; not in git. A manifest with sha256 per checkpoint is the evidence, not the file.

### 1.3 The central risk: the prior is the bet

The mandala says it, and it is right: if the prior is wrong, the model is wrong. What the mandala lacks is a way to know the prior is wrong *before* the GPU spend. The paper's own argument is that the prior does not need to match reality; it needs to make the transformer learn a good inductive bias (simplicity, causal structure, sensible noise). That means the test of the prior is not "does it look like real data" but **"does a small model trained on it learn to do in-context learning, and does that learning transfer to real small tables."** Section 3, component C1, turns that into four runnable checks with pass thresholds. None of them needs more than a few GPU hours.

### 1.4 Regime honesty, restated

J1 at 31,812 rows is outside the paper's regime in two ways: the context cannot hold the training set, and a tree ensemble with 31k rows of real signal will usually beat a zero-shot prior. The caveat stays. What makes the program worth it even if the PFN loses on J1:

1. A model that zero-shots any ≤10k-row table beats tuned baselines on *most* of the tables the family will meet (per-player, per-season, per-market cuts are all small).
2. A calibrated predictive distribution from one forward pass is a leaderboard entry that costs no tuning time per job.
3. The prior generator is a reusable asset: it is the same object you would use to pretrain the next model.
4. Fine-tuning the pretrained PFN on J1 (D3's optional lane) is the realistic path to competing on large tables, and is cheap once pretraining exists.

If after C1 passes and rung 1 completes the model still cannot beat logistic regression on small public tables, that is kill criterion K1 (§4).

---

## 2. PRD

### 2.1 Problem

The leaderboard slot TabPFN vacated (Amendment A1) is empty. The family needs a tabular model that predicts a new table without per-table training, with a calibrated output, built from code and weights the family owns outright. The existing seed proves the training loop, not in-context learning: it predicts the base rate.

### 2.2 Users

1. **The owner (Cameron).** Wants an own-built model on the leaderboard, a provenance trail that would survive an audit, and an honest read of where it wins and loses. Gates merges, releases, production.
2. **The STRABLE harness.** Needs a family entry that takes a job's train/dev split and returns calibrated probabilities (and a distribution for regression) inside the harness's time budget.
3. **The next program.** Will reuse the prior generator and the pretrained checkpoint as a starting point for fine-tuned or larger models.

### 2.3 Goals

- G1. A prior generator, own code, that produces tables a small transformer can learn in-context from, proven by C1 before any multi-day run.
- G2. A per-cell transformer, own code, implementing the published mechanism, with tests that would fail if any of the three mechanism properties (R5) were missing.
- G3. A pretrained checkpoint, with a loss curve and a synthetic held-out curve, trained in resumable rungs on the 4080.
- G4. A zero-shot evaluation on small public tables and on J1/J2 dev folds, with the three baselines of R9, under the gates of C5.
- G5. A harness family entry that runs end to end and lands in results.json.
- G6. A provenance log and a license audit that an outside reader could follow from paper section to code line.

### 2.4 Non-goals

- Matching the paper's pretraining scale (order 10^8 tables) in this program.
- Beating tuned catboost on J1 as a gate (stretch only).
- Any public release, any public repo, any weight upload. D4 stands.
- Any use of TabPFN code, weights, outputs, or author-published synthetic dumps.

### 2.5 Success

The program is successful when: C1 through C6 each have their evidence artifact in the named location; the small-table gate in C5 passes; the J1 read reports honestly whether the PFN beat the like-for-like baseline; and the family entry is live in the harness. J1 victory over tuned catboost is reported if it happens and is not required.

---

## 3. SPEC with per-component evidence contracts

Each component states: what it is, what "done" means, what evidence proves it, and where the evidence lives. Paths are relative to `~/workspace/pfn-from-scratch/` (D4). "Report" means a markdown file with the numbers inline and the command that produced them.

### C0 — Paper-to-spec provenance map (new; precedes all code)

**What.** A table mapping each design choice to the paper section that motivates it, written *before* the corresponding code. This is the mechanism that keeps the program inside the license boundary: if a choice has no paper citation, it is our invention and is labeled as such.

**Done when.** Every row of the config schema in C1 and C2 has a provenance entry: paper section, our interpretation, our parameter value, and a "paper / ours / unknown" tag.

**Evidence.** `provenance/PROVENANCE.md` with one row per config key. Diff-reviewed by the owner before C1 code starts.

### C1 — Synthetic prior generator

**What.** A sampler that returns `(X_context, y_context, X_query, y_query, meta)` tensors for one table, from a random structural causal model (SCM): random directed acyclic graph (DAG), random nonlinear edge functions, exogenous noise, a target selected from a node, post-hoc conversion of nodes to feature types, missingness, and a classification or regression target. All hyper-priors are ranges in a single config file.

**Config schema (minimum).** `n_rows ∈ [r_min, r_max]`, `n_features ∈ [f_min, f_max]`, `n_nodes`, `edge_density`, `activation_family`, `noise_scale`, `type_mix` (fraction boolean / categorical / ordinal / integer / continuous), `missing_rate` and mechanism, `task ∈ {binary, multiclass≤K, regression}`, `class_balance`, `seed`. Every key cites C0.

**Done when all four validation checks pass:**

| Check | What it proves | Pass threshold | Cost |
|---|---|---|---|
| V1 Structural | Generator does what the config says | 100% of 10k sampled tables: DAG acyclic, type histogram within ±5 pts of `type_mix`, missing rate within ±2 pts, no NaN in targets, row/feature counts in range; identical seed gives identical table | CPU minutes |
| V2 Difficulty spectrum | Tables are neither trivial nor noise | On 1k sampled tables, fit logistic regression, kNN (k=5), and a default 100-tree random forest on context, score on query. Pass if accuracy spread (10th to 90th percentile) is ≥ 0.25 for each learner and random forest beats logistic on ≥ 40% and loses on ≥ 10% of tables (nonlinearity is present but not universal) | CPU hour |
| V3 Learnability | A PFN can learn in-context from this prior | Train a seed-scale model (≤ 4 layers, d ≤ 128) for ≤ 2 GPU-hours on prior tables with ≤ 256 rows. Pass if on 1k held-out prior tables its mean query accuracy beats kNN by ≥ 3 pts and beats base-rate by ≥ 10 pts. This is the gate the mandala calls "P1's validation report, before any big GPU spend" | ≤ 2 GPU-hours |
| V4 Coverage | The prior spans the feature-type mixes of real tables | For J1's declared feature types (and 5 small public tables), compute summary vectors (type mix, n_features, missing rate, class balance). Each real vector must fall inside the convex hull, or within one std, of the prior's summary distribution. Also: a classifier trained to distinguish real-vs-synthetic *on summary vectors only* must score AUC ≤ 0.85 (we are not trying to make the prior indistinguishable from real data at the cell level; the paper's prior is not) | CPU hour |

**Evidence.** `prior/` (code), `prior/config.yaml`, `reports/C1-prior-validation.md` with V1–V4 tables and the exact commands, plus `reports/C1-samples/` with 20 sampled tables as CSV for eyeballing.

**Disagreement kept.** V4's threshold is a judgment call. An alternative view is that coverage of real summary statistics does not matter at all (the paper's argument). V4 is kept because the brief asked for a check that the prior "covers real feature-type mixes," and because it is cheap.

### C2 — Architecture

**What.** Per-cell transformer. One token per cell. Each layer: attention across features within a row, then attention across rows within a feature, then an MLP, with residuals and layer norm. The target is appended as one more feature column; its cells are masked (replaced by a learned mask embedding) on query rows. Output head reads the target-column cell of each query row: softmax over K classes for classification, softmax over B bins (histogram head) for regression.

**Mechanism properties that tests must enforce.**

1. **Masking.** Context rows attend to context rows only. Query rows attend to all context rows and to themselves, never to other query rows. Test: perturb one query row; no other query row's output changes.
2. **Permutation equivariance.** Permuting feature order or context row order leaves query predictions unchanged up to float tolerance. Test: assert on random permutations. No positional encoding anywhere.
3. **Target injection.** The target is a column, not a side input. Test: the model's input tensor has shape `(rows, features+1, d)`.
4. **Cell encoding.** Each scalar cell plus a missing-indicator goes through a per-cell linear embedding. Preprocessing (quantile transform per feature, categorical to integer code) happens outside the model and is recorded as provenance.
5. **Memory.** Attention uses a fused scaled-dot-product kernel so memory is linear in rows per feature; gradient checkpointing available per layer.

**Shape rungs.**

| Rung | Layers | d_model | Heads | Purpose |
|---|---|---|---|---|
| S0 | 4 | 128 | 4 | C1 V3 learnability gate, unit tests |
| S1 | 6 | 192 | 6 | First real run (C3 rung 1) |
| S2 | 12 | 192 **[verify vs. paper]** | 6 **[verify]** | Paper shape, only after S1 passes C3 criteria |

**Done when.** Unit tests for properties 1–4 pass; a forward and backward pass at S2 on a 1,024-row × 100-feature table fits in 12 GB with batch size ≥ 1; throughput measured (see C3 T0).

**Evidence.** `model/` (code), `model/tests/` (pytest, all green in CI), `reports/C2-architecture.md` with the test log and the VRAM/throughput table at S0/S1/S2.

### C3 — Pretraining

**What.** Train on prior tables from C1 with cross-entropy on query targets (classification) or histogram-bin cross-entropy (regression), under a curriculum of increasing table size, in resumable rungs.

**Rungs (replace D1's "1M first").**

| Rung | Tables | Shape | Gate to proceed |
|---|---|---|---|
| T0 Throughput | 1k | S1, S2 | Measured tables/s and GPU utilization; CPU prior sampler must not be the bottleneck (≥ 80% GPU busy). Produces the honest cost curve for all later rungs |
| T1 Smoke | 50k | S1 | Loss falls monotonically (smoothed); synthetic held-out accuracy beats kNN by ≥ 3 pts (same bar as V3, now at S1) |
| T2 First real | 1M | S1 | Held-out synthetic metric improves vs. T1 by ≥ 2 pts; small-table public benchmark (C5 B1) beats logistic regression |
| T3 Scale | 10M | S2 | Only if T2's curve is still falling. Expected wall time from T0, written down before starting |

**Checkpoint policy (new decision D6).** Save every N steps (default 2,000) and at every rung end; keep last 3 plus every rung-end; each checkpoint gets a sha256 and a line in `runs/MANIFEST.json` with step, tables seen, loss, held-out metric, git commit of code and prior config. A resume test (kill at step k, resume, compare loss at step k+100 to an uninterrupted run within tolerance) is part of T1.

**Done when.** T0 and T1 complete with their gates; T2 complete is the deliverable; T3 is stretch.

**Evidence.** `runs/<rung>/` with loss and held-out curves as CSV and PNG, `runs/MANIFEST.json`, `reports/C3-pretraining.md` with the measured cost curve (tables/s, GPU-hours per rung, projected hours to T3).

### C4 — Context selection for large tables (new; required by R2)

**What.** The policy that turns a training split larger than the model's context limit into a context. Options: (a) uniform random subsample of L rows; (b) stratified by target; (c) per-query kNN context (nearest L context rows in preprocessed feature space); (d) ensemble of E random contexts, averaged probabilities.

**Default.** (d) with E=8 and L = the largest context the checkpoint was trained at, with (a) inside each draw. kNN context (c) is a documented alternative to try after the first honest read, never silently.

**Done when.** The policy is implemented, parameterized, respects J1's fold/time boundaries (U6), and its cost per job is measured.

**Evidence.** `eval/context.py`, `reports/C4-context-policy.md` including a table of dev Brier vs. L and E on one fold (dev only, this is a design read, not the sealed read).

### C5 — Zero-shot evaluation

**Benchmarks.**

- **B1 Small public tables (the real test).** A fixed list of ≥ 15 public classification datasets with ≤ 10k rows and ≤ 100 features (OpenML-style, list frozen in the addendum). Baselines: logistic regression, kNN, default random forest, default catboost. Gate: PFN mean rank better than logistic and kNN; mean accuracy within 2 pts of default random forest.
- **B2 J1 props dev folds.** Primary metric Brier. Gates (same shape as STRABLE D10): ECE ≤ 0.05; Brier skill score > 0 where the reference is the dev-fold base rate; resolution ≥ the resolution of the like-for-like baseline (R9-ii). Holm correction across the family of PFN-vs-baseline comparisons on B2 (three baselines, one fold set).
- **B3 J2 next-season (regression).** Only if C2's histogram head exists. Metrics: pinball loss at 0.1/0.5/0.9 and coverage of the 80% interval.

**Baselines reported on B2 (all three, always).** (i) catboost tuned on full train split: ceiling, informational. (ii) default catboost on the *same context subset* the PFN saw: like-for-like, gate. (iii) the 72k seed: proves the prior added something, gate (PFN Brier must be lower).

**Sealed read.** Exactly once, after the addendum (D5) is locked, by a named operator, with the run log committed. Dev folds may be read as often as needed before that and every read is logged.

**Done when.** B1 report, B2 dev report, and (if applicable) B3 exist; the sealed read has happened once or is explicitly deferred with a reason.

**Evidence.** `eval/` (code), `reports/C5-eval.md` with the gate table, each cell marked pass/fail, and a section titled "Where it loses" that is not allowed to be empty.

### C6 — STRABLE harness family entry

**What.** A family that accepts a job's train/dev split in the harness's format, applies C4, runs the checkpoint, returns probabilities (and bin distribution for regression), and writes to results.json.

**Done when.** End-to-end on J1 dev inside the harness's time budget, with the time budget number recorded; leaderboard shows the entry.

**Evidence.** Harness family entry (in the STRABLE repo), results.json rows, `reports/C6-integration.md` with wall time per job and the checkpoint sha256 used.

### C7 — License and provenance hygiene

**What.** Rules, guards, and the audit.

1. Dependency manifest guard in CI: fails if any package named `tabpfn*` or any PriorLabs package appears.
2. Grep audit: `tabpfn|priorlabs` allowed only in `PROVENANCE.md` and `LICENSES.md` as citations.
3. Written rule in `README.md`: the TabPFN repositories and any author-published synthetic dataset dumps are not to be opened or downloaded in this program.
4. `LICENSES.md` entry recording the boundary, the paper citation(s), and the date.
5. C0's provenance map kept current; a config key with no provenance row fails CI.

**Evidence.** `reports/C7-audit.md` with the grep output and CI run link; `LICENSES.md`.

### C8 — Prereg addendum (D5)

**What.** A separate document, never a change to the STRABLE prereg, that locks: the B1 dataset list, the C4 policy, the C5 gates and baselines, the sealed-read operator, and the checkpoint sha256 that will be read. Hashed and recorded before the sealed read.

**Evidence.** `PREREG-ADDENDUM.md` plus its sha256 in `reports/C5-eval.md`.

---

## 4. Kill criteria

- **K1.** C1 V3 fails after two prior-config revisions. The prior cannot teach in-context learning; stop and redesign the prior before any T-rung.
- **K2.** T2 completes and B1 still loses to logistic regression. The program is not producing a PFN; stop, publish the honest curve, decide whether to continue at T3 or fine-tune.
- **K3.** Any TabPFN artifact enters the tree. Program halts until the owner clears it.

---

## 5. Open decisions (numbered, bounded, named defaults)

| # | Decision | Mandala default | Review default | Reason |
|---|---|---|---|---|
| D1 | Pretrain scale, first run | 1M tables, then 10M | **Replace.** T0 (1k, measure) → T1 (50k smoke) → T2 (1M) → T3 (10M, conditional) | Cost must be measured before promised; the first signal about the prior must arrive in hours |
| D2 | Model size | ~12 layers, d 128 | **Correct.** S0 (4×128) for gates, S1 (6×192) for first real run, S2 paper shape **[verify width/heads]** only after S1 passes | 128 is not the paper's width; a 12-layer first run delays the first signal by days |
| D3 | Real data in pretraining | Synthetic only; optional fine-tune lane later | **Confirm**, with one addition: the fine-tune lane is a separate family name (PFN-FT) with its own addendum entry, never a silent change to the zero-shot entry | Keeps zero-shot claims clean |
| D4 | Where it lives | `~/workspace/pfn-from-scratch/`, private | **Confirm**, plus: checkpoints outside git with a sha256 manifest (C3) | Size |
| D5 | Relation to STRABLE prereg | Separate addendum, prereg never edited | **Confirm**, plus: addendum hashed before the sealed read (C8) | Makes "read once" provable |
| D6 | Checkpoint policy | (absent) | Every 2,000 steps + rung ends; keep last 3 + rung ends; sha256 manifest; resume test in T1 | Consumer GPU runs get interrupted |
| D7 | Context policy for large tables | (absent) | Ensemble of 8 random contexts at trained length, fold-boundary-respecting; kNN context as a logged alternative | R2 |
| D8 | Regression head | (absent) | Histogram head with 100 bins over the quantile-transformed target; required for J2 | R7 |
| D9 | Inference ensembling | (absent) | Report both single-pass and 8-way feature-permutation ensemble; the leaderboard entry uses the ensemble and says so | U4 |
| D10 | Class ceiling | (absent) | K = 10 | Matches B1 needs; J1 is binary |
| D11 | Numerics | (absent) | bf16 autocast, fused SDPA attention, gradient checkpointing on at S2 | 12 GB |
| D12 | B1 dataset list | (absent) | ≥ 15 public datasets ≤ 10k rows, frozen in the addendum | The real test of the program |
| D13 | Baseline fairness on J1 | "catboost / extratrees" | Three baselines always reported; only like-for-like and seed are gates | R9 |
| D14 | Secondary paper sources | Nature 2025 only | Also cite the ICLR 2023 PFN and TabPFN v1 papers as method sources; code of any of them stays off-limits | R13 |
| D15 | Missingness mechanism in prior | (absent) | MCAR at a sampled rate, plus MAR via one parent node in 30% of tables | U3; cheap and closer to real tables |

Items marked "Correct" or "Replace" are disagreements with the mandala and are kept as such for the owner to rule on. Nothing else in the mandala is changed by this review.

---

## 6. Order of work

1. C0 provenance map (half a day, owner diff-review).
2. C1 generator + V1, V2 (one to two days, CPU).
3. C2 at S0 + tests, then C1 V3 and V4 (one day, ≤ 2 GPU-hours).
4. C7 guards in CI (hours; do it before any dependency gets added).
5. C3 T0, T1 at S1 (one day including the resume test).
6. C4 context policy + C5 B1 harness (one to two days, CPU for baselines).
7. C3 T2 (days, measured at T0).
8. C5 dev reads, C8 addendum lock, sealed read once.
9. C6 harness entry.
10. C3 T3 only if T2's curve says so.

Mid-flight changes to any component come back to this document as an amendment, per the standing process.
