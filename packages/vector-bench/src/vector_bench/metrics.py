"""Metrics — deterministic, seeded, honest.

Retrieval label metrics (purity@k, silhouette) delegate to :mod:`vector_core.eval`
so the harness scores on the *exact* implementation the fleet reports elsewhere.
Identity-retrieval recall@k is pairs-based with per-query anchor exclusion (query
``a`` must not retrieve its own row): that mode is being added to
``vector_core.eval.recall_at_k`` in a separate vector-core change, but is not yet
on ``main`` (which vector-bench depends on), so recall is computed here with a
small numpy implementation that follows the same cosine + anchor-exclusion +
top-k convention. When the superset lands on main this can delegate too.

Prediction metrics are pure numpy so CI needs neither scipy nor sklearn: Spearman
IC via average-rank Pearson, MAE / RMSE / R2, and a rank-based (Mann-Whitney)
ROC-AUC.

``HIGHER_IS_BETTER`` is the source of truth for ranking direction. The runner
consults it to decide which end of a metric is a win, so "lower RMSE is better"
never gets ranked upside-down.
"""

from __future__ import annotations

import numpy as np
from vector_core.eval import purity_at_k, silhouette_cosine

__all__ = [
    "HIGHER_IS_BETTER",
    "metric_higher_is_better",
    "spearman_ic",
    "mae",
    "rmse",
    "r2_score",
    "roc_auc",
    "recall_at_k_pairs",
    "prediction_metrics",
    "retrieval_metrics",
]

# Base direction per metric family. Parameterized names like "recall@10" resolve
# via metric_higher_is_better() by stripping the "@k" suffix.
HIGHER_IS_BETTER: dict[str, bool] = {
    "recall": True,
    "purity": True,
    "silhouette": True,
    "spearman_ic": True,
    "r2": True,
    "roc_auc": True,
    "mae": False,
    "rmse": False,
}


def metric_higher_is_better(metric: str) -> bool:
    """Whether a larger value of ``metric`` is better (handles ``name@k``)."""
    base = metric.split("@", 1)[0]
    if base not in HIGHER_IS_BETTER:
        raise KeyError(f"unknown metric {metric!r}")
    return HIGHER_IS_BETTER[base]


# --------------------------------------------------------------------------- #
# Prediction metrics (pure numpy)
# --------------------------------------------------------------------------- #
def _rankdata(a: np.ndarray) -> np.ndarray:
    """Average ranks with tie handling (matches scipy.stats.rankdata 'average')."""
    a = np.asarray(a, dtype=float)
    sorter = np.argsort(a, kind="mergesort")
    inv = np.empty(len(a), dtype=np.intp)
    inv[sorter] = np.arange(len(a))
    a_sorted = a[sorter]
    obs = np.r_[True, a_sorted[1:] != a_sorted[:-1]]
    dense = obs.cumsum()[inv]
    count = np.r_[np.nonzero(obs)[0], len(a)]
    return 0.5 * (count[dense] + count[dense - 1] + 1)


def _pearson(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    x = x - x.mean()
    y = y - y.mean()
    denom = np.sqrt(float((x * x).sum()) * float((y * y).sum()))
    return float((x * y).sum() / denom) if denom > 0 else 0.0


def spearman_ic(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Spearman rank correlation ("information coefficient")."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    if len(y_true) < 2:
        return float("nan")
    return _pearson(_rankdata(y_true), _rankdata(y_pred))


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(np.asarray(y_true, float) - np.asarray(y_pred, float))))


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    d = np.asarray(y_true, float) - np.asarray(y_pred, float)
    return float(np.sqrt(np.mean(d * d)))


def r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    ss_res = float(((y_true - y_pred) ** 2).sum())
    ss_tot = float(((y_true - y_true.mean()) ** 2).sum())
    return 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0


def roc_auc(y_true: np.ndarray, y_score: np.ndarray) -> float:
    """Binary ROC-AUC via the Mann-Whitney rank statistic.

    ``y_true`` must be 0/1. Returns NaN if only one class is present (undefined).
    """
    y = np.asarray(y_true, dtype=float)
    s = np.asarray(y_score, dtype=float)
    n_pos = float((y == 1).sum())
    n_neg = float((y == 0).sum())
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    ranks = _rankdata(s)
    return float((ranks[y == 1].sum() - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg))


def prediction_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    metrics: list[str],
) -> dict[str, float]:
    """Compute the requested prediction metrics on a test split."""
    out: dict[str, float] = {}
    for m in metrics:
        if m == "spearman_ic":
            out[m] = spearman_ic(y_true, y_pred)
        elif m == "mae":
            out[m] = mae(y_true, y_pred)
        elif m == "rmse":
            out[m] = rmse(y_true, y_pred)
        elif m == "r2":
            out[m] = r2_score(y_true, y_pred)
        elif m == "roc_auc":
            out[m] = roc_auc(y_true, y_pred)
        else:
            raise KeyError(f"unknown prediction metric {m!r}")
    return out


# --------------------------------------------------------------------------- #
# Retrieval metrics
# --------------------------------------------------------------------------- #
def _l2_normalize(X: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    X = np.asarray(X, dtype=np.float64)
    n = np.linalg.norm(X, axis=1, keepdims=True)
    return X / np.maximum(n, eps)


def recall_at_k_pairs(
    embeddings: np.ndarray,
    pairs: np.ndarray,
    k: int,
    normalize: bool = True,
) -> float:
    """Fraction of anchor->target pairs whose target is in the anchor's top-k.

    Cosine ranking over the full gallery ``embeddings`` with the anchor's own row
    excluded (so a row cannot retrieve itself). Mirrors the vector-* fleet's
    pairs-mode recall@k convention. Returns 0.0 for an empty pair set.
    """
    pairs = np.asarray(pairs).reshape(-1, 2)
    if len(pairs) == 0:
        return 0.0
    E = _l2_normalize(embeddings) if normalize else np.asarray(embeddings, dtype=np.float64)
    hits = 0
    kk = min(k, E.shape[0] - 1)
    for a, b in pairs:
        sims = E @ E[a]
        sims[a] = -np.inf  # never retrieve yourself
        top = np.argpartition(-sims, kk)[:kk]
        hits += int(b in top)
    return hits / len(pairs)


def retrieval_metrics(
    embeddings: np.ndarray,
    metrics: list[str],
    k_values: tuple[int, ...],
    *,
    eval_pairs: np.ndarray | None = None,
    labels: np.ndarray | None = None,
) -> dict[str, float]:
    """Compute retrieval metrics on the full gallery ``embeddings``.

    ``recall`` uses ``eval_pairs`` (the test pairs); each anchor is ranked
    against the whole gallery with its own row excluded (vector_core pairs mode).
    ``purity`` / ``silhouette`` use ``labels`` over all rows.
    """
    out: dict[str, float] = {}
    for m in metrics:
        if m == "recall":
            if eval_pairs is None or len(eval_pairs) == 0:
                for k in k_values:
                    out[f"recall@{k}"] = float("nan")
            else:
                for k in k_values:
                    out[f"recall@{k}"] = recall_at_k_pairs(embeddings, eval_pairs, k)
        elif m == "purity":
            if labels is None:
                raise ValueError("purity metric requires labels")
            for k in k_values:
                out[f"purity@{k}"] = float(purity_at_k(embeddings, labels, k=k))
        elif m == "silhouette":
            if labels is None:
                raise ValueError("silhouette metric requires labels")
            out["silhouette"] = float(silhouette_cosine(embeddings, labels))
        else:
            raise KeyError(f"unknown retrieval metric {m!r}")
    return out
