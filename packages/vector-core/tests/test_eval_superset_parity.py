"""Bit-identical parity: vector_core.eval superset vs vendored fleet references.

Every new recall_at_k mode, the sklearn silhouette backend, and
purity_from_neighbors are checked at max abs diff 0.0 against the exact
implementations copied from vector-equities / vector-realty.
"""

from __future__ import annotations

import _ref_equities as eq
import _ref_realty as rl
import numpy as np
import pytest

from vector_core.eval import purity_from_neighbors, recall_at_k, silhouette_cosine


# --------------------------------------------------------------------------- #
# recall_at_k — default (v0.1) mode is unchanged
# --------------------------------------------------------------------------- #
def test_recall_default_mode_unchanged():
    rng = np.random.default_rng(0)
    gallery = rng.normal(size=(50, 12))
    targets = rng.integers(0, 50, size=20)
    queries = gallery[targets]  # perfect matches -> recall 1.0
    assert recall_at_k(queries, gallery, targets, k=5) == 1.0
    # positional call signature still works exactly as before
    assert recall_at_k(queries, gallery, targets, 5, False) == 1.0


# --------------------------------------------------------------------------- #
# recall_at_k — pairs mode == vector-equities train_mtnn.recall_at_k
# --------------------------------------------------------------------------- #
def test_recall_pairs_mode_parity_equities():
    rng = np.random.default_rng(7)
    E = rng.normal(size=(80, 16)).astype(np.float32)
    n_pairs = 40
    a = rng.integers(0, 80, size=n_pairs)
    b = rng.integers(0, 80, size=n_pairs)
    pairs = np.stack([a, b], axis=1)

    ref = eq.recall_at_k(E, pairs, k=10)
    mine = recall_at_k(E, pairs=pairs, k=10)
    assert mine is not None and ref is not None
    assert abs(mine - ref) == 0.0

    # empty pair set -> None, matching the reference
    assert recall_at_k(E, pairs=np.zeros((0, 2), int), k=10) is None


# --------------------------------------------------------------------------- #
# recall_at_k — subset-query mode == vector-realty recall_at_k (train + probe)
# --------------------------------------------------------------------------- #
def test_recall_query_idx_parity_realty_train():
    rng = np.random.default_rng(11)
    E = rng.normal(size=(120, 24)).astype(np.float32)
    qi = rng.choice(120, size=30, replace=False)
    ti = rng.integers(0, 120, size=30)

    ref = rl.recall_at_k_train(E, qi, ti, k=10)
    mine = recall_at_k(E, query_idx=qi, targets=ti, k=10)
    assert abs(mine - ref) == 0.0


def test_recall_query_idx_parity_realty_probe_separate_gallery():
    rng = np.random.default_rng(13)
    Q = rng.normal(size=(90, 20)).astype(np.float32)
    Cand = rng.normal(size=(90, 20)).astype(np.float32)
    qi = rng.choice(90, size=25, replace=False)
    ti = rng.integers(0, 90, size=25)

    ref = rl.recall_at_k_probe(Q, Cand, qi, ti, k=10)
    mine = recall_at_k(Q, gallery=Cand, query_idx=qi, targets=ti, k=10)
    assert abs(mine - ref) == 0.0


# --------------------------------------------------------------------------- #
# purity_from_neighbors == vector-equities eval_sector_coherence
# --------------------------------------------------------------------------- #
def test_purity_from_neighbors_parity_equities():
    rng = np.random.default_rng(17)
    n, k = 60, 10
    labels = rng.integers(0, 5, size=n)
    neighbors = np.stack([rng.choice(n, size=k, replace=False) for _ in range(n)])

    ref = eq.purity_from_neighbors(neighbors, labels)
    mine = purity_from_neighbors(neighbors, labels)
    assert mine == ref  # exact float
    # string labels behave identically (exact)
    slabels = np.array([f"s{v}" for v in labels])
    assert purity_from_neighbors(neighbors, slabels) == eq.purity_from_neighbors(neighbors, slabels)


def test_purity_exclude_group_default_matches_base():
    # exclude_group=None must be identical to the base equities metric.
    rng = np.random.default_rng(19)
    n, k = 40, 8
    labels = rng.integers(0, 4, size=n)
    neighbors = np.stack([rng.choice(n, size=k, replace=False) for _ in range(n)])
    assert purity_from_neighbors(neighbors, labels, exclude_group=None) == eq.purity_from_neighbors(
        neighbors, labels
    )


# --------------------------------------------------------------------------- #
# silhouette_cosine — sklearn backend == vector-equities eval_sector_coherence
# --------------------------------------------------------------------------- #
def test_silhouette_sklearn_backend_parity_equities():
    pytest.importorskip("sklearn")
    rng = np.random.default_rng(3)
    emb = rng.normal(size=(70, 8)).astype(np.float32)
    labels = rng.integers(0, 4, size=70)

    ref = eq.silhouette_cosine(emb, labels)
    mine = silhouette_cosine(emb, labels, backend="sklearn")
    assert abs(mine - ref) == 0.0

    # "auto" resolves to sklearn when installed -> identical
    assert abs(silhouette_cosine(emb, labels, backend="auto") - ref) == 0.0


def test_silhouette_numpy_default_unchanged():
    rng = np.random.default_rng(5)
    emb = rng.normal(size=(40, 6))
    labels = rng.integers(0, 3, size=40)
    # default backend is the numpy path; explicit numpy must be identical
    assert silhouette_cosine(emb, labels) == silhouette_cosine(emb, labels, backend="numpy")
