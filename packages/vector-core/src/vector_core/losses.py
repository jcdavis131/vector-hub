"""Contrastive losses: InfoNCE and SupCon.

Two implementations of each:

- NumPy reference versions (``*_numpy``) — always importable, no torch. Useful
  for tests, sanity checks, and CPU-only eval.
- Torch versions (``*_torch``) — import torch lazily *inside* the function so the
  module (and the whole package) imports cleanly without torch installed.

Both InfoNCE and SupCon operate on L2-normalized embeddings and a temperature.
InfoNCE takes explicit (anchor, positive) pairs; SupCon takes a batch with
integer labels and treats all same-label rows as positives.
"""

from __future__ import annotations

import numpy as np

__all__ = [
    "info_nce_numpy",
    "sup_con_numpy",
    "info_nce_torch",
    "sup_con_torch",
    "temporal_info_nce",
]

# --------------------------------------------------------------------------- #
# NumPy reference implementations (always available)
# --------------------------------------------------------------------------- #


def _l2_normalize_np(X: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    X = np.asarray(X, dtype=np.float64)
    n = np.linalg.norm(X, axis=1, keepdims=True)
    return X / np.maximum(n, eps)


def info_nce_numpy(
    anchors: np.ndarray,
    positives: np.ndarray,
    temperature: float = 0.07,
    normalize: bool = True,
) -> float:
    """InfoNCE loss (NumPy reference).

    ``anchors`` and ``positives`` are ``(n, d)`` aligned rows: row ``i`` of
    positives is the positive for anchor ``i``; all other positives in the batch
    are in-batch negatives. Returns the mean cross-entropy over the batch.
    """
    A = np.asarray(anchors, dtype=np.float64)
    P = np.asarray(positives, dtype=np.float64)
    if A.shape != P.shape:
        raise ValueError("anchors and positives must have the same shape")
    if normalize:
        A = _l2_normalize_np(A)
        P = _l2_normalize_np(P)
    logits = (A @ P.T) / temperature  # (n, n)
    # log-softmax over each row; target is the diagonal.
    logits = logits - logits.max(axis=1, keepdims=True)
    log_prob = logits - np.log(np.exp(logits).sum(axis=1, keepdims=True))
    n = A.shape[0]
    return float(-np.mean(log_prob[np.arange(n), np.arange(n)]))


def sup_con_numpy(
    features: np.ndarray,
    labels: np.ndarray,
    temperature: float = 0.07,
    normalize: bool = True,
) -> float:
    """Supervised Contrastive loss (NumPy reference).

    ``features`` is ``(n, d)``; ``labels`` is ``(n,)`` integer class ids. For each
    anchor, positives are all *other* rows with the same label. Anchors with no
    same-label partner are skipped. Returns the mean loss over valid anchors.
    """
    F = np.asarray(features, dtype=np.float64)
    y = np.asarray(labels).ravel()
    if F.shape[0] != y.shape[0]:
        raise ValueError("features and labels length mismatch")
    if normalize:
        F = _l2_normalize_np(F)
    n = F.shape[0]
    sim = (F @ F.T) / temperature
    sim = sim - sim.max(axis=1, keepdims=True)
    exp = np.exp(sim)
    self_mask = np.eye(n, dtype=bool)
    exp[self_mask] = 0.0  # exclude self from the denominator
    denom = exp.sum(axis=1, keepdims=True)
    log_prob = sim - np.log(np.maximum(denom, 1e-12))

    pos_mask = (y[:, None] == y[None, :]) & ~self_mask
    losses = []
    for i in range(n):
        pos = pos_mask[i]
        n_pos = pos.sum()
        if n_pos == 0:
            continue
        losses.append(-log_prob[i, pos].mean())
    if not losses:
        return 0.0
    return float(np.mean(losses))


# --------------------------------------------------------------------------- #
# Torch implementations (torch imported lazily inside each function)
# --------------------------------------------------------------------------- #


def info_nce_torch(
    anchors,
    positives,
    temperature: float = 0.07,
    normalize: bool = True,
    symmetric: bool = False,
    hard_boost: float = 0.0,
    pos_a=None,
    pos_b=None,
):
    """InfoNCE loss (torch). Returns a scalar tensor. Requires torch installed.

    The defaults (``normalize=True``, ``symmetric=False``, ``hard_boost=0.0``)
    reproduce the v0.1 loss exactly: cross-entropy of the normalised anchor/positive
    logits against the diagonal.

    The extra knobs generalise it to vector-equities' ``train_mtnn.info_nce``:

    - ``symmetric`` — average the two directions
      ``0.5 * (CE(logits) + CE(logits.T))``.
    - ``hard_boost`` with ``pos_a``/``pos_b`` — a hard-negative miner: any
      off-diagonal pair whose ``pos_a[i] == pos_b[j]`` (same label, e.g. sector)
      gets ``hard_boost`` added to its logit. Applied only when ``hard_boost > 0``
      and both label vectors are given.

    To match vector-equities exactly, call with ``normalize=False, symmetric=True``
    (it feeds raw, pre-normalised embeddings).
    """
    import torch
    import torch.nn.functional as F

    if normalize:
        anchors = F.normalize(anchors, dim=1)
        positives = F.normalize(positives, dim=1)
    logits = anchors @ positives.T / temperature
    if hard_boost > 0 and pos_a is not None and pos_b is not None:
        b = logits.shape[0]
        idx = torch.arange(b, device=logits.device)
        hard = (pos_a.unsqueeze(1) == pos_b.unsqueeze(0)) & (idx.unsqueeze(0) != idx.unsqueeze(1))
        logits = logits + hard.float() * hard_boost
    targets = torch.arange(anchors.shape[0], device=anchors.device)
    if symmetric:
        return 0.5 * (F.cross_entropy(logits, targets) + F.cross_entropy(logits.T, targets))
    return F.cross_entropy(logits, targets)


def temporal_info_nce(
    c_seq,
    valid_mask,
    sector_ids,
    temp: float = 0.08,
    hard_boost: float = 0.3,
    delta_decay: float = 3.0,
):
    """Temporal InfoNCE over per-ticker sequences (torch).

    A faithful port of vector-equities' ``train_career_mtnn.temporal_info_nce``.
    ``c_seq`` is ``(B, L, D)`` of L2-normalised step embeddings, ``valid_mask`` is
    ``(B, L)`` bool, ``sector_ids`` is ``(B,)`` int (one sector per ticker/row).

    For every ticker, adjacent valid steps ``(l, l+1)`` form an anchor/positive
    pair; the negative pool is *every* valid step across the batch. Same-sector
    steps from a *different* ticker get ``hard_boost`` added to their logit (the
    sector hard-negative miner). Returns ``(loss, n_anchor_pairs, n_valid_steps)``,
    matching the reference's tuple contract so it is a drop-in replacement.

    ``delta_decay`` is accepted for signature compatibility but, exactly as in the
    reference, it does not weight the loss: positives are always adjacent
    (``delta == 1``) so the ``exp(-|delta|/decay)`` weighting the docstring mentions
    is a documented no-op there and here.
    """
    import torch
    import torch.nn.functional as F

    B, L, _D = c_seq.shape
    device = c_seq.device

    valid_flat_idx = -torch.ones((B, L), dtype=torch.long, device=device)
    all_valid_embs = []
    all_valid_sector = []
    all_valid_coords = []

    flat_counter = 0
    for b in range(B):
        for seq_pos in range(L):
            if valid_mask[b, seq_pos]:
                valid_flat_idx[b, seq_pos] = flat_counter
                flat_counter += 1
                all_valid_embs.append(c_seq[b, seq_pos])
                all_valid_sector.append(sector_ids[b])
                all_valid_coords.append((b, seq_pos))

    if flat_counter < 2:
        return c_seq.sum() * 0.0, 0, 0

    all_valid_embs = torch.stack(all_valid_embs)
    all_valid_sector = torch.tensor(all_valid_sector, device=device)

    anchors = []
    positives = []
    anchor_sector = []
    anchor_pos_index = []
    for b in range(B):
        for seq_pos in range(L - 1):
            if valid_mask[b, seq_pos] and valid_mask[b, seq_pos + 1]:
                anchors.append(c_seq[b, seq_pos])
                positives.append(c_seq[b, seq_pos + 1])
                anchor_sector.append(sector_ids[b])
                anchor_pos_index.append(int(valid_flat_idx[b, seq_pos + 1]))

    if len(anchors) == 0:
        return c_seq.sum() * 0.0, 0, flat_counter

    anchors = torch.stack(anchors)
    torch.stack(positives)

    logits = anchors @ all_valid_embs.T / temp

    anchor_b = []
    for b in range(B):
        for seq_pos in range(L - 1):
            if valid_mask[b, seq_pos] and valid_mask[b, seq_pos + 1]:
                anchor_b.append(b)

    anchor_b_t = torch.tensor(anchor_b, device=device)
    all_valid_b = torch.tensor([c[0] for c in all_valid_coords], device=device)
    sector_match = (
        torch.tensor(anchor_sector, device=device).unsqueeze(1) == all_valid_sector.unsqueeze(0)
    )
    diff_ticker = anchor_b_t.unsqueeze(1) != all_valid_b.unsqueeze(0)
    hard_mask = sector_match & diff_ticker
    logits = logits + hard_mask.float() * hard_boost

    target = torch.tensor(anchor_pos_index, device=device, dtype=torch.long)
    loss = F.cross_entropy(logits, target)
    return loss, len(anchors), flat_counter


def sup_con_torch(features, labels, temperature: float = 0.07, normalize: bool = True):
    """Supervised Contrastive loss (torch). Returns a scalar tensor."""
    import torch
    import torch.nn.functional as F

    if normalize:
        features = F.normalize(features, dim=1)
    n = features.shape[0]
    device = features.device
    sim = features @ features.T / temperature
    sim = sim - sim.max(dim=1, keepdim=True).values.detach()
    self_mask = torch.eye(n, dtype=torch.bool, device=device)
    exp = torch.exp(sim).masked_fill(self_mask, 0.0)
    log_prob = sim - torch.log(exp.sum(dim=1, keepdim=True).clamp_min(1e-12))

    labels = labels.view(-1)
    pos_mask = (labels[:, None] == labels[None, :]) & ~self_mask
    n_pos = pos_mask.sum(dim=1)
    valid = n_pos > 0
    if valid.sum() == 0:
        return features.sum() * 0.0
    mean_log_prob_pos = (pos_mask * log_prob).sum(dim=1)[valid] / n_pos[valid]
    return -mean_log_prob_pos.mean()
