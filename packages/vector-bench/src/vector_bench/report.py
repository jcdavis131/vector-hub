"""Serialize a :class:`~vector_bench.runner.Scorecard` to a versioned JSON report.

The schema is designed for a dashboard to render a method x metric grid with the
MTNN delta highlighted. Every metric carries its direction
(``higher_is_better``), the ranked methods, the best non-MTNN baseline, the MTNN
value, the signed delta (positive => MTNN better), and the boolean verdict — so a
UI can color a cell green/red without re-deriving anything.
"""

from __future__ import annotations

import json
from pathlib import Path

from .runner import Scorecard

__all__ = ["SCHEMA_VERSION", "scorecard_to_dict", "write_report"]

SCHEMA_VERSION = "1.0"


def _round(v, ndigits: int = 6):
    return None if v is None else round(float(v), ndigits)


def scorecard_to_dict(sc: Scorecard) -> dict:
    """Convert a Scorecard into a JSON-serializable dict (schema v1.0)."""
    methods = []
    for r in sc.methods:
        methods.append(
            {
                "name": r.name,
                "kind": r.kind,
                "is_mtnn": r.is_mtnn,
                "status": r.status,
                "metrics": {k: _round(v) for k, v in r.metrics.items()},
                "note": r.note,
            }
        )

    metrics = {}
    for name, v in sc.verdicts.items():
        metrics[name] = {
            "higher_is_better": v.higher_is_better,
            "ranking": [{"method": m, "value": _round(val)} for m, val in v.ranking],
            "best_method": v.best_method,
            "best_baseline": v.best_baseline,
            "best_baseline_value": _round(v.best_baseline_value),
            "mtnn_value": _round(v.mtnn_value),
            "mtnn_delta": _round(v.mtnn_delta),
            "mtnn_beats_best_baseline": v.mtnn_beats_best_baseline,
        }

    return {
        "schema_version": SCHEMA_VERSION,
        "domain": sc.domain,
        "task": sc.task,
        "task_type": sc.task_type,
        "split": sc.split,
        "seed": sc.seed,
        "k_values": list(sc.k_values),
        "summary": sc.summary,
        "methods": methods,
        "metrics": metrics,
        "notes": sc.notes,
    }


def write_report(sc: Scorecard, path: str | Path) -> Path:
    """Write ``benchmark_report.json`` for ``sc`` and return the path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(scorecard_to_dict(sc), indent=2) + "\n", encoding="utf-8")
    return path
