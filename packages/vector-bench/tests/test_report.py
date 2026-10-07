"""``write_report`` / ``write_domain_report`` — the disk-writing half of the
report module (``scorecard_to_dict`` / ``domain_report_to_dict`` are pinned
elsewhere, but nothing exercised the actual file I/O: parent-directory
creation, JSON round-tripping, trailing newline, and the returned ``Path``).
These are the exact functions the example scripts and any downstream
dashboard-generation step call to produce ``benchmark_report.json``, so a
silent regression here (e.g. a bad path join, wrong encoding, or content that
doesn't match the in-memory dict) would only show up once something tried to
read the file back.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from vector_bench import (
    BenchmarkTask,
    DomainSpec,
    PredictionTarget,
    build_task_for_target,
    domain_report_to_dict,
    run_benchmark,
    run_domain_benchmark,
    scorecard_to_dict,
    write_domain_report,
    write_report,
)


def _make_task(seed: int = 0) -> BenchmarkTask:
    rng = np.random.default_rng(seed)
    n, d = 200, 5
    X = rng.standard_normal((n, d))
    y = X[:, 0] - 0.5 * X[:, 1] + 0.1 * rng.standard_normal(n)
    return BenchmarkTask(
        name="synthetic_report",
        domain="synthetic",
        X=X,
        y=y,
        task_type="prediction",
        metrics=["spearman_ic", "rmse", "r2"],
        split="random",
        seed=seed,
    )


def test_write_report_creates_parents_and_round_trips(tmp_path):
    sc = run_benchmark(_make_task())
    target = tmp_path / "nested" / "sub" / "benchmark_report.json"
    assert not target.parent.exists()

    out = write_report(sc, target)

    assert out == target
    assert target.is_file()
    text = target.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert json.loads(text) == scorecard_to_dict(sc)


def test_write_report_accepts_str_path_and_overwrites(tmp_path):
    sc = run_benchmark(_make_task())
    target = tmp_path / "benchmark_report.json"
    target.write_text("stale content", encoding="utf-8")

    out = write_report(sc, str(target))

    assert isinstance(out, Path)
    assert out == target
    assert json.loads(target.read_text(encoding="utf-8")) == scorecard_to_dict(sc)


def _domain_spec_and_task():
    spec = DomainSpec(
        domain="synthetic_report_domain",
        primary_task_type="prediction",
        targets=(
            PredictionTarget(
                name="fwd",
                kind="regression",
                horizon="next_period",
                metrics=("spearman_ic", "rmse", "r2"),
                split="temporal",
            ),
        ),
    )
    rng = np.random.default_rng(1)
    n_entities, n_periods, d = 20, 6, 4
    rows_X, rows_y, t = [], [], []
    latent = rng.standard_normal((n_entities, d))
    for e in range(n_entities):
        for p in range(n_periods):
            rows_X.append(latent[e] + 0.2 * rng.standard_normal(d))
            rows_y.append(latent[e].sum() + 0.1 * p + 0.1 * rng.standard_normal())
            t.append(p)
    X = np.asarray(rows_X)
    y = np.asarray(rows_y)
    time_key = np.asarray(t)
    task = build_task_for_target(
        spec.target("fwd"), spec.domain, X, y, time_key=time_key, time_cut=3
    )
    return spec, {"fwd": task}


def test_write_domain_report_creates_parents_and_round_trips(tmp_path):
    spec, tasks = _domain_spec_and_task()
    dsc = run_domain_benchmark(spec, tasks)
    target = tmp_path / "domain" / "nested" / "benchmark_report.json"
    assert not target.parent.exists()

    out = write_domain_report(dsc, target)

    assert out == target
    assert target.is_file()
    text = target.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert json.loads(text) == domain_report_to_dict(dsc)
