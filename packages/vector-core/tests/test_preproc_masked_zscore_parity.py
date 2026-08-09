"""Bit-identical parity: vector_core.preproc.MaskedZScaler vs vector-realty.

The masked per-column z-score must reproduce build_features's block exactly
(max abs diff 0.0), including the degenerate branches: fully-masked columns,
single-observed columns, and constant (zero-variance) columns.
"""

from __future__ import annotations

import _ref_realty as rl
import numpy as np

from vector_core.preproc import MaskedZScaler


def _fixture():
    rng = np.random.default_rng(23)
    n, d = 50, 6
    X = rng.normal(size=(n, d)).astype(np.float32)
    M = (rng.random((n, d)) > 0.3).astype(np.float32)

    # degenerate columns to exercise every branch
    M[:, 0] = 0.0  # fully masked -> mu=0, sd=1
    M[:, 1] = 0.0
    M[0, 1] = 1.0  # single observed -> sd=1 branch
    X[:, 2] = 3.14  # constant, fully observed -> std 0 -> sd=1
    M[:, 2] = 1.0

    Xf = (X * M).astype(np.float32)  # missing cells are 0, as in build_features
    return Xf, M


def test_masked_zscore_parity_realty():
    Xf, M = _fixture()
    ref = rl.masked_zscore(Xf, M)
    mine = MaskedZScaler().fit_transform(Xf, M)

    assert mine.dtype == ref.dtype == np.float32
    assert mine.shape == ref.shape
    assert np.max(np.abs(mine - ref)) == 0.0
    assert np.array_equal(mine, ref)


def test_masked_zscore_fit_then_transform_matches_fit_transform():
    Xf, M = _fixture()
    scaler = MaskedZScaler()
    scaler.fit(Xf, M)
    assert np.array_equal(scaler.transform(Xf, M), MaskedZScaler().fit_transform(Xf, M))
