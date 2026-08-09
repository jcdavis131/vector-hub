"""Synthetic RETRIEVAL domain: planted clusters with noise dimensions.

Pins that recall@k ranks RawCosine / PCACosine well above the RandomFloor, and
that LearnedLinearMap is at least as good as RawCosine once a supervised signal
(the train pairs) exists — because the ridge metric map down-weights the noise
dimensions that raw cosine cannot ignore.
"""

from __future__ import annotations

import numpy as np

from vector_bench import BenchmarkTask, run_benchmark


def _make_task(seed: int = 0) -> BenchmarkTask:
    rng = np.random.default_rng(seed)
    n_clusters = 18
    per = 18
    d_signal = 8
    d_noise = 6
    centers = rng.standard_normal((n_clusters, d_signal)) * 5.0

    X_signal, labels = [], []
    for c in range(n_clusters):
        X_signal.append(centers[c] + 0.6 * rng.standard_normal((per, d_signal)))
        labels.extend([c] * per)
    X_signal = np.vstack(X_signal)
    labels = np.array(labels)
    n = X_signal.shape[0]
    # Pure-noise dimensions that carry no cluster information — the thing a
    # learned linear map should learn to suppress.
    X_noise = 2.5 * rng.standard_normal((n, d_noise))
    X = np.hstack([X_signal, X_noise])

    # Identity-style retrieval pairs: each point paired to two same-cluster peers.
    pairs = []
    for i in range(n):
        peers = np.where(labels == labels[i])[0]
        peers = peers[peers != i]
        for j in rng.choice(peers, size=2, replace=False):
            pairs.append((i, int(j)))
    pairs = np.array(pairs, dtype=np.int64)

    return BenchmarkTask(
        name="synthetic_retrieval",
        domain="synthetic",
        X=X,
        pairs=pairs,
        labels=labels,
        task_type="retrieval",
        metrics=["recall", "purity"],
        split="random",
        seed=seed,
        k_values=(1, 5, 10),
    )


def _metric(sc, method, m):
    for r in sc.methods:
        if r.name == method:
            return r.metrics.get(m)
    raise AssertionError(f"method {method} not found")


def test_structure_beats_random_floor():
    sc = run_benchmark(_make_task())
    assert all(r.status == "ok" for r in sc.methods), [
        (r.name, r.status, r.note) for r in sc.methods
    ]
    floor = _metric(sc, "random_floor", "recall@10")
    raw = _metric(sc, "raw_cosine", "recall@10")
    pca = _metric(sc, "pca_cosine(n=16)", "recall@10")
    assert raw > floor + 0.3
    assert pca > floor + 0.3
    assert floor < 0.2  # random is near chance


def test_learned_map_at_least_matches_raw_when_signal_exists():
    sc = run_benchmark(_make_task())
    raw = _metric(sc, "raw_cosine", "recall@10")
    learned = _metric(sc, "learned_linear_map(ridge)", "recall@10")
    # With true supervision and noise dims present, the learned map should not
    # lose to raw cosine, and typically improves on it.
    assert learned >= raw - 1e-9


def test_verdict_headline_no_mtnn():
    sc = run_benchmark(_make_task())
    # No MTNN rung was supplied -> summary says baseline-only, no false victory.
    assert sc.summary["metrics_judged"] == 0
    assert "baseline ladder only" in sc.summary["headline"]
