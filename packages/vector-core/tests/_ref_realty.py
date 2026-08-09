"""Vendored reference implementations copied verbatim from vector-realty.

Ground truth for vector-core's superset. numpy-only.

Sources:
  - recall_at_k (subset-query, self-column excluded)   pipeline/train_mtnn.py
  - recall_at_k (separate query / gallery source)       pipeline/probe_metric.py
  - masked per-column z-score                            pipeline/build_features.py
"""

from __future__ import annotations

import numpy as np


# --- pipeline/train_mtnn.py -------------------------------------------------- #
def recall_at_k_train(E, qi, ti, k=10):
    E = E / (np.linalg.norm(E, axis=1, keepdims=True) + 1e-9)
    S = E[qi] @ E.T
    S[np.arange(len(qi)), qi] = -np.inf
    top = np.argpartition(-S, k, axis=1)[:, :k]
    return float(np.mean([t in row for t, row in zip(ti, top)]))  # noqa: B905


# --- pipeline/probe_metric.py ------------------------------------------------ #
def recall_at_k_probe(Q, Cand, qi, ti, k=10):
    q = Q[qi] / (np.linalg.norm(Q[qi], axis=1, keepdims=True) + 1e-9)
    c = Cand / (np.linalg.norm(Cand, axis=1, keepdims=True) + 1e-9)
    S = q @ c.T
    S[np.arange(len(qi)), qi] = -np.inf
    top = np.argpartition(-S, k, axis=1)[:, :k]
    return float(np.mean([t in row for t, row in zip(ti, top)]))  # noqa: B905


# --- pipeline/build_features.py ---------------------------------------------- #
def masked_zscore(Xf, M):
    """The z-score block from build_features.main, verbatim.

    ``Xf`` is observed values with missing cells already set to 0 (float32),
    ``M`` is the float32 observation mask.
    """
    mu = np.array([Xf[M[:, j] > 0, j].mean() if M[:, j].sum() else 0.0
                   for j in range(Xf.shape[1])], dtype=np.float32)
    sd = np.array([Xf[M[:, j] > 0, j].std() if M[:, j].sum() > 1 else 1.0
                   for j in range(Xf.shape[1])], dtype=np.float32)
    sd[sd < 1e-6] = 1.0
    Z = ((Xf - mu) / sd) * M
    return Z
