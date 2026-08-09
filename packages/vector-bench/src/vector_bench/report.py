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

from .runner import DomainScorecard, Scorecard

__all__ = [
    "SCHEMA_VERSION",
    "DOMAIN_REPORT_SCHEMA_VERSION",
    "scorecard_to_dict",
    "write_report",
    "domain_report_to_dict",
    "write_domain_report",
]

# Single-scorecard report. UNCHANGED — every existing 1.0 reader (and the shipped
# examples/realty/benchmark_report.json) keeps working byte-for-byte.
SCHEMA_VERSION = "1.0"

# Multi-target domain report. Minor bump: additive wrapper around a list of
# per-target entries, each embedding an unmodified 1.0 scorecard. A 1.0 reader
# that only understands the single-scorecard document is unaffected — this is a
# new, separately-named artifact — and a 1.1 reader can walk ``targets[].scorecard``
# and find the exact 1.0 shape it already knows.
DOMAIN_REPORT_SCHEMA_VERSION = "1.1"


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


def domain_report_to_dict(dsc: DomainScorecard) -> dict:
    """Convert a multi-target :class:`DomainScorecard` to a dict (schema v1.1).

    Each entry in ``targets`` carries the target's metadata and, when the target
    was scored, an embedded schema-1.0 scorecard under ``scorecard`` (``null`` for
    spec-only / errored targets). The per-target MTNN verdict is therefore exactly
    as legible as in a single-scorecard report, one level down.
    """
    targets = []
    for t in dsc.targets:
        targets.append(
            {
                "target": {
                    "name": t.target_name,
                    "kind": t.kind,
                    "horizon": t.horizon,
                    "split": t.split,
                    "primary_metric": t.primary_metric,
                    "status": t.status,
                },
                "note": t.note,
                "scorecard": (
                    scorecard_to_dict(t.scorecard) if t.scorecard is not None else None
                ),
            }
        )

    return {
        "schema_version": DOMAIN_REPORT_SCHEMA_VERSION,
        "domain": dsc.domain,
        "primary_task_type": dsc.primary_task_type,
        "description": dsc.description,
        "aggregate": dsc.aggregate,
        "targets": targets,
        "notes": dsc.notes,
    }


def write_domain_report(dsc: DomainScorecard, path: str | Path) -> Path:
    """Write a multi-target ``benchmark_report.json`` (schema 1.1) and return path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(domain_report_to_dict(dsc), indent=2) + "\n", encoding="utf-8"
    )
    return path
