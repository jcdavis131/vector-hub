"""A real, reproducible multi-target run — on SYNTHETIC, in-repo data.

This example exists to demonstrate the *harness mechanics* end to end: a domain
declaring a SET of targets, each scored on its own leakage-safe temporal split by
the full baseline gauntlet, aggregated into one schema-1.1 domain report with a
verdict PER TARGET. Nothing here is a claim about a real domain or a real MTNN.

Honesty notes, on purpose:

- The data is generated from a seeded ``numpy`` RNG in this file — no external
  data, no committed real domain. The signal is planted so the baselines have
  something real to find (so the report is not all-noise), but it is synthetic.
- **No MTNN rung is supplied.** The committed report is therefore baseline-only:
  every target's ``mtnn_beats_best_baseline`` is ``null`` ("no MTNN rung
  present"). This is deliberate — the outperformance thesis is UNPROVEN and this
  harness does not invent an MTNN number to pretend otherwise. Wiring a real MTNN
  rung (precomputed embeddings/predictions) is a later data pass.
- One target (``long_horizon_return``) is left ``spec-only`` (no task wired) so a
  real report shows how a not-yet-computable target is carried through honestly.

Run::

    python examples/multitarget_synthetic/build_synthetic_multitarget.py

It rewrites ``benchmark_report.json`` next to this script.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from vector_bench import (
    DomainSpec,
    PredictionTarget,
    build_task_for_target,
    run_domain_benchmark,
    write_domain_report,
)

SEED = 7


def build_panel(seed: int = SEED):
    """Entity x period panel with genuinely forward-shifted, leakage-safe targets.

    For each (entity, period t) row the features describe period t only; every
    target is a function of period ``t+1`` outcomes, so a temporal split at a
    period cut trains strictly on the past. Returns arrays aligned row-for-row.
    """
    rng = np.random.default_rng(seed)
    n_entities, n_periods, d = 120, 10, 8
    latent = rng.standard_normal((n_entities, d))
    beta_ret = rng.standard_normal(d)
    beta_vol = rng.standard_normal(d)

    X, ret, vol, ddown, g, t = [], [], [], [], [], []
    for e in range(n_entities):
        for p in range(n_periods - 1):  # p+1 must exist for the forward targets
            feat = latent[e] + 0.4 * rng.standard_normal(d) + 0.03 * p
            drift = 0.05 * (p + 1)
            # Forward return: linear signal in features + a mild nonlinearity + noise.
            fwd_ret = feat @ beta_ret + 1.5 * np.tanh(feat[0]) + drift
            fwd_ret += 0.6 * rng.standard_normal()
            # Forward realized vol: positive, driven by a different feature mix.
            fwd_vol = np.abs(feat @ beta_vol) * 0.5 + 0.3 + 0.1 * rng.standard_normal()
            fwd_vol = abs(fwd_vol)
            # Drawdown-exceedance: more likely when forward vol is high & return low.
            score = 0.8 * fwd_vol - 0.5 * fwd_ret + 0.3 * rng.standard_normal()
            X.append(feat)
            ret.append(fwd_ret)
            vol.append(fwd_vol)
            ddown.append(score)
            g.append(e)
            t.append(p)

    X = np.asarray(X)
    ret = np.asarray(ret)
    vol = np.asarray(vol)
    ddown = np.asarray(ddown)
    # Binary label: top-third drawdown scores are exceedances (1).
    thresh = np.quantile(ddown, 2.0 / 3.0)
    ddown_flag = (ddown >= thresh).astype(float)
    return X, ret, vol, ddown_flag, np.asarray(g), np.asarray(t)


def build_spec() -> DomainSpec:
    return DomainSpec(
        domain="synthetic_markets",
        primary_task_type="prediction",
        description=(
            "Synthetic in-repo domain (seeded). Demonstrates multi-target scoring: "
            "a forward return, a forward realized volatility, and a binary "
            "drawdown-exceedance flag, each on its own temporal split."
        ),
        targets=(
            PredictionTarget(
                name="forward_return",
                kind="regression",
                horizon="next_period",
                metrics=("spearman_ic", "mae", "rmse", "r2"),
                split="temporal",
                primary_metric="spearman_ic",
                status="data-wired",
                construction="y = next-period return; features from period t only; temporal cut.",
            ),
            PredictionTarget(
                name="forward_realized_vol",
                kind="regression",
                horizon="next_period",
                metrics=("spearman_ic", "mae", "rmse", "r2"),
                split="temporal",
                primary_metric="spearman_ic",
                status="data-wired",
                construction="y = next-period realized vol; features from period t; temporal cut.",
            ),
            PredictionTarget(
                name="drawdown_exceedance",
                kind="binary_classification",
                horizon="next_period",
                metrics=("roc_auc", "spearman_ic"),
                split="temporal",
                primary_metric="roc_auc",
                status="data-wired",
                construction=(
                    "y = 1 if next-period drawdown score in top third else 0; "
                    "features from period t; temporal cut; scored by roc_auc."
                ),
            ),
            PredictionTarget(
                name="long_horizon_return",
                kind="regression",
                horizon="t+3",
                metrics=("spearman_ic", "rmse", "r2"),
                split="temporal",
                primary_metric="spearman_ic",
                status="spec-only",
                construction=(
                    "y = cumulative return to t+3; NOT wired here (demonstrates spec-only)."
                ),
            ),
        ),
    )


def main() -> None:
    X, ret, vol, ddown_flag, g, t = build_panel()
    spec = build_spec()
    cut = 6  # train on periods < 6, test on periods >= 6 (strictly future)
    tasks = {
        "forward_return": build_task_for_target(
            spec.target("forward_return"), spec.domain, X, ret,
            group_key=g, time_key=t, time_cut=cut, seed=SEED,
        ),
        "forward_realized_vol": build_task_for_target(
            spec.target("forward_realized_vol"), spec.domain, X, vol,
            group_key=g, time_key=t, time_cut=cut, seed=SEED,
        ),
        "drawdown_exceedance": build_task_for_target(
            spec.target("drawdown_exceedance"), spec.domain, X, ddown_flag,
            group_key=g, time_key=t, time_cut=cut, seed=SEED,
        ),
        # "long_horizon_return" intentionally omitted -> spec-only in the report.
    }

    # No MTNN rung: the committed report is honestly baseline-only.
    dsc = run_domain_benchmark(spec, tasks)
    dsc.notes["provenance"] = (
        "synthetic seeded data generated in build_synthetic_multitarget.py; "
        "no MTNN rung supplied (baseline-only); thesis UNPROVEN pending real runs"
    )
    out = Path(__file__).with_name("benchmark_report.json")
    write_domain_report(dsc, out)
    print(dsc.aggregate["headline"])
    for ts in dsc.targets:
        line = f"  {ts.target_name:24s} status={ts.status}"
        if ts.scorecard is not None:
            v = ts.scorecard.verdicts.get(ts.primary_metric)
            best = v.best_method if v else "?"
            val = None if v is None else v.best_baseline_value
            line += f"  best={best} ({ts.primary_metric}={val:.4f})" if val is not None else ""
        print(line)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
