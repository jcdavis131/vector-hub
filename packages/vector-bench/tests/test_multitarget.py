"""Multi-target task specs, leakage-safe target splits, per-target aggregation.

Three things are pinned here:

1. **Spec construction** — the ``PredictionTarget`` / ``DomainSpec`` validation
   and the concrete per-domain registry (every fleet domain present, kinds and
   metric sets legal, spec-only vs data-wired flags honest).
2. **Leakage-safety of the new splits** — a forward-shifted target built the way
   the registry documents, run through ``build_task_for_target`` + the temporal
   split, never lets a future row into train.
3. **Per-target scorecard aggregation** — ``run_domain_benchmark`` produces one
   scorecard (and one MTNN verdict) PER TARGET, carries spec-only targets through
   without fabricating a result, and the schema-1.1 report embeds unmodified 1.0
   scorecards.
"""

from __future__ import annotations

import numpy as np
import pytest

from vector_bench import (
    DOMAIN_REPORT_SCHEMA_VERSION,
    BenchmarkTask,
    DomainSpec,
    MTNNRung,
    PredictionTarget,
    all_targets,
    build_task_for_target,
    domain_report_to_dict,
    get_domain_spec,
    list_domains,
    run_domain_benchmark,
)


# --------------------------------------------------------------------------- #
# 1. Spec construction + registry
# --------------------------------------------------------------------------- #
def test_prediction_target_validates_kind_and_metrics():
    with pytest.raises(ValueError):
        PredictionTarget(name="x", kind="classification", horizon="1y", metrics=("r2",))
    with pytest.raises(ValueError):
        # regression cannot report roc_auc
        PredictionTarget(name="x", kind="regression", horizon="1y", metrics=("roc_auc",))
    with pytest.raises(ValueError):
        # binary must report roc_auc
        PredictionTarget(
            name="x", kind="binary_classification", horizon="1y", metrics=("spearman_ic",)
        )
    with pytest.raises(ValueError):
        # primary_metric must be one of metrics
        PredictionTarget(
            name="x", kind="regression", horizon="1y", metrics=("r2",), primary_metric="mae"
        )


def test_prediction_target_primary_metric_defaults_to_first():
    t = PredictionTarget(
        name="fwd", kind="regression", horizon="1m", metrics=("spearman_ic", "rmse")
    )
    assert t.primary_metric == "spearman_ic"
    assert t.status == "spec-only"


def test_domain_spec_rejects_duplicate_targets():
    t = PredictionTarget(name="dup", kind="regression", horizon="1y", metrics=("r2",))
    with pytest.raises(ValueError):
        DomainSpec(domain="d", primary_task_type="prediction", targets=(t, t))


def test_registry_has_all_fleet_domains():
    assert set(list_domains()) == {
        "hoops",
        "gridiron",
        "equities",
        "realty",
        "pitch",
        "unified",
    }
    # Spot-check each domain's declared target names follow its real signal.
    assert {t.name for t in get_domain_spec("hoops").targets} >= {
        "next_season_per",
        "next_season_win_shares",
        "next_season_bpm",
        "next_season_pts",
        "next_season_reb",
        "next_season_ast",
    }
    assert {t.name for t in get_domain_spec("gridiron").targets} == {
        "next_game_fpts",
        "next_game_yards",
        "next_game_tds",
    }
    eq = {t.name: t for t in get_domain_spec("equities").targets}
    assert eq["drawdown_exceedance"].kind == "binary_classification"
    assert eq["forward_return"].primary_metric == "spearman_ic"
    rl = {t.name: t for t in get_domain_spec("realty").targets}
    assert rl["above_market_appreciation"].kind == "binary_classification"
    # realty stays retrieval-primary; the prediction targets are additive.
    assert get_domain_spec("realty").primary_task_type == "retrieval"
    assert get_domain_spec("pitch").primary_task_type == "retrieval"
    assert len(get_domain_spec("pitch").targets) >= 1
    # unified documents a transfer probe.
    assert get_domain_spec("unified").transfer_probe


def test_registry_targets_reflect_real_data_benchmark_status():
    # Real-data benchmark runs have validated data-wiring for hoops, gridiron,
    # equities, and pitch (each target's status line links the MERGED
    # domain-repo PR). realty's real-data run still refutes the outperformance
    # thesis, so its targets stay spec-only. unified's transfer probe was also
    # computed on real data, but its PR (vector-unified#5) is still unmerged and
    # trained partly on realty's pre-fix (XM/XW-contaminated) data, so it stays
    # spec-only too pending both fixes landing. Every target, wired or not, must
    # document its leakage-safe construction — status is never trusted without
    # one.
    data_wired_domains = {"hoops", "gridiron", "equities", "pitch"}
    spec_only_domains = {"realty", "unified"}
    assert data_wired_domains | spec_only_domains == set(list_domains())

    for domain, target in all_targets():
        assert target.status in ("spec-only", "data-wired"), (domain, target.name)
        assert target.construction, f"{domain}.{target.name} missing leakage construction"
        expected = "spec-only" if domain in spec_only_domains else "data-wired"
        assert target.status == expected, (domain, target.name, target.status)


# --------------------------------------------------------------------------- #
# 2. Leakage-safety of the new target splits
# --------------------------------------------------------------------------- #
def _panel(seed: int = 0):
    """A small entity x period panel with a genuine forward-shifted target."""
    rng = np.random.default_rng(seed)
    n_entities, n_periods, d = 40, 8, 6
    rows_X, rows_y, g, t = [], [], [], []
    latent = rng.standard_normal((n_entities, d))
    for e in range(n_entities):
        for p in range(n_periods - 1):  # need p+1 to exist for the forward target
            feat = latent[e] + 0.3 * rng.standard_normal(d) + 0.05 * p
            # y is the NEXT period's signal -> strictly forward, no leakage into feat.
            nxt = latent[e].sum() + 0.4 * (p + 1) + 0.2 * rng.standard_normal()
            rows_X.append(feat)
            rows_y.append(nxt)
            g.append(e)
            t.append(p)
    return (
        np.asarray(rows_X),
        np.asarray(rows_y),
        np.asarray(g),
        np.asarray(t),
    )


def test_temporal_target_split_has_no_future_leakage():
    X, y, g, t = _panel()
    target = PredictionTarget(
        name="next_period_signal",
        kind="regression",
        horizon="next_period",
        metrics=("spearman_ic", "rmse", "r2"),
        split="temporal",
    )
    task = build_task_for_target(
        target, "synthetic", X, y, group_key=g, time_key=t, time_cut=5
    )
    assert isinstance(task, BenchmarkTask)
    assert task.split == "temporal"
    assert task.metrics == ["spearman_ic", "rmse", "r2"]
    split = task.make_split()
    # The whole point: every train time is strictly before every test time.
    assert t[split.train_idx].max() < t[split.test_idx].min()
    assert set(split.train_idx).isdisjoint(set(split.test_idx))
    # notes carry the target provenance onto the task.
    assert task.notes["target"] == "next_period_signal"
    assert task.notes["primary_metric"] == "spearman_ic"


def test_binary_target_task_carries_binary_metrics():
    X, y, g, t = _panel()
    ybin = (y > np.median(y)).astype(float)
    target = PredictionTarget(
        name="above_median_next",
        kind="binary_classification",
        horizon="next_period",
        metrics=("roc_auc", "spearman_ic"),
        split="temporal",
    )
    task = build_task_for_target(target, "synthetic", X, ybin, time_key=t, time_cut=5)
    assert task.metrics == ["roc_auc", "spearman_ic"]
    assert set(np.unique(task.y)) <= {0.0, 1.0}


# --------------------------------------------------------------------------- #
# 3. Per-target scorecard aggregation
# --------------------------------------------------------------------------- #
def _synthetic_domain():
    return DomainSpec(
        domain="synthetic",
        primary_task_type="prediction",
        description="synthetic multi-target domain for aggregation tests",
        targets=(
            PredictionTarget(
                name="reg_a",
                kind="regression",
                horizon="next_period",
                metrics=("spearman_ic", "rmse", "r2"),
                split="temporal",
            ),
            PredictionTarget(
                name="reg_b",
                kind="regression",
                horizon="next_period",
                metrics=("spearman_ic", "rmse", "r2"),
                split="temporal",
            ),
            PredictionTarget(
                name="bin_c",
                kind="binary_classification",
                horizon="next_period",
                metrics=("roc_auc",),
                split="temporal",
            ),
            PredictionTarget(
                name="not_wired",
                kind="regression",
                horizon="next_period",
                metrics=("r2",),
                split="temporal",
            ),
        ),
    )


def _wire_tasks(spec):
    X, y, g, t = _panel()
    ybin = (y > np.median(y)).astype(float)

    def _mk(name, yy):
        return build_task_for_target(
            spec.target(name), "synthetic", X, yy, time_key=t, time_cut=5
        )

    return {
        "reg_a": _mk("reg_a", y),
        "reg_b": _mk("reg_b", y),
        "bin_c": _mk("bin_c", ybin),
        # "not_wired" intentionally absent -> spec-only at runtime.
    }


def test_per_target_scorecards_and_spec_only_carry_through():
    spec = _synthetic_domain()
    tasks = _wire_tasks(spec)
    dsc = run_domain_benchmark(spec, tasks)

    by_name = {t.target_name: t for t in dsc.targets}
    assert set(by_name) == {"reg_a", "reg_b", "bin_c", "not_wired"}
    # Three data-wired targets scored, each with its own full scorecard.
    for name in ("reg_a", "reg_b", "bin_c"):
        ts = by_name[name]
        assert ts.status == "scored"
        assert ts.scorecard is not None
        method_names = {m.name for m in ts.scorecard.methods}
        assert {"dummy_mean", "ridge", "hist_gbm"} <= method_names
    # The undwired target is spec-only, NOT fabricated.
    assert by_name["not_wired"].status == "spec-only"
    assert by_name["not_wired"].scorecard is None
    # No MTNN rung supplied -> nothing judged, honest aggregate.
    agg = dsc.aggregate
    assert agg["targets_total"] == 4
    assert agg["targets_scored"] == 3
    assert agg["targets_spec_only"] == 1
    assert agg["targets_judged"] == 0
    assert agg["mtnn_target_wins"] == 0


def test_per_target_mtnn_verdict_is_independent_per_target():
    spec = _synthetic_domain()
    tasks = _wire_tasks(spec)
    # A "perfect" precomputed MTNN for reg_a only; reg_b/bin_c get a deliberately
    # useless MTNN (constant) so the verdict must differ target-by-target.
    perfect_a = tasks["reg_a"].y[tasks["reg_a"].make_split().test_idx].copy()
    n_b = len(tasks["reg_b"].make_split().test_idx)
    n_c = len(tasks["bin_c"].make_split().test_idx)
    mtnns = {
        "reg_a": MTNNRung(predictions=perfect_a),
        "reg_b": MTNNRung(predictions=np.zeros(n_b)),
        "bin_c": MTNNRung(predictions=np.zeros(n_c)),
    }
    dsc = run_domain_benchmark(spec, tasks, mtnns=mtnns)
    verdicts = dsc.aggregate["primary_metric_verdicts"]

    # reg_a: perfect predictions -> MTNN beats best baseline on spearman_ic.
    assert verdicts["reg_a"] is True
    # reg_b: constant predictions -> spearman_ic is NaN (dropped) or a clear loss,
    # so the MTNN does not win.
    assert verdicts["reg_b"] is not True
    # bin_c: constant score -> roc_auc undefined/loss, MTNN does not win.
    assert verdicts["bin_c"] is not True
    # not_wired stays spec-only (absent from judged verdicts).
    assert "not_wired" not in verdicts
    assert dsc.aggregate["mtnn_target_wins"] == 1
    assert dsc.aggregate["targets_judged"] >= 1


def test_domain_report_schema_1_1_embeds_unmodified_1_0_scorecards():
    spec = _synthetic_domain()
    tasks = _wire_tasks(spec)
    dsc = run_domain_benchmark(spec, tasks)
    d = domain_report_to_dict(dsc)

    assert d["schema_version"] == DOMAIN_REPORT_SCHEMA_VERSION == "1.1"
    assert d["domain"] == "synthetic"
    assert d["primary_task_type"] == "prediction"
    assert len(d["targets"]) == 4
    entries = {e["target"]["name"]: e for e in d["targets"]}
    # Scored entries embed a full scorecard that is STILL schema 1.0 (back-compat).
    for name in ("reg_a", "reg_b", "bin_c"):
        e = entries[name]
        assert e["target"]["status"] == "scored"
        assert e["scorecard"] is not None
        assert e["scorecard"]["schema_version"] == "1.0"
        assert "methods" in e["scorecard"] and "metrics" in e["scorecard"]
    # Spec-only entry has no scorecard and says so.
    assert entries["not_wired"]["target"]["status"] == "spec-only"
    assert entries["not_wired"]["scorecard"] is None
    # Binary target's metadata is preserved through the report.
    assert entries["bin_c"]["target"]["kind"] == "binary_classification"
    assert entries["bin_c"]["target"]["primary_metric"] == "roc_auc"
