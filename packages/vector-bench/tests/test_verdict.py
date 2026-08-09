"""Verdict logic: mtnn_beats_best_baseline computed correctly from injected numbers.

These pin the pure ranking/verdict function directly, independent of any model —
including the direction handling (higher-is-better vs lower-is-better), the
best-*non-MTNN* baseline selection, and NaN dropping.
"""

from __future__ import annotations

import math

from vector_bench import compute_metric_verdict


def test_higher_is_better_mtnn_wins():
    v = compute_metric_verdict(
        "r2",
        {"ridge": 0.50, "dummy_mean": 0.00, "mtnn": 0.70},
        {"ridge": False, "dummy_mean": False, "mtnn": True},
    )
    assert v.best_baseline == "ridge"
    assert v.best_baseline_value == 0.50
    assert v.mtnn_value == 0.70
    assert math.isclose(v.mtnn_delta, 0.20)
    assert v.mtnn_beats_best_baseline is True
    assert v.best_method == "mtnn"


def test_higher_is_better_mtnn_loses():
    v = compute_metric_verdict(
        "spearman_ic",
        {"ridge": 0.90, "mtnn": 0.60},
        {"ridge": False, "mtnn": True},
    )
    assert v.best_baseline == "ridge"
    assert math.isclose(v.mtnn_delta, -0.30)
    assert v.mtnn_beats_best_baseline is False
    assert v.best_method == "ridge"


def test_lower_is_better_direction():
    # rmse: smaller is better. MTNN with lower error should win.
    win = compute_metric_verdict(
        "rmse",
        {"ridge": 1.0, "mtnn": 0.5},
        {"ridge": False, "mtnn": True},
    )
    assert math.isclose(win.mtnn_delta, 0.5)  # positive => MTNN better
    assert win.mtnn_beats_best_baseline is True

    lose = compute_metric_verdict(
        "rmse",
        {"ridge": 0.5, "mtnn": 1.0},
        {"ridge": False, "mtnn": True},
    )
    assert math.isclose(lose.mtnn_delta, -0.5)
    assert lose.mtnn_beats_best_baseline is False


def test_best_baseline_ignores_mtnn():
    # Even if the MTNN is the overall best, the delta is vs the best *baseline*.
    v = compute_metric_verdict(
        "recall@10",
        {"raw_cosine": 0.60, "pca_cosine": 0.65, "mtnn": 0.80},
        {"raw_cosine": False, "pca_cosine": False, "mtnn": True},
    )
    assert v.best_baseline == "pca_cosine"
    assert math.isclose(v.mtnn_delta, 0.15)
    assert v.mtnn_beats_best_baseline is True


def test_nan_values_are_dropped():
    v = compute_metric_verdict(
        "roc_auc",
        {"ridge": float("nan"), "dummy_mean": 0.5, "mtnn": 0.7},
        {"ridge": False, "dummy_mean": False, "mtnn": True},
    )
    ranked_methods = [m for m, _ in v.ranking]
    assert "ridge" not in ranked_methods  # NaN dropped
    assert v.best_baseline == "dummy_mean"
    assert v.mtnn_beats_best_baseline is True


def test_no_mtnn_gives_none_verdict():
    v = compute_metric_verdict(
        "r2",
        {"ridge": 0.5, "dummy_mean": 0.0},
        {"ridge": False, "dummy_mean": False},
    )
    assert v.mtnn_value is None
    assert v.mtnn_delta is None
    assert v.mtnn_beats_best_baseline is None
