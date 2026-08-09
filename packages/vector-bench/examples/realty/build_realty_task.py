#!/usr/bin/env python3
"""Real-data benchmark: vector-realty adjacent-year identity retrieval.

This is vector-bench pointed at a real domain. It reconstructs the 18-d masked,
z-scored property-market feature matrix from vector-realty's *committed* raw
snapshot (``pipeline/data/bis_property.json``) — the exact construction in
realty's ``build_features.py`` — pairs it with the *committed* 32-d MTNN
embeddings (``assets/realty_embeddings.json``), and runs the ladder:

    raw_cosine                 cosine on the raw z-scored features (no learning)
    learned_linear_map(ridge)  closed-form supervised linear map, then cosine
    learned_linear_map(infonce)  a full linear metric map trained with InfoNCE via
                                 autograd (correct gradient) — needs torch
    mtnn                       cosine on the shipped 32-d MTNN embeddings

Task: given one year of a country's property market, retrieve the SAME country's
NEXT year among all country-years. Temporal split at 2015 (train on pairs whose
target year <= 2015, evaluate strictly after) — no future row visible at fit
time. Candidate pool is every row.

Why this example exists: realty's own adversarial review found that a *correctly
differentiated* learned linear map (~0.85 recall@10) beats the shipped MTNN
(0.83) — the hand-written gradient in realty's probe undertrained the bar. This
run reproduces that honest result through the harness: the MTNN is NOT always the
winner, and vector-bench says so out loud.

READ-ONLY on vector-realty: nothing here writes to that repo. Only this script
and the resulting ``benchmark_report.json`` are committed to vector-bench; no
realty data is copied in.

Usage:
    python build_realty_task.py --realty-root /path/to/vector-realty
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from vector_bench import BenchmarkTask, LearnedLinearMap, MTNNRung, RawCosine, run_benchmark
from vector_bench.report import write_report

# Feature families — copied verbatim from vector-realty/pipeline/build_features.py
# so the reconstructed matrix matches the one the MTNN embeddings were built from.
MIN_YEARS = 8
FAMILIES = {
    "level": ["lvl_nom", "lvl_real", "lvl_vs_own_mean"],
    "momentum": ["g1_nom", "g1_real", "g3_nom", "g3_real", "g5_nom", "g5_real"],
    "vol": ["vol_q_nom", "vol_q_real", "vol_1y_nom"],
    "cycle": ["drawdown_nom", "drawdown_real", "yrs_since_peak", "up_run"],
    "gap": ["nom_minus_real_1y", "nom_minus_real_5y"],
}


def _qkey(q: str) -> tuple[int, int]:
    y, qq = q.split("-Q")
    return int(y), int(qq)


def build_matrix(bis_property: dict):
    """Reconstruct (Z, econ, year, feat) exactly as realty's build_features.py does."""
    idx = defaultdict(lambda: defaultdict(dict))
    for key, obs in bis_property["series"].items():
        code, name, basis, unit = key.split("|")
        if not (len(code) == 2 and code.isalpha()):
            continue
        if not unit.startswith("index"):
            continue
        for q, v in obs.items():
            idx[code][basis][_qkey(q)] = v

    feat = [f for fam in FAMILIES.values() for f in fam]
    fi = {f: i for i, f in enumerate(feat)}
    rows, econ, year = [], [], []

    for code, bases in sorted(idx.items()):
        ann = {}
        for basis, obs in bases.items():
            per = defaultdict(list)
            for (y, _q), v in obs.items():
                per[y].append(v)
            ann[basis] = {y: float(np.mean(vs)) for y, vs in per.items()}
        yrs = sorted(set().union(*[set(a) for a in ann.values()])) if ann else []
        if len(yrs) < MIN_YEARS:
            continue
        for y in yrs:
            x = np.full(len(feat), np.nan, dtype=np.float32)

            def put(f, v, _x=x):
                if v is not None and np.isfinite(v):
                    _x[fi[f]] = v

            for basis, tag in (("nominal", "nom"), ("real", "real")):
                a = ann.get(basis, {})
                if y not in a:
                    continue
                put(f"lvl_{tag}", a[y])
                for k, lab in ((1, "g1"), (3, "g3"), (5, "g5")):
                    if (y - k) in a and a[y - k]:
                        put(f"{lab}_{tag}", 100.0 * (a[y] / a[y - k] - 1.0))
                hist = [a[q] for q in sorted(a) if q <= y]
                if len(hist) >= 3:
                    peak = max(hist)
                    put(f"drawdown_{tag}", 100.0 * (a[y] / peak - 1.0) if peak else None)
                qv = [v for (yy, _), v in sorted(bases[basis].items()) if yy == y]
                if len(qv) >= 3:
                    put(f"vol_q_{tag}", float(np.std(qv, ddof=1)))
            a = ann.get("nominal", {})
            if y in a:
                hist = {q: a[q] for q in a if q <= y}
                if len(hist) >= 3:
                    pk = max(hist, key=lambda q: hist[q])
                    put("yrs_since_peak", float(y - pk))
                    put("lvl_vs_own_mean",
                        100.0 * (a[y] / float(np.mean(list(hist.values()))) - 1.0))
                    run = 0
                    for q in sorted(hist, reverse=True)[1:]:
                        if hist[q] < hist.get(q + 1, hist[q]):
                            run += 1
                        else:
                            break
                    put("up_run", float(run))
                g = [100.0 * (a[q] / a[q - 1] - 1.0)
                     for q in sorted(a) if (q - 1) in a and a[q - 1] and q <= y]
                if len(g) >= 3:
                    put("vol_1y_nom", float(np.std(g[-5:], ddof=1)))
            for lab, k in (("nom_minus_real_1y", "g1"), ("nom_minus_real_5y", "g5")):
                n_, r_ = x[fi[f"{k}_nom"]], x[fi[f"{k}_real"]]
                if np.isfinite(n_) and np.isfinite(r_):
                    put(lab, float(n_ - r_))
            if np.isfinite(x).sum() >= 4:
                rows.append(x)
                econ.append(code)
                year.append(y)

    X = np.vstack(rows)
    M = np.isfinite(X).astype(np.float32)
    Xf = np.where(np.isfinite(X), X, 0.0).astype(np.float32)
    mu = np.array([Xf[M[:, j] > 0, j].mean() if M[:, j].sum() else 0.0
                   for j in range(X.shape[1])], dtype=np.float32)
    sd = np.array([Xf[M[:, j] > 0, j].std() if M[:, j].sum() > 1 else 1.0
                   for j in range(X.shape[1])], dtype=np.float32)
    sd[sd < 1e-6] = 1.0
    Z = ((Xf - mu) / sd) * M
    return Z, np.array(econ), np.array(year, dtype=np.int32), feat


def load_embeddings(emb_json: dict, econ: np.ndarray, year: np.ndarray) -> np.ndarray:
    """Align shipped 32-d MTNN embeddings to the reconstructed (econ, year) rows."""
    by_key = {(r["economy"], int(r["year"])): np.asarray(r["e"], dtype=np.float64)
              for r in emb_json["rows"]}
    out = np.zeros((len(econ), emb_json["d_emb"]), dtype=np.float64)
    missing = 0
    for i, (e, y) in enumerate(zip(econ, year, strict=True)):
        key = (str(e), int(y))
        if key in by_key:
            out[i] = by_key[key]
        else:
            missing += 1
    if missing:
        raise SystemExit(f"{missing} rows had no matching shipped embedding — matrix drift")
    return out


def next_year_pairs(econ: np.ndarray, year: np.ndarray) -> np.ndarray:
    """(i, j) where j is the SAME economy's next year — realty's pairs_of."""
    loc = {(str(e), int(y)): i for i, (e, y) in enumerate(zip(econ, year, strict=True))}
    pairs = [(i, loc[(str(e), int(y) + 1)])
             for i, (e, y) in enumerate(zip(econ, year, strict=True))
             if (str(e), int(y) + 1) in loc]
    return np.array(pairs, dtype=np.int64)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--realty-root", default="/workspace/vector-realty",
                    help="path to a (read-only) vector-realty checkout")
    ap.add_argument("--cut", type=int, default=2015)
    ap.add_argument("--out", default=str(Path(__file__).with_name("benchmark_report.json")))
    args = ap.parse_args()

    root = Path(args.realty_root)
    bis = json.loads((root / "pipeline" / "data" / "bis_property.json").read_text())
    emb_json = json.loads((root / "assets" / "realty_embeddings.json").read_text())

    Z, econ, year, feat = build_matrix(bis)
    embeddings = load_embeddings(emb_json, econ, year)
    pairs = next_year_pairs(econ, year)

    print(f"reconstructed {Z.shape[0]} rows x {Z.shape[1]} features, "
          f"{len(set(econ.tolist()))} economies, {year.min()}-{year.max()}")
    print(f"{len(pairs)} adjacent-year pairs; MTNN embeddings d={embeddings.shape[1]}")

    task = BenchmarkTask(
        name="realty_adjacent_year_retrieval",
        domain="realty",
        X=Z,
        embeddings=embeddings,
        pairs=pairs,
        task_type="retrieval",
        metrics=["recall"],
        split="temporal",
        time_key=year,
        time_cut=args.cut,
        k_values=(1, 5, 10),
        seed=0,
        notes={
            "source": "vector-realty (read-only): bis_property.json + realty_embeddings.json",
            "task": "identity retrieval — same economy's next year among all country-years",
            "split": f"temporal, train target-year<={args.cut}, test after; full-gallery pool",
            "provenance": "features reconstructed from committed raw snapshot via realty's "
                          "build_features.py logic; MTNN = shipped 32-d embeddings",
            "review_context": "realty's own review found a correct-gradient learned linear "
                              "map (~0.85 recall@10) beats the shipped MTNN (~0.83); this "
                              "run reproduces that finding honestly through the harness.",
        },
    )

    ladder = [RawCosine(), LearnedLinearMap(mode="ridge", seed=0)]
    try:
        import torch  # noqa: F401

        ladder.append(LearnedLinearMap(mode="infonce", seed=0))
    except ImportError:
        print("torch not available — skipping learned_linear_map(infonce)")

    sc = run_benchmark(task, mtnn=MTNNRung(embeddings=embeddings), ladder=ladder)

    print("\n=== recall@10 ===")
    for r in sc.methods:
        print(f"  {r.name:32s} {r.metrics.get('recall@10')}")
    print(f"\nverdict: {sc.summary['headline']}")

    out = write_report(sc, args.out)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
