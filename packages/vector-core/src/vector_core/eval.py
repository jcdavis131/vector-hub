"""NumPy retrieval / clustering evaluation metrics.

These are the metrics the fleet's eval scoreboards report: recall@k on identity or
adjacent-period retrieval, kNN label purity@k, and cosine silhouette. All pure
NumPy so they run in CI without torch.

Convention: embeddings are compared by cosine similarity. Rows are L2-normalized
internally, so callers can pass raw embeddings.
"""

from __future__ import annotations

import numpy as np

__all__ = [
    "recall_at_k",
    "purity_at_k",
    "purity_from_neighbors",
    "silhouette_cosine",
]


def _l2_normalize(X: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    X = np.asarray(X, dtype=np.float64)
    n = np.linalg.norm(X, axis=1, keepdims=True)
    return X / np.maximum(n, eps)


def _cosine_sim(X: np.ndarray, Y: np.ndarray) -> np.ndarray:
    return _l2_normalize(X) @ _l2_normalize(Y).T


def _recall_pairs(
    embeddings: np.ndarray,
    pairs: np.ndarray,
    k: int,
    normalize: bool,
    dtype,
    eps: float,
) -> float | None:
    """Pair-based recall@k (vector-equities ``train_mtnn.recall_at_k`` semantics).

    ``pairs`` are ``(anchor_idx, target_idx)`` rows over a single embedding matrix.
    For each anchor its own row is excluded, then we check whether the target is
    among the anchor's top-k neighbours. Returns ``None`` for an empty pair set,
    matching the reference. The reference does raw dot products (no normalisation);
    pass ``normalize=True`` for cosine.
    """
    pairs = np.asarray(pairs)
    if len(pairs) == 0:
        return None
    E = np.asarray(embeddings, dtype=dtype) if dtype is not None else np.asarray(embeddings)
    if normalize:
        E = E / (np.linalg.norm(E, axis=1, keepdims=True) + eps)
    hits = 0
    for a, b in pairs:
        sims = E @ E[a]
        sims[a] = -np.inf
        top = np.argpartition(-sims, k)[:k]
        hits += int(b in top)
    return hits / len(pairs)


def _recall_query_idx(
    embeddings: np.ndarray,
    gallery: np.ndarray | None,
    query_idx: np.ndarray,
    targets: np.ndarray,
    k: int,
    normalize: bool,
    dtype,
    eps: float,
) -> float:
    """Subset-query recall@k (vector-realty ``probe_metric.recall_at_k`` semantics).

    Queries are ``embeddings[query_idx]``, the gallery is the full matrix (or a
    separate ``gallery``), and each query's own gallery column ``query_idx[i]`` is
    masked before ranking. Normalisation uses an *additive* ``eps`` (``norm + eps``)
    and operates in ``dtype`` (float32 by default) to match the reference.
    """
    Q = np.asarray(embeddings, dtype=dtype)
    C = Q if gallery is None else np.asarray(gallery, dtype=dtype)
    qi = np.asarray(query_idx)
    ti = np.asarray(targets)
    if normalize:
        q = Q[qi] / (np.linalg.norm(Q[qi], axis=1, keepdims=True) + eps)
        c = C / (np.linalg.norm(C, axis=1, keepdims=True) + eps)
    else:
        q = Q[qi]
        c = C
    S = q @ c.T
    S[np.arange(len(qi)), qi] = -np.inf
    top = np.argpartition(-S, k, axis=1)[:, :k]
    return float(np.mean([t in row for t, row in zip(ti, top, strict=False)]))


def recall_at_k(
    queries: np.ndarray,
    gallery: np.ndarray | None = None,
    targets: np.ndarray | None = None,
    k: int = 10,
    exclude_self: bool = False,
    *,
    pairs: np.ndarray | None = None,
    query_idx: np.ndarray | None = None,
    normalize: bool | None = None,
    dtype=None,
    eps: float | None = None,
) -> float | None:
    """Fraction of queries whose target index is within the top-k gallery neighbors.

    This one function expresses three retrieval conventions used across the fleet;
    the mode is selected by which keyword you pass.

    Default (query/gallery/targets) — the v0.1 behaviour, unchanged
        ``queries`` ``(nq, d)``, ``gallery`` ``(ng, d)``, ``targets`` ``(nq,)``
        giving the gallery index that is the correct match for each query. If
        queries and gallery are the same set, pass ``exclude_self=True`` to drop
        the query's own row from its ranking. Rows are cosine-compared in float64.

    ``pairs=(anchor_idx, target_idx)`` — vector-equities pair mode
        ``queries`` is a single embedding matrix; ``pairs`` are index rows. Each
        anchor's own row is excluded. Returns ``None`` for an empty pair set.
        Defaults: ``normalize=False`` (raw dot), no dtype cast, ``eps=1e-9``.

    ``query_idx`` — vector-realty subset-query mode
        ``queries`` is the embedding matrix (or query source), ``gallery`` is the
        gallery source (defaults to ``queries``), ``targets`` are the true gallery
        rows. Each query's own gallery column ``query_idx[i]`` is masked. Defaults:
        ``normalize=True`` with additive ``eps`` (``norm + eps``), ``dtype=float32``,
        ``eps=1e-9``.

    ``normalize``, ``dtype`` and ``eps`` only affect the ``pairs`` and ``query_idx``
    modes; the default mode is untouched.
    """
    if pairs is not None:
        _normalize = False if normalize is None else normalize
        _eps = 1e-9 if eps is None else eps
        return _recall_pairs(queries, pairs, k, normalize=_normalize, dtype=dtype, eps=_eps)
    if query_idx is not None:
        _normalize = True if normalize is None else normalize
        _eps = 1e-9 if eps is None else eps
        _dtype = np.float32 if dtype is None else dtype
        return _recall_query_idx(
            queries, gallery, query_idx, targets, k,
            normalize=_normalize, dtype=_dtype, eps=_eps,
        )
    if gallery is None or targets is None:
        raise ValueError("default recall_at_k mode requires gallery and targets")
    queries = np.asarray(queries, dtype=np.float64)
    gallery = np.asarray(gallery, dtype=np.float64)
    targets = np.asarray(targets).ravel()
    if queries.shape[0] != targets.shape[0]:
        raise ValueError("queries and targets length mismatch")
    if k < 1:
        raise ValueError("k must be >= 1")

    sim = _cosine_sim(queries, gallery)  # (nq, ng)
    if exclude_self:
        n = min(sim.shape[0], sim.shape[1])
        sim[np.arange(n), np.arange(n)] = -np.inf

    kk = min(k, sim.shape[1])
    # Indices of the top-kk gallery items per query.
    topk = np.argpartition(-sim, kth=kk - 1, axis=1)[:, :kk]
    hits = (topk == targets[:, None]).any(axis=1)
    return float(hits.mean())


def purity_at_k(
    embeddings: np.ndarray,
    labels: np.ndarray,
    k: int = 10,
) -> float:
    """Mean kNN label purity@k.

    For each row, look at its ``k`` nearest neighbors (excluding itself) and
    compute the fraction that share its label; average over all rows.
    """
    embeddings = np.asarray(embeddings, dtype=np.float64)
    labels = np.asarray(labels).ravel()
    n = embeddings.shape[0]
    if n != labels.shape[0]:
        raise ValueError("embeddings and labels length mismatch")
    if k < 1:
        raise ValueError("k must be >= 1")

    sim = _cosine_sim(embeddings, embeddings)
    np.fill_diagonal(sim, -np.inf)  # never a neighbor of itself
    kk = min(k, n - 1)
    if kk < 1:
        return 0.0
    topk = np.argpartition(-sim, kth=kk - 1, axis=1)[:, :kk]
    neigh_labels = labels[topk]
    same = neigh_labels == labels[:, None]
    return float(same.mean())


def purity_from_neighbors(
    neighbor_idx: np.ndarray,
    labels: np.ndarray,
    exclude_group: np.ndarray | None = None,
) -> float:
    """Mean fraction of each row's neighbours that share the row's label.

    ``neighbor_idx`` is ``(n, k)`` of precomputed neighbour row indices (self and
    any group exclusion already applied upstream). With ``exclude_group=None`` this
    is exactly vector-equities' ``eval_sector_coherence.purity_from_neighbors``::

        float((labels[neighbor_idx] == labels[:, None]).mean())

    ``exclude_group`` (an additive vector-core extension) is a per-row group id
    array; neighbours sharing the query row's group are dropped from the average
    (a pooled fraction over the kept neighbour cells). Note this masks *given*
    neighbours — it is not the same computation as vector-equities' cross-ticker
    purity, which excludes same-group rows at the kNN *selection* stage.
    """
    neighbors = np.asarray(neighbor_idx)
    labels = np.asarray(labels)
    same_label = labels[neighbors] == labels[:, None]
    if exclude_group is None:
        return float(same_label.mean())
    groups = np.asarray(exclude_group)
    keep = groups[neighbors] != groups[:, None]
    den = keep.sum()
    if den == 0:
        return 0.0
    return float((same_label & keep).sum() / den)


def silhouette_cosine(
    embeddings: np.ndarray,
    labels: np.ndarray,
    backend: str = "numpy",
) -> float:
    """Mean silhouette score using cosine distance.

    For each point: ``a`` = mean cosine distance to same-cluster points, ``b`` =
    min over other clusters of the mean cosine distance to that cluster;
    silhouette ``= (b - a) / max(a, b)``. Singletons contribute 0. Returns the
    mean over all points; range ``[-1, 1]``.

    ``backend`` selects the implementation:

    - ``"numpy"`` (default) — the pure-NumPy implementation below; the v0.1
      behaviour, unchanged, and importable without sklearn.
    - ``"sklearn"`` — delegates to ``sklearn.metrics.silhouette_score(metric=
      "cosine")``, reproducing vector-equities' ``eval_sector_coherence``. Requires
      scikit-learn (imported lazily, only on this path).
    - ``"auto"`` — use sklearn if importable, else fall back to numpy.
    """
    if backend == "auto":
        try:
            import sklearn.metrics  # noqa: F401

            backend = "sklearn"
        except ImportError:
            backend = "numpy"
    if backend == "sklearn":
        from sklearn.metrics import silhouette_score

        return float(silhouette_score(embeddings, labels, metric="cosine"))
    if backend != "numpy":
        raise ValueError(f"unknown backend {backend!r}; use 'numpy', 'sklearn', or 'auto'")

    embeddings = np.asarray(embeddings, dtype=np.float64)
    labels = np.asarray(labels).ravel()
    n = embeddings.shape[0]
    if n != labels.shape[0]:
        raise ValueError("embeddings and labels length mismatch")
    uniq = np.unique(labels)
    if uniq.size < 2:
        raise ValueError("silhouette needs at least 2 clusters")

    dist = 1.0 - _cosine_sim(embeddings, embeddings)  # cosine distance
    np.clip(dist, 0.0, 2.0, out=dist)

    scores = np.zeros(n, dtype=np.float64)
    for i in range(n):
        same = labels == labels[i]
        same[i] = False
        n_same = same.sum()
        if n_same == 0:
            scores[i] = 0.0  # singleton cluster
            continue
        a = dist[i, same].mean()
        b = np.inf
        for c in uniq:
            if c == labels[i]:
                continue
            other = labels == c
            b = min(b, dist[i, other].mean())
        denom = max(a, b)
        scores[i] = 0.0 if denom == 0 else (b - a) / denom
    return float(scores.mean())
