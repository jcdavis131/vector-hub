"""Bit-identical parity: vector_core.losses torch superset vs vendored references.

Torch-gated (skips cleanly without torch). Checks:
  - info_nce_torch defaults still reproduce the v0.1 loss exactly.
  - info_nce_torch(symmetric + hard_boost) == vector-equities train_mtnn.info_nce.
  - temporal_info_nce == vector-equities train_career_mtnn.temporal_info_nce.
All at max abs diff 0.0 (exact ints for the returned counts).
"""

from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")

import _ref_equities as eq  # noqa: E402
import torch.nn.functional as F  # noqa: E402

from vector_core.losses import info_nce_torch, temporal_info_nce  # noqa: E402


def test_info_nce_defaults_reproduce_v01():
    torch.manual_seed(0)
    a = torch.randn(24, 16)
    p = torch.randn(24, 16)
    # v0.1 body, inline
    an = F.normalize(a, dim=1)
    pn = F.normalize(p, dim=1)
    logits = an @ pn.T / 0.07
    targets = torch.arange(24)
    v01 = F.cross_entropy(logits, targets)

    mine = info_nce_torch(a, p, temperature=0.07)
    assert (mine - v01).abs().item() == 0.0


def test_info_nce_symmetric_hardboost_parity_equities():
    torch.manual_seed(1)
    b, d = 32, 20
    za = torch.randn(b, d)
    zb = torch.randn(b, d)
    pos_a = torch.randint(0, 5, (b,))
    pos_b = torch.randint(0, 5, (b,))

    ref = eq.info_nce(za, zb, temp=0.08, pos_a=pos_a, pos_b=pos_b, hard_boost=0.2)
    mine = info_nce_torch(
        za, zb, temperature=0.08, normalize=False, symmetric=True,
        hard_boost=0.2, pos_a=pos_a, pos_b=pos_b,
    )
    assert (mine - ref).abs().item() == 0.0


def test_info_nce_symmetric_without_hardboost_parity_equities():
    torch.manual_seed(2)
    za = torch.randn(16, 12)
    zb = torch.randn(16, 12)
    ref = eq.info_nce(za, zb, temp=0.08)  # hard_boost=0.0 -> no miner
    mine = info_nce_torch(za, zb, temperature=0.08, normalize=False, symmetric=True)
    assert (mine - ref).abs().item() == 0.0


def test_temporal_info_nce_parity_equities():
    torch.manual_seed(3)
    B, L, D = 4, 5, 8
    c_seq = F.normalize(torch.randn(B, L, D), dim=-1)
    valid_mask = torch.rand(B, L) > 0.2  # mostly valid, some gaps
    valid_mask[:, 0] = True  # guarantee some adjacency
    valid_mask[:, 1] = True
    sector_ids = torch.tensor([0, 1, 0, 1])  # shared sectors across tickers

    ref_loss, ref_na, ref_fc = eq.temporal_info_nce(
        c_seq, valid_mask, sector_ids, temp=0.08, hard_boost=0.3
    )
    mine_loss, mine_na, mine_fc = temporal_info_nce(
        c_seq, valid_mask, sector_ids, temp=0.08, hard_boost=0.3
    )
    assert mine_na == ref_na
    assert mine_fc == ref_fc
    assert (mine_loss - ref_loss).abs().item() == 0.0
