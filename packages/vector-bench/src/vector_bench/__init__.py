"""vector-bench — an honest outperformance benchmark harness for the vector-* fleet.

Thesis under test: *a flexible multi-task neural net (MTNN) outperforms strong
per-task baselines across domains, on retrieval AND prediction.* This package
exists to test that claim honestly — it reports where the MTNN wins and where a
simple baseline wins, treating "this domain is simple" as a finding, not a
failure.

Typical use::

    from vector_bench import BenchmarkTask, run_benchmark, write_report

    task = BenchmarkTask(name=..., domain=..., X=..., task_type="prediction",
                         y=..., metrics=["spearman_ic", "rmse", "r2"])
    scorecard = run_benchmark(task)          # trains the whole ladder from scratch
    write_report(scorecard, "benchmark_report.json")

torch is optional: importing ``vector_bench`` never imports torch. Only
``MTNNRung(train=True)`` needs it; the precomputed-embeddings/predictions path
(operator-GPU outputs) does not.
"""

from __future__ import annotations

from . import baselines, metrics, registry, report, runner, tasks
from .baselines import (
    DummyMean,
    HistGradientBoosting,
    KNNRegressor,
    LearnedLinearMap,
    MLPRegressor,
    MTNNRung,
    PCACosine,
    PCARidge,
    Persistence,
    RandomFloor,
    RawCosine,
    Ridge,
    default_prediction_ladder,
    default_retrieval_ladder,
)
from .metrics import prediction_metrics, retrieval_metrics
from .registry import (
    DOMAIN_REGISTRY,
    all_targets,
    get_domain_spec,
    list_domains,
)
from .report import (
    DOMAIN_REPORT_SCHEMA_VERSION,
    SCHEMA_VERSION,
    domain_report_to_dict,
    scorecard_to_dict,
    write_domain_report,
    write_report,
)
from .runner import (
    DomainScorecard,
    MethodResult,
    MetricVerdict,
    Scorecard,
    TargetScorecard,
    compute_metric_verdict,
    run_benchmark,
    run_domain_benchmark,
)
from .tasks import (
    BINARY_METRICS,
    REGRESSION_METRICS,
    BenchmarkTask,
    DomainSpec,
    PredictionTarget,
    Split,
    build_adjacent_period_pairs,
    build_task_for_target,
    group_split,
    random_split,
    temporal_split,
)

__version__ = "0.1.0"

__all__ = [
    # submodules
    "tasks",
    "baselines",
    "metrics",
    "runner",
    "report",
    "registry",
    # tasks
    "BenchmarkTask",
    "PredictionTarget",
    "DomainSpec",
    "Split",
    "random_split",
    "temporal_split",
    "group_split",
    "build_adjacent_period_pairs",
    "build_task_for_target",
    "REGRESSION_METRICS",
    "BINARY_METRICS",
    # registry
    "DOMAIN_REGISTRY",
    "get_domain_spec",
    "list_domains",
    "all_targets",
    # baselines
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
    # metrics
    "prediction_metrics",
    "retrieval_metrics",
    # runner
    "run_benchmark",
    "run_domain_benchmark",
    "Scorecard",
    "TargetScorecard",
    "DomainScorecard",
    "MethodResult",
    "MetricVerdict",
    "compute_metric_verdict",
    # report
    "write_report",
    "scorecard_to_dict",
    "write_domain_report",
    "domain_report_to_dict",
    "SCHEMA_VERSION",
    "DOMAIN_REPORT_SCHEMA_VERSION",
]
