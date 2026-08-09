"""Vendored reference implementations copied verbatim from vector-equities.

These are the ground-truth functions vector-core's superset must reproduce
bit-for-bit. Kept in the test tree so parity is checked against the real source,
not a paraphrase. numpy-only at import; torch/sklearn imported lazily inside the
functions that need them so this module imports without either installed.

Sources:
  - info_nce, recall_at_k        pipeline/train_mtnn.py
  - silhouette_cosine,
    purity_from_neighbors        pipeline/eval_sector_coherence.py
  - temporal_info_nce            pipeline/train_career_mtnn.py
"""

from __future__ import annotations

import numpy as np


# --- pipeline/train_mtnn.py -------------------------------------------------- #
def info_nce(za, zb, temp=0.08, pos_a=None, pos_b=None, hard_boost=0.0):
    import torch
    import torch.nn.functional as F

    logits = za @ zb.T / temp
    if hard_boost > 0 and pos_a is not None and pos_b is not None:
        b = logits.shape[0]
        idx = torch.arange(b, device=logits.device)
        hard = (pos_a.unsqueeze(1) == pos_b.unsqueeze(0)) & (idx.unsqueeze(0) != idx.unsqueeze(1))
        logits = logits + hard.float() * hard_boost
    target = torch.arange(len(za), device=za.device)
    return 0.5 * (F.cross_entropy(logits, target) + F.cross_entropy(logits.T, target))


def recall_at_k(E, pairs, k=10):
    if len(pairs) == 0:
        return None
    sample = pairs[np.random.choice(len(pairs), min(500, len(pairs)), replace=False)] if len(pairs) > 500 else pairs  # noqa: E501
    hits = 0
    for a, b in sample:
        sims = E @ E[a]
        sims[a] = -np.inf
        top = np.argpartition(-sims, k)[:k]
        hits += int(b in top)
    return hits / len(sample)


# --- pipeline/eval_sector_coherence.py --------------------------------------- #
def purity_from_neighbors(neighbors, labels):
    """Mean fraction of neighbors sharing the query row's label."""
    return float((labels[neighbors] == labels[:, None]).mean())


def silhouette_cosine(emb, labels):
    from sklearn.metrics import silhouette_score

    return float(silhouette_score(emb, labels, metric="cosine"))


# --- pipeline/train_career_mtnn.py ------------------------------------------- #
def temporal_info_nce(c_seq, valid_mask, sector_ids, temp=0.08, hard_boost=0.3, delta_decay=3.0):
    import torch
    import torch.nn.functional as F

    B, L, _D = c_seq.shape
    device = c_seq.device
    anchors = []
    positives = []
    anchor_sector = []
    anchor_pos_index = []
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
    idx = 0
    for b in range(B):
        for seq_pos in range(L - 1):
            if valid_mask[b, seq_pos] and valid_mask[b, seq_pos + 1]:
                anchor_b.append(b)
                idx += 1

    anchor_b_t = torch.tensor(anchor_b, device=device)
    all_valid_b = torch.tensor([c[0] for c in all_valid_coords], device=device)
    sector_match = torch.tensor(anchor_sector, device=device).unsqueeze(1) == all_valid_sector.unsqueeze(0)  # noqa: E501
    diff_ticker = anchor_b_t.unsqueeze(1) != all_valid_b.unsqueeze(0)
    hard_mask = sector_match & diff_ticker
    logits = logits + hard_mask.float() * hard_boost

    target = torch.tensor(anchor_pos_index, device=device, dtype=torch.long)
    loss = F.cross_entropy(logits, target)
    return loss, len(anchors), flat_counter
