# vector-bench

An **honest outperformance benchmark harness** for the vector-\* model fleet.

## The thesis it serves

> A flexible multi-task neural net (MTNN) outperforms strong per-task baselines
> across domains, on retrieval **and** prediction.

vector-bench exists to test that claim **honestly**. It trains a ladder of strong
per-task baselines from scratch on every task, scores them alongside the MTNN,
and reports — per metric — where the MTNN wins **and where a simple baseline
wins**. A domain being simple enough that `RawCosine` or `Ridge` already solves it
is a *finding*, not a failure of the harness. The scorecard never hides a loss.

This is the discipline the fleet already practices (see vector-realty's review,
reproduced below): a bar that is too low makes a model look good for the wrong
reason. vector-bench makes the bar explicit and the verdict falsifiable.

## The baseline ladder

Every rung is trained **from scratch per run** (no leaked global state) and pinned
by a seed. The floors (`RandomFloor`, `DummyMean`) let you read a small absolute
number as "near chance" vs "real signal".

**Retrieval** (`task_type="retrieval"`, ranked by cosine over per-row vectors):

| rung | what it tests |
|---|---|
| `RandomFloor` | chance floor (deterministic random vectors) |
| `RawCosine` | cosine on raw features — the "do nothing" rung |
| `PCACosine(n)` | is a linear subspace all you need? |
| `LearnedLinearMap` | supervised linear metric map (`ridge` closed-form, or `infonce` via autograd), then cosine |
| `MTNNRung` | the model under test |

**Prediction** (`task_type="prediction"`):

| rung | what it tests |
|---|---|
| `DummyMean` / `Persistence` | chance / naive-forecast floors |
| `Ridge`, `PCARidge` | linear signal |
| `KNNRegressor` | local structure |
| `HistGradientBoosting` | nonlinear tabular signal |
| `MLPRegressor` | a plain neural net |
| `MTNNRung` | the model under test |

`MTNNRung` has two modes:

- **precomputed** — pass `embeddings=` (retrieval) or `predictions=` (prediction).
  This is how **operator-GPU outputs slot in**: train the MTNN wherever the GPUs
  are, drop the resulting vectors/predictions into the rung, and it is scored on
  the exact same split and metrics as every baseline. No torch needed.
- **train** (`MTNNRung(train=True)`) — train a small vector-core MTNN on CPU
  (torch, lazily imported and optional). For small domains only.

## The honest scorecard

`run_benchmark(task)` returns a `Scorecard`. For each metric it computes the
ranking, the **best non-MTNN baseline**, the MTNN's value, the signed delta
(**positive ⇒ MTNN better**, direction-aware so "lower RMSE is better" is handled),
and the boolean `mtnn_beats_best_baseline`. `write_report` serializes it to a
versioned `benchmark_report.json` (schema `1.0`) laid out so a dashboard can
render a method × metric grid with the MTNN delta highlighted green/red.

```python
from vector_bench import BenchmarkTask, run_benchmark, write_report

task = BenchmarkTask(
    name="my_domain_prediction", domain="my_domain",
    X=X, y=y, task_type="prediction",
    metrics=["spearman_ic", "rmse", "r2"], split="temporal", time_key=t,
)
sc = run_benchmark(task)                       # trains the whole ladder from scratch
write_report(sc, "benchmark_report.json")
print(sc.summary["headline"])                  # e.g. "MTNN wins 2/3 judged metric(s)…"
```

## Defining a task for a domain

A `BenchmarkTask` (see `tasks.py`) carries the data and a **leakage-safe split
policy** — the part that makes a benchmark trustworthy:

- `split="random"` — seeded shuffle (i.i.d. rows).
- `split="temporal"` — train strictly on the past, test strictly on the future
  (`time_key` + `time_cut`). No future row is visible at fit time.
- `split="group"` — no entity (economy, ticker, player) in both train and test.

For **retrieval**, supply identity `pairs` `(anchor_idx, target_idx)` — the helper
`build_adjacent_period_pairs(group_key, time_key)` builds the fleet's canonical
"find the same entity's adjacent period" pairs — and/or `labels` for
purity/silhouette. The split induces train pairs (fit) vs test pairs (score); the
gallery is always the full row set.

For **prediction**, supply `y` and any of
`spearman_ic` / `mae` / `rmse` / `r2` / `roc_auc`.

## How operator-GPU MTNN outputs plug in

1. Build the `BenchmarkTask` for the domain (features, pairs/targets, split).
2. Train the MTNN on the operator's GPUs, producing per-row embeddings
   (retrieval) or predictions (prediction) **for the same rows, in the same
   order**.
3. `run_benchmark(task, mtnn=MTNNRung(embeddings=E))` (or `predictions=p`). The
   rung is scored on the identical split and metrics as the baselines, and the
   scorecard reports the honest delta.

If the task already carries `task.embeddings`, `run_benchmark` builds the retrieval
MTNN rung automatically.

## Real first run: vector-realty (`examples/realty/`)

`examples/realty/build_realty_task.py` points the harness at a real domain,
**read-only**, reconstructing the 18-d masked z-scored feature matrix from
vector-realty's *committed* raw snapshot (the exact `build_features.py`
construction) and pairing it with the *committed* 32-d MTNN embeddings. Task:
given one year of a country's property market, retrieve the **same country's next
year** among all country-years; temporal split at 2015; full-gallery candidate
pool. (No realty data is copied into this repo — only the script and the report.)

The committed `examples/realty/benchmark_report.json` result (recall@k):

| method | recall@1 | recall@5 | recall@10 |
|---|---|---|---|
| raw_cosine | 0.271 | 0.566 | **0.654** |
| learned_linear_map(ridge) | 0.300 | 0.588 | 0.660 |
| learned_linear_map(infonce) | **0.432** | **0.764** | **0.849** |
| mtnn (shipped 32-d) | 0.365 | 0.757 | 0.849 |

**Verdict: a correct-gradient learned linear map matches or beats the shipped
MTNN at every k.** This reproduces vector-realty's own adversarial-review finding
— that realty's hand-written probe gradient undertrained the linear bar, and a
correctly-differentiated linear map (~0.85 recall@10) clears the MTNN's fair
5-seed mean (0.8281) — straight through the harness. `raw_cosine = 0.6537`
matches realty's reported raw cosine exactly, the control proving the
reconstructed matrix is identical. The MTNN is not the winner here, and
vector-bench says so out loud. That is the point.

To reproduce (needs a vector-realty checkout and, for the `infonce` rung, torch):

```bash
python examples/realty/build_realty_task.py --realty-root /path/to/vector-realty
```

## Install

```bash
pip install "vector-bench[sklearn] @ \
  git+https://github.com/jcdavis131/vector-hub.git#subdirectory=packages/vector-bench"
```

`vector-core` is pulled in as a git dependency. `scikit-learn` powers most of the
ladder (install the `sklearn` extra). `torch` is only needed to *train* an MTNN
rung or run the `infonce` learned-linear map (the `torch` extra); importing
`vector_bench` never imports torch.

## Layout

```
src/vector_bench/
  tasks.py       BenchmarkTask + leakage-safe splits (random/temporal/group)
  baselines.py   the ladder (retrieval + prediction rungs, MTNNRung)
  metrics.py     retrieval (recall@k, purity@k, silhouette) + prediction (IC/MAE/RMSE/R2/AUC)
  runner.py      run_benchmark -> Scorecard (ranking, best baseline, MTNN delta, verdict)
  report.py      Scorecard -> versioned benchmark_report.json
examples/realty/ real read-only run against vector-realty + its committed report
tests/           deterministic CPU pytest (prediction, retrieval, verdict logic)
```
