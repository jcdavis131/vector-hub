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

## Multiple prediction targets per domain

Multiple prediction targets per domain was always the vision: a player has a
next-season PER *and* a next-season win-share; a ticker has a forward return *and*
a forward volatility *and* a drawdown flag. Each is its own supervised problem
with its own leakage-safe construction and its own honest verdict. Collapsing them
into a single "does the MTNN win?" number would hide exactly the target-by-target
story the thesis lives or dies on.

A domain therefore declares a **set** of targets:

- A `PredictionTarget` (in `tasks.py`) is one target: `name`, `kind`
  (`regression` | `binary_classification`), `horizon`, a `metrics` set, a
  leakage-safe `split` policy, a `primary_metric`, a `status`
  (`data-wired` | `spec-only`), and a `construction` string documenting exactly
  how `y` is derived from the future without leaking it.
- A `DomainSpec` carries the tuple of targets plus the domain's `primary_task_type`
  (`retrieval` domains like realty/pitch keep their retrieval path untouched — the
  targets are additive).
- `registry.py` is the concrete, declarative registry — **data, not hardcoded into
  the runner**. `build_task_for_target(target, domain, X, y, ...)` turns a target +
  data into a per-target `BenchmarkTask`, carrying the target's split and metrics.

`run_domain_benchmark(spec, tasks, mtnns=...)` runs the **full applicable baseline
gauntlet + the MTNN rung for each target independently** and emits a
`beats_best_baseline` verdict **per target** — there is one verdict per target,
never one per domain. It aggregates into a `DomainScorecard`; `write_domain_report`
serializes it to a **schema `1.1`** `benchmark_report.json`.

```python
from vector_bench import get_domain_spec, build_task_for_target, run_domain_benchmark

spec = get_domain_spec("equities")
tasks = {
    "forward_return": build_task_for_target(spec.target("forward_return"),
                                            "equities", X, y_ret, time_key=t),
    # ... one task per data-wired target; omit a target to leave it spec-only
}
dsc = run_domain_benchmark(spec, tasks, mtnns={"forward_return": MTNNRung(predictions=p)})
print(dsc.aggregate["headline"])   # e.g. "MTNN beats best baseline on 1/1 judged target(s)"
```

### Schema `1.1` (additive, does not break `1.0` readers)

The single-scorecard `scorecard_to_dict` / `write_report` / the shipped
`examples/realty/benchmark_report.json` are **unchanged** — still schema `1.0`. The
multi-target document is a new, separately-named artifact at schema `1.1`: a thin
wrapper `{ schema_version, domain, primary_task_type, aggregate, targets[] }` where
each `targets[]` entry embeds an **unmodified `1.0` scorecard** under `scorecard`
(`null` for spec-only / errored targets). A `1.0` reader is unaffected; a `1.1`
reader walks `targets[].scorecard` and finds the exact `1.0` shape it already knows.

### The per-domain target registry

Following each domain's real signal. **Every real-domain target below is currently
`spec-only`** — declared with a leakage-safe construction, but the domain feature
matrices and forward-shifted labels are not committed to this repo, so nothing
fabricates a number. Data wiring is a later pass.

| domain | primary | targets | kind | status |
|---|---|---|---|---|
| **hoops** (NBA) | prediction | `next_season_per`, `next_season_win_shares`, `next_season_bpm`, `next_season_pts`, `next_season_reb`, `next_season_ast` | regression | spec-only |
| **gridiron** (NFL) | prediction | `next_game_fpts`, `next_game_yards`, `next_game_tds` | regression | spec-only |
| **equities** | prediction | `forward_return`, `forward_realized_vol` | regression | spec-only |
| | | `drawdown_exceedance` | binary | spec-only |
| **realty** | retrieval | `next_year_price_change`, `three_year_price_change` | regression | spec-only |
| | | `above_market_appreciation` | binary | spec-only |
| **pitch** (soccer) | retrieval | `next_window_minutes`, `next_window_goal_contribution` | regression | spec-only |
| **unified** | prediction | `transfer_forward_return`, `transfer_next_season_per` (transfer probe) | regression | spec-only |

**unified is the cross-domain transfer probe**: freeze the shared MTNN embedding
whose heads were trained WITHOUT the held-out domain, then fit only a fresh linear
head on the held-out domain's target using the frozen embedding as features. A win
means the shared representation transferred; the held-out domain's own leakage-safe
temporal split is reused so transfer is measured on genuinely future rows. See
`spec.transfer_probe`.

> **The outperformance thesis is UNPROVEN per target.** No real per-target MTNN run
> has been computed — all real-domain targets are `spec-only`. In realty's
> *retrieval* task the thesis is already **DISPROVEN** (a correct-gradient learned
> linear map matches/beats the shipped MTNN; see `examples/realty/`). The only
> computed multi-target report is on **synthetic in-repo data**
> (`examples/multitarget_synthetic/`), and it is deliberately **baseline-only** (no
> MTNN rung) — it proves the harness mechanics, not the thesis.

### Real run on synthetic data: `examples/multitarget_synthetic/`

`build_synthetic_multitarget.py` generates a seeded synthetic panel
(entity × period, features at `t`, targets from `t+1`), declares a `DomainSpec`
with three data-wired targets (`forward_return`, `forward_realized_vol`,
`drawdown_exceedance`) + one `spec-only` target, and runs the multi-target harness
on a temporal split — **no MTNN rung**. The committed `benchmark_report.json`
(schema `1.1`) shows the full baseline gauntlet scored per target, every
`mtnn_beats_best_baseline` honestly `null`, and the spec-only target carried
through with `scorecard: null`.

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
  tasks.py       BenchmarkTask + leakage-safe splits; PredictionTarget / DomainSpec / build_task_for_target
  registry.py    declarative per-domain prediction-target registry (hoops/gridiron/equities/realty/pitch/unified)
  baselines.py   the ladder (retrieval + prediction rungs, MTNNRung)
  metrics.py     retrieval (recall@k, purity@k, silhouette) + prediction (IC/MAE/RMSE/R2/AUC)
  runner.py      run_benchmark -> Scorecard; run_domain_benchmark -> DomainScorecard (one verdict per target)
  report.py      Scorecard -> 1.0 report; DomainScorecard -> 1.1 multi-target report
examples/realty/               real read-only retrieval run against vector-realty + its committed report
examples/multitarget_synthetic/ real multi-target run on seeded synthetic in-repo data (baseline-only, schema 1.1)
tests/           deterministic CPU pytest (prediction, retrieval, verdict logic, multi-target specs/splits/aggregation)
```
