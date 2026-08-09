"""Synthetic PREDICTION domain: y = linear(X) + nonlinear term + noise.

Pins that the ladder runs end to end, the scorecard/report schema is valid, and
the sanity ordering holds: Ridge crushes DummyMean, and HistGBM captures the
nonlinear term Ridge cannot. Also checks the MTNN delta is computed correctly for
a precomputed (perfect) MTNN rung.
"""

from __future__ import annotations

import numpy as np

from vector_bench import (
    BenchmarkTask,
    MTNNRung,
    run_benchmark,
    scorecard_to_dict,
)


def _make_task(seed: int = 0) -> BenchmarkTask:
    rng = np.random.default_rng(seed)
    n, d = 800, 8
    X = rng.standard_normal((n, d))
    w = np.array([2.0, -1.5, 0.0, 1.0, 0.0, -0.5, 0.8, 0.0])
    nonlinear = 4.0 * np.sin(3.0 * X[:, 2])  # Ridge cannot fit this; HistGBM can
    y = X @ w + nonlinear + 0.3 * rng.standard_normal(n)
    return BenchmarkTask(
        name="synthetic_prediction",
        domain="synthetic",
        X=X,
        y=y,
        task_type="prediction",
        metrics=["spearman_ic", "mae", "rmse", "r2"],
        split="random",
        seed=seed,
    )


def _metric(sc, method, m):
    for r in sc.methods:
        if r.name == method:
            return r.metrics.get(m)
    raise AssertionError(f"method {method} not found")


def test_ladder_runs_and_schema_valid():
    sc = run_benchmark(_make_task())
    names = {r.name for r in sc.methods}
    assert {"dummy_mean", "ridge", "hist_gbm"} <= names
    assert all(r.status == "ok" for r in sc.methods), [
        (r.name, r.status, r.note) for r in sc.methods
    ]
    d = scorecard_to_dict(sc)
    assert d["schema_version"] == "1.0"
    assert d["task_type"] == "prediction"
    assert set(d["metrics"]) == {"spearman_ic", "mae", "rmse", "r2"}
    for mv in d["metrics"].values():
        assert "higher_is_better" in mv
        assert "ranking" in mv and len(mv["ranking"]) >= 3


def test_ridge_beats_dummy_and_histgbm_captures_nonlinear():
    sc = run_benchmark(_make_task())
    ridge_r2 = _metric(sc, "ridge", "r2")
    dummy_r2 = _metric(sc, "dummy_mean", "r2")
    hgbm_r2 = _metric(sc, "hist_gbm", "r2")
    # Ridge explains the linear part; Dummy explains nothing (r2 ~ 0).
    assert ridge_r2 > dummy_r2 + 0.3
    assert dummy_r2 < 0.05
    # HistGBM additionally captures the sin() term Ridge is blind to.
    assert hgbm_r2 > ridge_r2


def test_mtnn_delta_computed_correctly():
    task = _make_task()
    split = task.make_split()
    # A "perfect" precomputed MTNN: predictions == the held-out truth.
    perfect = task.y[split.test_idx].copy()
    sc = run_benchmark(task, mtnn=MTNNRung(predictions=perfect))

    v = sc.verdicts["r2"]
    assert v.mtnn_value is not None and v.best_baseline_value is not None
    # r2 is higher-is-better: delta = mtnn - best_baseline, positive => MTNN wins.
    assert abs(v.mtnn_delta - (v.mtnn_value - v.best_baseline_value)) < 1e-9
    assert v.mtnn_beats_best_baseline is True
    assert v.mtnn_value > 0.999  # perfect predictions

    # rmse is lower-is-better: perfect MTNN has ~0 error, delta positive => wins.
    vr = sc.verdicts["rmse"]
    assert vr.mtnn_beats_best_baseline is True
    assert abs(vr.mtnn_delta - (vr.best_baseline_value - vr.mtnn_value)) < 1e-9
