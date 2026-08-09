"""Task definitions and leakage-safe splits.

A :class:`BenchmarkTask` is the single object the whole harness consumes. It
carries the data (features, optional embeddings, optional targets, optional
retrieval pairs/labels), declares whether the domain is a ``"retrieval"`` or
``"prediction"`` problem, names the metrics to report, and pins a split policy
plus a seed so every run is deterministic.

The split policy is where honesty starts: a benchmark that leaks the answer from
train into test makes every method look good and tells you nothing. The three
splitters here each guarantee a specific non-leakage property:

- ``random`` — a plain seeded shuffle. Fine when rows are i.i.d.
- ``temporal`` — train strictly on the past, test strictly on the future, using a
  time key and a cut. No future row is ever visible at fit time.
- ``group`` — no entity (economy, ticker, player) appears in both train and test,
  so a method cannot win by memorizing an entity.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

__all__ = [
    "BenchmarkTask",
    "Split",
    "random_split",
    "temporal_split",
    "group_split",
    "build_adjacent_period_pairs",
]

TaskType = str  # "retrieval" | "prediction"
SplitKind = str  # "random" | "temporal" | "group"


@dataclass(frozen=True)
class Split:
    """Train/test row indices produced by a leakage-safe splitter.

    For retrieval tasks the same split also induces *train pairs* and *test
    pairs*: a pair is assigned to whichever side its anchor row falls on. The
    gallery for evaluation is always the full row set (retrieval ranks a query
    against everything), but a supervised method may only *fit* on train pairs.
    """

    train_idx: np.ndarray
    test_idx: np.ndarray
    kind: SplitKind

    def train_pairs(self, pairs: np.ndarray) -> np.ndarray:
        """Pairs whose anchor is in the train set."""
        train_set = set(int(i) for i in self.train_idx)
        return np.array(
            [p for p in np.asarray(pairs) if int(p[0]) in train_set],
            dtype=np.int64,
        ).reshape(-1, 2)

    def test_pairs(self, pairs: np.ndarray) -> np.ndarray:
        """Pairs whose anchor is in the test set."""
        test_set = set(int(i) for i in self.test_idx)
        return np.array(
            [p for p in np.asarray(pairs) if int(p[0]) in test_set],
            dtype=np.int64,
        ).reshape(-1, 2)


def random_split(n: int, test_frac: float = 0.3, seed: int = 0) -> Split:
    """Seeded uniform random split of ``range(n)`` into train/test."""
    if not 0.0 < test_frac < 1.0:
        raise ValueError("test_frac must be in (0, 1)")
    rng = np.random.default_rng(seed)
    perm = rng.permutation(n)
    n_test = max(1, int(round(n * test_frac)))
    test_idx = np.sort(perm[:n_test])
    train_idx = np.sort(perm[n_test:])
    return Split(train_idx=train_idx, test_idx=test_idx, kind="random")


def temporal_split(
    time_key: np.ndarray,
    cut: float | int | None = None,
    test_frac: float = 0.3,
) -> Split:
    """Past/future split: train where ``time < cut``, test where ``time >= cut``.

    If ``cut`` is None it is chosen as the quantile that puts ~``test_frac`` of
    rows in the future. No future row is ever in train, which is the whole point:
    a temporal benchmark that shuffles is lying about what the model will see.
    """
    t = np.asarray(time_key)
    if cut is None:
        cut = float(np.quantile(t.astype(float), 1.0 - test_frac))
    train_idx = np.sort(np.where(t < cut)[0])
    test_idx = np.sort(np.where(t >= cut)[0])
    if len(train_idx) == 0 or len(test_idx) == 0:
        raise ValueError(f"temporal cut={cut!r} left an empty side")
    return Split(train_idx=train_idx, test_idx=test_idx, kind="temporal")


def group_split(
    group_key: np.ndarray,
    test_frac: float = 0.3,
    seed: int = 0,
) -> Split:
    """Entity-disjoint split: no group id appears in both train and test.

    Groups (not rows) are shuffled and partitioned, so a method cannot score by
    recognizing an entity it already saw.
    """
    g = np.asarray(group_key)
    groups = np.unique(g)
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(groups))
    n_test = max(1, int(round(len(groups) * test_frac)))
    test_groups = set(groups[perm[:n_test]].tolist())
    test_mask = np.array([gi in test_groups for gi in g])
    test_idx = np.sort(np.where(test_mask)[0])
    train_idx = np.sort(np.where(~test_mask)[0])
    if len(train_idx) == 0 or len(test_idx) == 0:
        raise ValueError("group split left an empty side")
    return Split(train_idx=train_idx, test_idx=test_idx, kind="group")


def build_adjacent_period_pairs(
    group_key: np.ndarray,
    time_key: np.ndarray,
) -> np.ndarray:
    """Identity-retrieval pairs: (row_t, row_{t+1}) for the same group.

    This is the fleet's canonical retrieval target — given one period of an
    entity, find the *same entity's* adjacent period among all entities. Returns
    an ``(m, 2)`` array of ``(anchor_idx, target_idx)`` row-index pairs. Both
    directions are emitted so every row that has a neighbor is a queryable anchor.
    """
    g = np.asarray(group_key)
    t = np.asarray(time_key)
    pairs: list[tuple[int, int]] = []
    for grp in np.unique(g):
        idx = np.where(g == grp)[0]
        order = idx[np.argsort(t[idx])]
        times = t[order]
        for a in range(len(order) - 1):
            if times[a + 1] - times[a] == 1:  # strictly adjacent period
                pairs.append((int(order[a]), int(order[a + 1])))
                pairs.append((int(order[a + 1]), int(order[a])))
    return np.array(pairs, dtype=np.int64).reshape(-1, 2)


@dataclass
class BenchmarkTask:
    """A single benchmark: data + split policy + metrics for one domain.

    Parameters
    ----------
    name, domain :
        Human labels (``domain`` groups tasks; ``name`` is the specific task).
    X :
        ``(n, d)`` feature matrix. The baseline ladder consumes this directly.
    task_type :
        ``"retrieval"`` or ``"prediction"``.
    metrics :
        Metric families to report. Retrieval: any of ``recall``, ``purity``,
        ``silhouette``. Prediction: any of ``spearman_ic``, ``mae``, ``rmse``,
        ``r2``, ``roc_auc``.
    embeddings :
        Optional ``(n, d_emb)`` precomputed MTNN embeddings (operator-GPU output).
        Slotted in via :class:`~vector_bench.baselines.MTNNRung`.
    y :
        Optional ``(n,)`` prediction targets.
    pairs :
        Optional ``(m, 2)`` retrieval identity pairs (anchor_idx, target_idx).
    labels :
        Optional ``(n,)`` cluster/class labels (for purity/silhouette).
    split :
        ``"random"`` | ``"temporal"`` | ``"group"``.
    group_key, time_key :
        Per-row entity id / time index, required by ``group`` / ``temporal``
        splits respectively.
    """

    name: str
    domain: str
    X: np.ndarray
    task_type: TaskType
    metrics: list[str]
    seed: int = 0
    embeddings: np.ndarray | None = None
    y: np.ndarray | None = None
    pairs: np.ndarray | None = None
    labels: np.ndarray | None = None
    split: SplitKind = "random"
    group_key: np.ndarray | None = None
    time_key: np.ndarray | None = None
    test_frac: float = 0.3
    time_cut: float | int | None = None
    k_values: tuple[int, ...] = (1, 5, 10)
    notes: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.X = np.asarray(self.X)
        n = self.X.shape[0]
        if self.task_type not in ("retrieval", "prediction"):
            raise ValueError(f"task_type must be retrieval|prediction, got {self.task_type!r}")
        if self.split not in ("random", "temporal", "group"):
            raise ValueError(f"split must be random|temporal|group, got {self.split!r}")
        if self.task_type == "prediction" and self.y is None:
            raise ValueError("prediction task requires y")
        if self.task_type == "retrieval" and self.pairs is None and self.labels is None:
            raise ValueError("retrieval task requires pairs (recall) or labels (purity/silhouette)")
        if self.split == "temporal" and self.time_key is None:
            raise ValueError("temporal split requires time_key")
        if self.split == "group" and self.group_key is None:
            raise ValueError("group split requires group_key")
        for attr in ("y", "labels", "group_key", "time_key", "embeddings"):
            v = getattr(self, attr)
            if v is not None:
                v = np.asarray(v)
                setattr(self, attr, v)
                if v.shape[0] != n:
                    raise ValueError(f"{attr} has {v.shape[0]} rows, expected {n}")
        if self.pairs is not None:
            self.pairs = np.asarray(self.pairs, dtype=np.int64).reshape(-1, 2)

    def make_split(self) -> Split:
        """Build the leakage-safe train/test split declared by ``self.split``."""
        if self.split == "random":
            return random_split(self.X.shape[0], self.test_frac, self.seed)
        if self.split == "temporal":
            return temporal_split(self.time_key, self.time_cut, self.test_frac)
        return group_split(self.group_key, self.test_frac, self.seed)
