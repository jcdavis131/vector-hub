"""The runner: train the whole ladder, score it, and judge it honestly.

``run_benchmark(task)`` trains every applicable rung FROM SCRATCH on the task's
leakage-safe split, evaluates each on the task's metrics, ranks the methods per
metric, and — the honest part — computes the MTNN's delta against the *best
non-MTNN baseline* for each metric and records whether it actually won.

Nothing is hidden. A rung that errors or is skipped (e.g. sklearn missing) is
recorded with its status, not dropped. A metric the MTNN loses is reported as a
loss with the exact margin. "This domain is simple and the baseline wins" is a
first-class result of this function, not a failure of it.
"""

from __future__ import annotations

import time
from collections.abc import Mapping
from dataclasses import dataclass, field

from .baselines import (
    MTNNRung,
    PredictionBaseline,
    RetrievalBaseline,
    default_prediction_ladder,
    default_retrieval_ladder,
)
from .metrics import (
    metric_higher_is_better,
    prediction_metrics,
    retrieval_metrics,
)
from .tasks import BenchmarkTask, DomainSpec

__all__ = [
    "MethodResult",
    "MetricVerdict",
    "Scorecard",
    "TargetScorecard",
    "DomainScorecard",
    "run_benchmark",
    "run_domain_benchmark",
    "compute_metric_verdict",
]


@dataclass
class MethodResult:
    """One rung's outcome: its metric values and whether it ran cleanly."""

    name: str
    kind: str  # "retrieval" | "prediction"
    is_mtnn: bool
    status: str  # "ok" | "skipped" | "error"
    metrics: dict[str, float] = field(default_factory=dict)
    note: str = ""


@dataclass
class MetricVerdict:
    """Per-metric ranking + the MTNN-vs-best-baseline judgment."""

    metric: str
    higher_is_better: bool
    ranking: list[tuple[str, float]]
    best_method: str | None
    best_baseline: str | None
    best_baseline_value: float | None
    mtnn_value: float | None
    mtnn_delta: float | None  # positive => MTNN better (direction-adjusted)
    mtnn_beats_best_baseline: bool | None


@dataclass
class Scorecard:
    """The full, serializable result of one benchmark run."""

    domain: str
    task: str
    task_type: str
    split: str
    seed: int
    k_values: tuple[int, ...]
    methods: list[MethodResult]
    verdicts: dict[str, MetricVerdict]
    summary: dict[str, object]
    notes: dict[str, str] = field(default_factory=dict)


def compute_metric_verdict(
    metric: str,
    values: dict[str, float],
    is_mtnn: dict[str, bool],
) -> MetricVerdict:
    """Rank methods on one metric and judge the MTNN against the best baseline.

    Pure function of the numbers — this is what the verdict test pins directly.
    NaN values are dropped from ranking (an undefined metric is not a rank).
    """
    higher = metric_higher_is_better(metric)
    valid = {n: float(v) for n, v in values.items() if v == v}  # drop NaN
    ranking = sorted(valid.items(), key=lambda kv: kv[1], reverse=higher)
    best_method = ranking[0][0] if ranking else None

    baselines = {n: v for n, v in valid.items() if not is_mtnn.get(n, False)}
    mtnns = {n: v for n, v in valid.items() if is_mtnn.get(n, False)}

    best_baseline = None
    best_baseline_value = None
    if baselines:
        best_baseline = (max if higher else min)(baselines, key=baselines.get)
        best_baseline_value = baselines[best_baseline]

    mtnn_value = next(iter(mtnns.values())) if mtnns else None

    delta = None
    beats = None
    if mtnn_value is not None and best_baseline_value is not None:
        raw = mtnn_value - best_baseline_value
        delta = raw if higher else -raw  # positive => MTNN better
        beats = delta > 0.0

    return MetricVerdict(
        metric=metric,
        higher_is_better=higher,
        ranking=ranking,
        best_method=best_method,
        best_baseline=best_baseline,
        best_baseline_value=best_baseline_value,
        mtnn_value=mtnn_value,
        mtnn_delta=delta,
        mtnn_beats_best_baseline=beats,
    )


def _expand_metric_names(task: BenchmarkTask) -> list[str]:
    """Concrete metric column names (e.g. 'recall' -> recall@1/5/10)."""
    names: list[str] = []
    for m in task.metrics:
        if task.task_type == "retrieval" and m in ("recall", "purity"):
            names.extend(f"{m}@{k}" for k in task.k_values)
        else:
            names.append(m)
    return names


def _run_prediction(task, split, ladder):
    results: list[MethodResult] = []
    Xtr, Xte = task.X[split.train_idx], task.X[split.test_idx]
    ytr, yte = task.y[split.train_idx], task.y[split.test_idx]
    ctx_fit = {}
    ctx_pred = {}
    if task.group_key is not None:
        ctx_fit["train_groups"] = task.group_key[split.train_idx]
        ctx_pred["test_groups"] = task.group_key[split.test_idx]
    if task.time_key is not None:
        ctx_fit["train_times"] = task.time_key[split.train_idx]
    for est in ladder:
        try:
            est.fit(Xtr, ytr, **ctx_fit)
            yhat = est.predict(Xte, **ctx_pred)
            mvals = prediction_metrics(yte, yhat, task.metrics)
            results.append(
                MethodResult(est.name, "prediction", est.is_mtnn, "ok", mvals)
            )
        except ImportError as e:
            results.append(
                MethodResult(est.name, "prediction", est.is_mtnn, "skipped", {}, str(e))
            )
        except Exception as e:  # noqa: BLE001 - record, never hide
            results.append(
                MethodResult(est.name, "prediction", est.is_mtnn, "error", {}, repr(e))
            )
    return results


def _run_retrieval(task, split, ladder):
    results: list[MethodResult] = []
    train_pairs = split.train_pairs(task.pairs) if task.pairs is not None else None
    test_pairs = split.test_pairs(task.pairs) if task.pairs is not None else None
    for est in ladder:
        try:
            est.fit(task.X, train_idx=split.train_idx, train_pairs=train_pairs)
            E = est.embed(task.X)
            mvals = retrieval_metrics(
                E,
                task.metrics,
                task.k_values,
                eval_pairs=test_pairs,
                labels=task.labels,
            )
            results.append(
                MethodResult(est.name, "retrieval", est.is_mtnn, "ok", mvals)
            )
        except ImportError as e:
            results.append(
                MethodResult(est.name, "retrieval", est.is_mtnn, "skipped", {}, str(e))
            )
        except Exception as e:  # noqa: BLE001 - record, never hide
            results.append(
                MethodResult(est.name, "retrieval", est.is_mtnn, "error", {}, repr(e))
            )
    return results


def run_benchmark(
    task: BenchmarkTask,
    mtnn: RetrievalBaseline | PredictionBaseline | None = None,
    ladder: list | None = None,
) -> Scorecard:
    """Run the full ladder on ``task`` and return an honest :class:`Scorecard`.

    ``mtnn`` is the MTNN rung under test. If not given and the task carries
    precomputed ``embeddings``, an :class:`~vector_bench.baselines.MTNNRung` is
    built from them automatically (retrieval). ``ladder`` overrides the default
    baseline ladder for the task type. The MTNN rung is always appended last so
    it appears alongside — never in place of — the baselines.
    """
    split = task.make_split()

    if ladder is None:
        ladder = (
            default_prediction_ladder(task.seed)
            if task.task_type == "prediction"
            else default_retrieval_ladder(task.seed)
        )
    else:
        ladder = list(ladder)

    if mtnn is None and task.task_type == "retrieval" and task.embeddings is not None:
        mtnn = MTNNRung(embeddings=task.embeddings)
    if mtnn is not None:
        ladder = [*ladder, mtnn]

    if task.task_type == "prediction":
        results = _run_prediction(task, split, ladder)
    else:
        results = _run_retrieval(task, split, ladder)

    # Per-metric verdicts across all methods that produced that metric.
    metric_names = _expand_metric_names(task)
    is_mtnn = {r.name: r.is_mtnn for r in results}
    verdicts: dict[str, MetricVerdict] = {}
    for m in metric_names:
        values = {r.name: r.metrics[m] for r in results if m in r.metrics}
        if values:
            verdicts[m] = compute_metric_verdict(m, values, is_mtnn)

    won = sum(1 for v in verdicts.values() if v.mtnn_beats_best_baseline is True)
    lost = sum(1 for v in verdicts.values() if v.mtnn_beats_best_baseline is False)
    judged = won + lost
    if judged == 0:
        headline = "no MTNN rung present — baseline ladder only"
    elif won == judged:
        headline = f"MTNN wins all {judged} judged metric(s)"
    elif won == 0:
        headline = f"baseline wins all {judged} judged metric(s) — this domain is simple"
    else:
        headline = f"MTNN wins {won}/{judged} judged metric(s); baseline wins the rest"

    summary = {
        "metrics_judged": judged,
        "mtnn_wins": won,
        "baseline_wins": lost,
        "headline": headline,
        "built": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "n_train": int(len(split.train_idx)),
        "n_test": int(len(split.test_idx)),
    }

    return Scorecard(
        domain=task.domain,
        task=task.name,
        task_type=task.task_type,
        split=task.split,
        seed=task.seed,
        k_values=task.k_values,
        methods=results,
        verdicts=verdicts,
        summary=summary,
        notes=dict(task.notes),
    )


# --------------------------------------------------------------------------- #
# Multi-target: one scorecard per (domain, target), aggregated per domain
# --------------------------------------------------------------------------- #
@dataclass
class TargetScorecard:
    """One target's outcome inside a domain run.

    ``status`` is the *runtime* state of this target in this run:

    - ``"scored"`` — a task was supplied and the ladder ran; ``scorecard`` is set.
    - ``"spec-only"`` — no data/task was wired for the target; nothing is
      fabricated, ``scorecard`` is ``None``.
    - ``"error"`` — a task was supplied but the run raised; ``note`` has the repr.

    The per-target MTNN verdict lives in ``scorecard.verdicts[primary_metric]`` —
    the aggregate reads exactly that, so the MTNN's advantage is reportable
    target-by-target, never collapsed to one domain number.
    """

    target_name: str
    kind: str
    horizon: str
    split: str
    primary_metric: str
    status: str
    scorecard: Scorecard | None = None
    note: str = ""


@dataclass
class DomainScorecard:
    """A domain's full multi-target result: one entry per declared target."""

    domain: str
    primary_task_type: str
    description: str
    targets: list[TargetScorecard]
    aggregate: dict[str, object]
    notes: dict[str, str] = field(default_factory=dict)


def _primary_verdict(ts: TargetScorecard) -> bool | None:
    """The MTNN-beats-best-baseline verdict on the target's primary metric.

    ``None`` when the target was not scored, the primary metric is absent, or no
    MTNN rung was present (so there is nothing to judge) — the aggregate counts
    those as unjudged rather than as a baseline win, keeping the tally honest.
    """
    if ts.scorecard is None:
        return None
    v = ts.scorecard.verdicts.get(ts.primary_metric)
    return None if v is None else v.mtnn_beats_best_baseline


def run_domain_benchmark(
    spec: DomainSpec,
    tasks: Mapping[str, BenchmarkTask | None],
    mtnns: Mapping[str, RetrievalBaseline | PredictionBaseline] | None = None,
    ladder: list | None = None,
) -> DomainScorecard:
    """Run every target a domain declares and aggregate per-target verdicts.

    ``tasks`` maps ``target.name -> BenchmarkTask`` (data-wired) or ``None``
    (spec-only, no data yet). ``mtnns`` optionally maps ``target.name -> MTNN
    rung`` so the thesis is tested per target. Each scored target runs the FULL
    applicable baseline gauntlet plus its MTNN rung via :func:`run_benchmark`, and
    emits its own ``beats_best_baseline`` verdict — there is one verdict per
    target, never one per domain. Spec-only targets are carried through honestly.
    """
    mtnns = mtnns or {}
    target_results: list[TargetScorecard] = []
    for target in spec.targets:
        pm = target.primary_metric or target.metrics[0]
        base = dict(
            target_name=target.name,
            kind=target.kind,
            horizon=target.horizon,
            split=target.split,
            primary_metric=pm,
        )
        task = tasks.get(target.name)
        if task is None:
            target_results.append(
                TargetScorecard(**base, status="spec-only", note="no data wired")
            )
            continue
        try:
            sc = run_benchmark(task, mtnn=mtnns.get(target.name), ladder=ladder)
            target_results.append(TargetScorecard(**base, status="scored", scorecard=sc))
        except Exception as e:  # noqa: BLE001 - record, never hide
            target_results.append(TargetScorecard(**base, status="error", note=repr(e)))

    total = len(target_results)
    scored = [t for t in target_results if t.status == "scored"]
    spec_only = sum(1 for t in target_results if t.status == "spec-only")
    errored = sum(1 for t in target_results if t.status == "error")
    verdicts = {t.target_name: _primary_verdict(t) for t in scored}
    mtnn_wins = sum(1 for v in verdicts.values() if v is True)
    baseline_wins = sum(1 for v in verdicts.values() if v is False)
    judged = mtnn_wins + baseline_wins

    if total == 0:
        headline = "no targets declared for this domain"
    elif not scored:
        headline = f"0/{total} targets scored ({spec_only} spec-only) — no results yet"
    elif judged == 0:
        headline = (
            f"{len(scored)}/{total} targets scored, none judged "
            "(no MTNN rung present); baseline ladder only"
        )
    elif mtnn_wins == judged:
        headline = f"MTNN beats best baseline on all {judged} judged target(s)"
    elif mtnn_wins == 0:
        headline = f"baseline wins all {judged} judged target(s) on their primary metric"
    else:
        headline = (
            f"MTNN beats best baseline on {mtnn_wins}/{judged} judged target(s) "
            "(primary metric); baseline wins the rest"
        )

    aggregate = {
        "targets_total": total,
        "targets_scored": len(scored),
        "targets_spec_only": spec_only,
        "targets_errored": errored,
        "targets_judged": judged,
        "mtnn_target_wins": mtnn_wins,
        "baseline_target_wins": baseline_wins,
        "primary_metric_verdicts": verdicts,
        "headline": headline,
        "built": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }

    return DomainScorecard(
        domain=spec.domain,
        primary_task_type=spec.primary_task_type,
        description=spec.description,
        targets=target_results,
        aggregate=aggregate,
        notes={"transfer_probe": spec.transfer_probe} if spec.transfer_probe else {},
    )
