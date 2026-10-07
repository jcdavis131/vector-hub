"""The baseline ladder.

Every rung is trained FROM SCRATCH per run (no leaked global state) and exposes a
tiny uniform interface so the runner can treat them identically:

- Retrieval rungs implement ``fit(X, train_idx, train_pairs)`` then ``embed(X)``
  returning per-row vectors that are ranked by cosine.
- Prediction rungs implement ``fit(X, y, **ctx)`` then ``predict(X, **ctx)``.

The point of the ladder is calibration. If a domain's answer is reachable by
``RawCosine`` or ``Ridge``, that is a *finding* — it means the fancy model is not
buying anything there. ``RandomFloor`` / ``DummyMean`` pin the bottom so a small
absolute number can be read as "near chance" vs "real signal".

``MTNNRung`` is deliberately the only rung that can be either trained here (a small
vector-core MTNN on CPU, torch optional) OR fed precomputed embeddings/predictions
produced elsewhere (operator-GPU). Both slot into the same scorecard as "mtnn".

scikit-learn is an optional dependency: the numpy-only rungs (RawCosine,
LearnedLinearMap, RandomFloor, DummyMean, Persistence) always run; the sklearn
rungs raise :class:`ImportError` at ``fit`` time if it is missing, which the
runner records as ``skipped`` rather than crashing the whole benchmark.
"""

from __future__ import annotations

import numpy as np

__all__ = [
    "RetrievalBaseline",
    "PredictionBaseline",
    "RawCosine",
    "PCACosine",
    "LearnedLinearMap",
    "RandomFloor",
    "DummyMean",
    "Persistence",
    "Ridge",
    "PCARidge",
    "KNNRegressor",
    "HistGradientBoosting",
    "MLPRegressor",
    "MTNNRung",
    "default_retrieval_ladder",
    "default_prediction_ladder",
]


# --------------------------------------------------------------------------- #
# Interfaces
# --------------------------------------------------------------------------- #
class RetrievalBaseline:
    """Base class for retrieval rungs. Subclasses set ``name`` and implement fit/embed."""

    name: str = "retrieval-baseline"
    is_mtnn: bool = False

    def fit(
        self,
        X: np.ndarray,
        train_idx: np.ndarray | None = None,
        train_pairs: np.ndarray | None = None,
    ) -> RetrievalBaseline:
        return self

    def embed(self, X: np.ndarray) -> np.ndarray:  # pragma: no cover - abstract
        raise NotImplementedError


class PredictionBaseline:
    """Base class for prediction rungs. Subclasses set ``name`` and implement fit/predict."""

    name: str = "prediction-baseline"
    is_mtnn: bool = False

    def fit(self, X: np.ndarray, y: np.ndarray, **ctx) -> PredictionBaseline:
        return self

    def predict(self, X: np.ndarray, **ctx) -> np.ndarray:  # pragma: no cover - abstract
        raise NotImplementedError


# --------------------------------------------------------------------------- #
# Retrieval rungs
# --------------------------------------------------------------------------- #
class RawCosine(RetrievalBaseline):
    """Cosine similarity on the raw features. The 'do nothing' retrieval rung."""

    name = "raw_cosine"

    def embed(self, X: np.ndarray) -> np.ndarray:
        return np.asarray(X, dtype=np.float64)


class PCACosine(RetrievalBaseline):
    """PCA-reduce, then cosine. Tests whether a linear subspace is all you need."""

    def __init__(self, n_components: int = 16, seed: int = 0):
        self.n_components = n_components
        self.seed = seed
        self.name = f"pca_cosine(n={n_components})"
        self._pca = None

    def fit(self, X, train_idx=None, train_pairs=None):
        from sklearn.decomposition import PCA

        X = np.asarray(X, dtype=np.float64)
        fit_rows = X if train_idx is None else X[train_idx]
        n_comp = min(self.n_components, fit_rows.shape[0], fit_rows.shape[1])
        self._pca = PCA(n_components=n_comp, random_state=self.seed)
        self._pca.fit(fit_rows)
        return self

    def embed(self, X):
        return self._pca.transform(np.asarray(X, dtype=np.float64))


class LearnedLinearMap(RetrievalBaseline):
    """Supervised linear metric map, then cosine.

    Fits a closed-form ridge map ``W`` from anchor features to their paired
    (adjacent-period / same-cluster) target features over the TRAIN pairs:

        ``W = (Aᵀ A + α I)⁻¹ Aᵀ B``,  ``A = X[anchors]``, ``B = X[targets]``.

    Retrieval then ranks cosine over ``X @ W``. When a real supervised signal
    exists this pulls true partners together and should beat RawCosine; when it
    does not, it collapses toward RawCosine. Deterministic, no torch.

    This is the honest CPU stand-in for realty's learned-linear bar. An optional
    torch/InfoNCE variant (``mode="infonce"``) is available when torch is present;
    ``mode="ridge"`` (default) is what CI uses.
    """

    def __init__(self, alpha: float = 1.0, mode: str = "ridge", seed: int = 0):
        self.alpha = alpha
        self.mode = mode
        self.seed = seed
        self.name = f"learned_linear_map({mode})"
        self._W: np.ndarray | None = None

    def fit(self, X, train_idx=None, train_pairs=None):
        X = np.asarray(X, dtype=np.float64)
        if train_pairs is None or len(train_pairs) == 0:
            # No supervision available -> identity map (== RawCosine).
            self._W = np.eye(X.shape[1])
            return self
        if self.mode == "infonce":
            self._W = self._fit_infonce(X, train_pairs)
        else:
            self._W = self._fit_ridge(X, train_pairs)
        return self

    def _fit_ridge(self, X, train_pairs):
        a = np.asarray(train_pairs)[:, 0]
        b = np.asarray(train_pairs)[:, 1]
        A = X[a]
        B = X[b]
        d = X.shape[1]
        gram = A.T @ A + self.alpha * np.eye(d)
        return np.linalg.solve(gram, A.T @ B)

    def _fit_infonce(self, X, train_pairs):  # pragma: no cover - optional torch path
        import torch

        torch.manual_seed(self.seed)
        Xt = torch.tensor(X, dtype=torch.float32)
        a = torch.tensor(np.asarray(train_pairs)[:, 0], dtype=torch.long)
        b = torch.tensor(np.asarray(train_pairs)[:, 1], dtype=torch.long)
        d = X.shape[1]
        W = torch.eye(d, requires_grad=True)
        opt = torch.optim.Adam([W], lr=0.05)
        for _ in range(300):
            opt.zero_grad()
            E = torch.nn.functional.normalize(Xt @ W, dim=1)
            S = (E[a] @ E.T) / 0.07
            S[torch.arange(len(a)), a] = -1e9
            loss = torch.nn.functional.cross_entropy(S, b)
            loss.backward()
            opt.step()
        return W.detach().numpy().astype(np.float64)

    def embed(self, X):
        return np.asarray(X, dtype=np.float64) @ self._W


class RandomFloor(RetrievalBaseline):
    """Deterministic random embeddings — the chance floor for retrieval."""

    name = "random_floor"

    def __init__(self, d: int = 16, seed: int = 0):
        self.d = d
        self.seed = seed

    def embed(self, X):
        rng = np.random.default_rng(self.seed)
        return rng.standard_normal((np.asarray(X).shape[0], self.d))


# --------------------------------------------------------------------------- #
# Prediction rungs
# --------------------------------------------------------------------------- #
class DummyMean(PredictionBaseline):
    """Predict the training-set mean for every row. The prediction chance floor."""

    name = "dummy_mean"

    def fit(self, X, y, **ctx):
        self._mean = float(np.mean(np.asarray(y, dtype=float)))
        return self

    def predict(self, X, **ctx):
        return np.full(np.asarray(X).shape[0], self._mean, dtype=float)


class Persistence(PredictionBaseline):
    """Predict each row's own group's last-known training target (naive forecast).

    Falls back to the global training mean for groups unseen at fit time (or when
    no ``group_key`` context is supplied), which makes it identical to DummyMean
    in the i.i.d. case and a genuine naive-forecast floor in the temporal case.
    """

    name = "persistence"

    def fit(self, X, y, train_groups=None, train_times=None, **ctx):
        y = np.asarray(y, dtype=float)
        self._global = float(np.mean(y))
        self._last: dict[object, float] = {}
        if train_groups is not None:
            g = np.asarray(train_groups)
            if train_times is not None:
                order = np.argsort(np.asarray(train_times), kind="mergesort")
            else:
                order = np.arange(len(g))
            for i in order:
                self._last[g[i].item() if hasattr(g[i], "item") else g[i]] = y[i]
        return self

    def predict(self, X, test_groups=None, **ctx):
        n = np.asarray(X).shape[0]
        if test_groups is None:
            return np.full(n, self._global, dtype=float)
        g = np.asarray(test_groups)
        return np.array(
            [self._last.get(gi.item() if hasattr(gi, "item") else gi, self._global) for gi in g],
            dtype=float,
        )


class _SklearnRegressor(PredictionBaseline):
    """Adapter wrapping any sklearn regressor factory (imported lazily at fit)."""

    def __init__(self, name: str, factory):
        self.name = name
        self._factory = factory
        self._model = None

    def fit(self, X, y, **ctx):
        self._model = self._factory()
        self._model.fit(np.asarray(X, dtype=float), np.asarray(y, dtype=float))
        return self

    def predict(self, X, **ctx):
        return np.asarray(self._model.predict(np.asarray(X, dtype=float)), dtype=float)


def Ridge(alpha: float = 1.0, seed: int = 0) -> _SklearnRegressor:
    def factory():
        from sklearn.linear_model import Ridge as _Ridge

        return _Ridge(alpha=alpha, random_state=seed)

    return _SklearnRegressor("ridge", factory)


class PCARidge(PredictionBaseline):
    """PCA-reduce then Ridge. Caps n_components to the data's rank at fit time."""

    def __init__(self, n_components: int = 16, alpha: float = 1.0, seed: int = 0):
        self.n_components = n_components
        self.alpha = alpha
        self.seed = seed
        self.name = f"pca_ridge(n={n_components})"
        self._model = None

    def fit(self, X, y, **ctx):
        from sklearn.decomposition import PCA
        from sklearn.linear_model import Ridge as _Ridge
        from sklearn.pipeline import make_pipeline

        X = np.asarray(X, dtype=float)
        n_comp = max(1, min(self.n_components, X.shape[1], X.shape[0]))
        self._model = make_pipeline(
            PCA(n_components=n_comp, random_state=self.seed),
            _Ridge(alpha=self.alpha, random_state=self.seed),
        )
        self._model.fit(X, np.asarray(y, dtype=float))
        return self

    def predict(self, X, **ctx):
        return np.asarray(self._model.predict(np.asarray(X, dtype=float)), dtype=float)


def KNNRegressor(n_neighbors: int = 10) -> _SklearnRegressor:
    def factory():
        from sklearn.neighbors import KNeighborsRegressor

        return KNeighborsRegressor(n_neighbors=n_neighbors)

    return _SklearnRegressor(f"knn(k={n_neighbors})", factory)


def HistGradientBoosting(seed: int = 0) -> _SklearnRegressor:
    def factory():
        from sklearn.ensemble import HistGradientBoostingRegressor

        return HistGradientBoostingRegressor(random_state=seed)

    return _SklearnRegressor("hist_gbm", factory)


def MLPRegressor(seed: int = 0, hidden: tuple[int, ...] = (64, 32), max_iter: int = 500):
    def factory():
        from sklearn.neural_network import MLPRegressor as _MLP

        return _MLP(hidden_layer_sizes=hidden, random_state=seed, max_iter=max_iter)

    return _SklearnRegressor("mlp", factory)


# --------------------------------------------------------------------------- #
# The MTNN rung (train-here OR precomputed)
# --------------------------------------------------------------------------- #
class MTNNRung(RetrievalBaseline, PredictionBaseline):
    """The multi-task neural net under test.

    Two modes:

    - **precomputed** (default when ``embeddings`` or ``predictions`` is given):
      slot in vectors/predictions produced elsewhere (e.g. an operator's GPU
      training run). ``embed`` returns the stored embeddings; ``predict`` returns
      the stored predictions. No torch needed — this is how CI and the realty
      example use it.
    - **train** (``train=True``): train a small vector-core MTNN on CPU. Requires
      torch. For prediction it adds a linear head on the MTNN trunk (MSE); for
      retrieval it fits the embedding with an InfoNCE contrastive loss on train
      pairs. Guarded and lazy so importing this module never needs torch.
    """

    is_mtnn = True
    name = "mtnn"

    def __init__(
        self,
        *,
        embeddings: np.ndarray | None = None,
        predictions: np.ndarray | None = None,
        train: bool = False,
        out_dim: int = 32,
        epochs: int = 200,
        lr: float = 0.01,
        seed: int = 0,
    ):
        self._embeddings = None if embeddings is None else np.asarray(embeddings, dtype=np.float64)
        self._predictions = None if predictions is None else np.asarray(predictions, dtype=float)
        self.train = train
        self.out_dim = out_dim
        self.epochs = epochs
        self.lr = lr
        self.seed = seed
        self._model = None
        self._trained_emb: np.ndarray | None = None
        self._trained_pred = None

    # -- retrieval --
    def fit(self, X=None, y=None, train_idx=None, train_pairs=None, **ctx):
        if not self.train:
            return self
        if train_pairs is not None:  # retrieval training
            self._trained_emb = self._train_retrieval(np.asarray(X, float), train_pairs)
        else:  # prediction training
            self._model = self._train_prediction(np.asarray(X, float), np.asarray(y, float))
        return self

    def embed(self, X):
        if self._embeddings is not None:
            return self._embeddings
        if self._trained_emb is not None:
            return self._trained_emb
        raise ValueError("MTNNRung retrieval needs precomputed embeddings or train=True")

    def predict(self, X, **ctx):
        if self._predictions is not None:
            return self._predictions
        if self._model is not None:  # pragma: no cover - optional torch path
            import torch

            with torch.no_grad():
                out = self._model(torch.tensor(np.asarray(X, np.float32)))
            return out.squeeze(-1).numpy().astype(float)
        raise ValueError("MTNNRung prediction needs precomputed predictions or train=True")

    # -- optional torch training paths (not exercised in CI) --
    def _build_trunk(self, in_dim):  # pragma: no cover - optional torch path
        import torch.nn as nn

        return nn.Sequential(
            nn.Linear(in_dim, 64),
            nn.GELU(),
            nn.Linear(64, 64),
            nn.GELU(),
            nn.Linear(64, self.out_dim),
        )

    def _train_retrieval(self, X, train_pairs):  # pragma: no cover - optional torch path
        import torch
        import torch.nn.functional as F

        torch.manual_seed(self.seed)
        Xt = torch.tensor(X, dtype=torch.float32)
        trunk = self._build_trunk(X.shape[1])
        a = torch.tensor(np.asarray(train_pairs)[:, 0], dtype=torch.long)
        b = torch.tensor(np.asarray(train_pairs)[:, 1], dtype=torch.long)
        opt = torch.optim.Adam(trunk.parameters(), lr=self.lr)
        for _ in range(self.epochs):
            opt.zero_grad()
            E = F.normalize(trunk(Xt), dim=1)
            S = (E[a] @ E.T) / 0.07
            S[torch.arange(len(a)), a] = -1e9
            loss = F.cross_entropy(S, b)
            loss.backward()
            opt.step()
        with torch.no_grad():
            return F.normalize(trunk(Xt), dim=1).numpy().astype(np.float64)

    def _train_prediction(self, X, y):  # pragma: no cover - optional torch path
        import torch
        import torch.nn as nn

        torch.manual_seed(self.seed)
        Xt = torch.tensor(X, dtype=torch.float32)
        yt = torch.tensor(y, dtype=torch.float32).unsqueeze(-1)
        trunk = self._build_trunk(X.shape[1])
        head = nn.Linear(self.out_dim, 1)
        model = nn.Sequential(trunk, head)
        opt = torch.optim.Adam(model.parameters(), lr=self.lr)
        lossf = nn.MSELoss()
        for _ in range(self.epochs):
            opt.zero_grad()
            loss = lossf(model(Xt), yt)
            loss.backward()
            opt.step()
        model.eval()
        return model


# --------------------------------------------------------------------------- #
# Default ladders
# --------------------------------------------------------------------------- #
def default_retrieval_ladder(seed: int = 0, pca_components: int = 16) -> list[RetrievalBaseline]:
    """Standard retrieval ladder (excludes the MTNN rung; the runner adds that)."""
    return [
        RandomFloor(seed=seed),
        RawCosine(),
        PCACosine(n_components=pca_components, seed=seed),
        LearnedLinearMap(mode="ridge", seed=seed),
    ]


def default_prediction_ladder(seed: int = 0) -> list[PredictionBaseline]:
    """Standard prediction ladder (excludes the MTNN rung; the runner adds that)."""
    return [
        DummyMean(),
        Persistence(),
        Ridge(seed=seed),
        PCARidge(seed=seed),
        KNNRegressor(),
        HistGradientBoosting(seed=seed),
        MLPRegressor(seed=seed),
    ]
