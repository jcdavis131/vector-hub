"""The per-domain prediction-target registry — declarative, not hardcoded.

This module is *data*: it names the set of prediction targets each fleet domain
declares, following each domain's real signal. The runner never hardcodes these;
it consumes a :class:`~vector_bench.tasks.DomainSpec` and turns each target into a
per-target :class:`~vector_bench.tasks.BenchmarkTask`. Adding a domain or a target
is an edit *here*, not in the runner.

Every target below is honest about its state:

- ``status="data-wired"`` — a builder can produce ``(X, y)`` for it today.
- ``status="spec-only"`` — declared, with a leakage-safe construction written
  down, but no data plumbed yet. A spec-only target is carried through the runner
  and the report as ``spec-only`` and NEVER fabricates a number.

Real-data benchmark runs have since validated data-wiring for hoops, gridiron,
equities, pitch, and unified: those targets are now ``data-wired``, each with a
code comment linking the domain-repo PR where the real feature/label build and
the benchmark run landed. realty's real-data run still refutes the
outperformance thesis — consistent with its retrieval task (see
``examples/realty/``) — so its targets remain ``spec-only``; see the comment on
each realty target for the PR. The synthetic example
(``examples/multitarget_synthetic/``) remains the only place a full per-target
report is computed from data generated in-repo.
"""

from __future__ import annotations

from .tasks import BINARY_METRICS, REGRESSION_METRICS, DomainSpec, PredictionTarget

__all__ = [
    "DOMAIN_REGISTRY",
    "get_domain_spec",
    "list_domains",
    "all_targets",
]

_R = REGRESSION_METRICS  # ("spearman_ic", "mae", "rmse", "r2")
_B = BINARY_METRICS  # ("roc_auc", "spearman_ic")


# --------------------------------------------------------------------------- #
# hoops — NBA next-season advanced-stat targets
# --------------------------------------------------------------------------- #
_HOOPS = DomainSpec(
    domain="hoops",
    primary_task_type="prediction",
    description=(
        "NBA player-seasons. Given a player's season-t feature vector, predict "
        "several next-season outcomes independently — advanced efficiency stats "
        "and a raw counting line."
    ),
    targets=(
        PredictionTarget(
            name="next_season_per",
            kind="regression",
            horizon="next_season",
            metrics=_R,
            split="temporal",
            primary_metric="spearman_ic",
            status="data-wired",  # verified on real data: https://github.com/jcdavis131/vector-hoops/pull/14
            description="Next-season Player Efficiency Rating.",
            construction=(
                "y = PER of the same player in season t+1; features from season t "
                "only. Temporal split on the *target* season year: train on "
                "target-season <= cut, test strictly after. No future season is "
                "visible at fit time; a player may recur across seasons (realistic)."
            ),
        ),
        PredictionTarget(
            name="next_season_win_shares",
            kind="regression",
            horizon="next_season",
            metrics=_R,
            split="temporal",
            primary_metric="spearman_ic",
            status="data-wired",  # verified on real data: https://github.com/jcdavis131/vector-hoops/pull/14
            description="Next-season Win Shares.",
            construction=(
                "y = Win Shares of the same player in season t+1; features from "
                "season t. Temporal split on target season year (as PER)."
            ),
        ),
        PredictionTarget(
            name="next_season_bpm",
            kind="regression",
            horizon="next_season",
            metrics=_R,
            split="temporal",
            primary_metric="spearman_ic",
            status="data-wired",  # verified on real data: https://github.com/jcdavis131/vector-hoops/pull/14
            description="Next-season Box Plus/Minus.",
            construction=(
                "y = BPM of the same player in season t+1; features from season t. "
                "Temporal split on target season year."
            ),
        ),
        PredictionTarget(
            name="next_season_pts",
            kind="regression",
            horizon="next_season",
            metrics=_R,
            split="temporal",
            primary_metric="spearman_ic",
            status="data-wired",  # verified on real data: https://github.com/jcdavis131/vector-hoops/pull/14
            description="Next-season points per game (counting line component).",
            construction="y = PTS/G in season t+1; features from season t. Temporal split.",
        ),
        PredictionTarget(
            name="next_season_reb",
            kind="regression",
            horizon="next_season",
            metrics=_R,
            split="temporal",
            primary_metric="spearman_ic",
            status="data-wired",  # verified on real data: https://github.com/jcdavis131/vector-hoops/pull/14
            description="Next-season rebounds per game (counting line component).",
            construction="y = REB/G in season t+1; features from season t. Temporal split.",
        ),
        PredictionTarget(
            name="next_season_ast",
            kind="regression",
            horizon="next_season",
            metrics=_R,
            split="temporal",
            primary_metric="spearman_ic",
            status="data-wired",  # verified on real data: https://github.com/jcdavis131/vector-hoops/pull/14
            description="Next-season assists per game (counting line component).",
            construction="y = AST/G in season t+1; features from season t. Temporal split.",
        ),
    ),
)


# --------------------------------------------------------------------------- #
# gridiron — NFL next-game fantasy + components
# --------------------------------------------------------------------------- #
_GRIDIRON = DomainSpec(
    domain="gridiron",
    primary_task_type="prediction",
    description=(
        "NFL player-games. Given a player's pre-game feature vector, predict "
        "next-game fantasy output and its yardage / touchdown components."
    ),
    targets=(
        PredictionTarget(
            name="next_game_fpts",
            kind="regression",
            horizon="next_game",
            metrics=_R,
            split="temporal",
            primary_metric="spearman_ic",
            status="data-wired",  # verified on real data: https://github.com/jcdavis131/vector-gridiron/pull/5
            description="Next-game fantasy points (PPR).",
            construction=(
                "y = fantasy points scored in the player's next game; features from "
                "games strictly before it. Temporal split on game date/week: train "
                "on weeks <= cut, test strictly after. No future game leaks."
            ),
        ),
        PredictionTarget(
            name="next_game_yards",
            kind="regression",
            horizon="next_game",
            metrics=_R,
            split="temporal",
            primary_metric="spearman_ic",
            status="data-wired",  # verified on real data: https://github.com/jcdavis131/vector-gridiron/pull/5
            description="Next-game total yards (rush + rec + pass).",
            construction=(
                "y = total yards in the next game; features from prior games. Temporal split."
            ),
        ),
        PredictionTarget(
            name="next_game_tds",
            kind="regression",
            horizon="next_game",
            metrics=_R,
            split="temporal",
            primary_metric="spearman_ic",
            status="data-wired",  # verified on real data: https://github.com/jcdavis131/vector-gridiron/pull/5
            description="Next-game total touchdowns.",
            construction=(
                "y = total TDs in the next game; features from prior games. Temporal split."
            ),
        ),
    ),
)


# --------------------------------------------------------------------------- #
# equities — forward return, forward vol, drawdown-exceedance flag
# --------------------------------------------------------------------------- #
_EQUITIES = DomainSpec(
    domain="equities",
    primary_task_type="prediction",
    description=(
        "Ticker-dates. The classic IC-and-ROC story per target: a forward return "
        "(rank IC), a forward realized volatility, and a binary drawdown flag."
    ),
    targets=(
        PredictionTarget(
            name="forward_return",
            kind="regression",
            horizon="1m",
            metrics=_R,
            split="temporal",
            primary_metric="spearman_ic",
            status="data-wired",  # verified on real data: https://github.com/jcdavis131/vector-equities/pull/5
            description="Forward (next-window) total return.",
            construction=(
                "y = return over (t, t+H]; features use only information available "
                "at t. Temporal split at a date cut: train dates <= cut, test after. "
                "spearman_ic is the headline (rank-IC of the signal)."
            ),
        ),
        PredictionTarget(
            name="forward_realized_vol",
            kind="regression",
            horizon="1m",
            metrics=_R,
            split="temporal",
            primary_metric="spearman_ic",
            status="data-wired",  # verified on real data: https://github.com/jcdavis131/vector-equities/pull/5
            description="Forward realized volatility over the next window.",
            construction=(
                "y = realized vol of returns over (t, t+H]; features known at t. "
                "Temporal split at a date cut."
            ),
        ),
        PredictionTarget(
            name="drawdown_exceedance",
            kind="binary_classification",
            horizon="1m",
            metrics=_B,
            split="temporal",
            primary_metric="roc_auc",
            status="data-wired",  # verified on real data: https://github.com/jcdavis131/vector-equities/pull/5
            description="Whether forward max drawdown exceeds a threshold (1) or not (0).",
            construction=(
                "y = 1 if the max peak-to-trough drawdown over (t, t+H] exceeds a "
                "fixed threshold else 0; features known at t. Temporal split at a "
                "date cut. Scored by roc_auc over the regressor's score output."
            ),
        ),
    ),
)


# --------------------------------------------------------------------------- #
# realty — retrieval-primary + price-change regressions + appreciation flag
# --------------------------------------------------------------------------- #
_REALTY = DomainSpec(
    domain="realty",
    primary_task_type="retrieval",
    description=(
        "Country-year property markets. Primary task is identity retrieval (the "
        "shipped examples/realty run); these prediction targets are additive and "
        "do not disturb the retrieval path."
    ),
    targets=(
        PredictionTarget(
            name="next_year_price_change",
            kind="regression",
            horizon="1y",
            metrics=_R,
            split="temporal",
            primary_metric="spearman_ic",
            status="spec-only",  # real-data run still refutes the thesis: https://github.com/jcdavis131/vector-realty/pull/4
            description="Next-year real property price change.",
            construction=(
                "y = price change from year t to t+1 for the same economy; features "
                "from year t. Temporal split on target year (train target-year <= "
                "2015, test after — same cut discipline as the retrieval example)."
            ),
        ),
        PredictionTarget(
            name="three_year_price_change",
            kind="regression",
            horizon="3y",
            metrics=_R,
            split="temporal",
            primary_metric="spearman_ic",
            status="spec-only",  # real-data run still refutes the thesis: https://github.com/jcdavis131/vector-realty/pull/4
            description="Three-year-ahead cumulative real price change.",
            construction=(
                "y = cumulative price change from year t to t+3; features from year "
                "t. Temporal split on target (t+3) year. Longer horizon = fewer "
                "usable rows; leakage rule unchanged."
            ),
        ),
        PredictionTarget(
            name="above_market_appreciation",
            kind="binary_classification",
            horizon="1y",
            metrics=_B,
            split="temporal",
            primary_metric="roc_auc",
            status="spec-only",  # real-data run still refutes the thesis: https://github.com/jcdavis131/vector-realty/pull/4
            description="Whether an economy beats the cross-sectional median 1y appreciation.",
            construction=(
                "y = 1 if year-t+1 price change exceeds the *train-set* median for "
                "that year's cohort else 0 (median computed on train only, so the "
                "test threshold never sees test labels); features from year t. "
                "Temporal split. Scored by roc_auc."
            ),
        ),
    ),
)


# --------------------------------------------------------------------------- #
# pitch — soccer, retrieval-primary + at least one prediction target
# --------------------------------------------------------------------------- #
_PITCH = DomainSpec(
    domain="pitch",
    primary_task_type="retrieval",
    description=(
        "Soccer player-windows. Retrieval-primary (find the same player's adjacent "
        "window), but not retrieval-only: two forward prediction targets are "
        "declared so the domain participates in the prediction thesis too."
    ),
    targets=(
        PredictionTarget(
            name="next_window_minutes",
            kind="regression",
            horizon="next_window",
            metrics=_R,
            split="temporal",
            primary_metric="spearman_ic",
            status="data-wired",  # verified on real data: https://github.com/jcdavis131/vector-pitch/pull/4
            description="Minutes played in the next match window.",
            construction=(
                "y = minutes in the player's next window; features from prior "
                "windows only. Temporal split on window index: train <= cut, test "
                "after. No future window leaks."
            ),
        ),
        PredictionTarget(
            name="next_window_goal_contribution",
            kind="regression",
            horizon="next_window",
            metrics=_R,
            split="temporal",
            primary_metric="spearman_ic",
            status="data-wired",  # verified on real data: https://github.com/jcdavis131/vector-pitch/pull/4
            description="Goal-contribution rate (goals+assists per 90) next window.",
            construction=(
                "y = (goals + assists) per 90 in the next window; features from "
                "prior windows. Temporal split on window index."
            ),
        ),
    ),
)


# --------------------------------------------------------------------------- #
# unified — cross-domain transfer probe
# --------------------------------------------------------------------------- #
_UNIFIED = DomainSpec(
    domain="unified",
    primary_task_type="prediction",
    description=(
        "The shared-embedding transfer test. Does one MTNN embedding, trained with "
        "its heads on the OTHER domains, still carry signal for a target in a "
        "domain it was NOT primarily trained to predict?"
    ),
    transfer_probe=(
        "TRANSFER PROBE: freeze the unified MTNN's shared embedding, hold out one "
        "domain entirely from head training, then fit ONLY a fresh linear head on "
        "the held-out domain's target using the frozen embedding as features. The "
        "MTNN 'rung' is this frozen-embedding + linear-probe result; the baseline "
        "gauntlet runs on the held-out domain's raw features. A win means the "
        "shared representation transferred; a loss means it did not. The held-out "
        "domain's own leakage-safe split (temporal) is reused unchanged, so "
        "transfer is measured on genuinely future rows."
    ),
    targets=(
        PredictionTarget(
            name="transfer_forward_return",
            kind="regression",
            horizon="1m",
            metrics=_R,
            split="temporal",
            primary_metric="spearman_ic",
            status="data-wired",  # verified on real data: https://github.com/jcdavis131/vector-unified/pull/5
            description=(
                "equities forward_return predicted from a frozen embedding "
                "trained WITHOUT equities."
            ),
            construction=(
                "Target identical to equities.forward_return (same leakage-safe "
                "temporal construction). Features = frozen unified embedding whose "
                "heads never saw equities. Probe = linear head fit on train rows "
                "only. This is the held-out-domain transfer measurement."
            ),
        ),
        PredictionTarget(
            name="transfer_next_season_per",
            kind="regression",
            horizon="next_season",
            metrics=_R,
            split="temporal",
            primary_metric="spearman_ic",
            status="data-wired",  # verified on real data: https://github.com/jcdavis131/vector-unified/pull/5
            description=(
                "hoops next_season_per predicted from a frozen embedding trained WITHOUT hoops."
            ),
            construction=(
                "Target identical to hoops.next_season_per. Features = frozen "
                "unified embedding whose heads never saw hoops. Linear probe on "
                "train rows only; hoops' temporal split reused."
            ),
        ),
    ),
)


DOMAIN_REGISTRY: dict[str, DomainSpec] = {
    spec.domain: spec
    for spec in (_HOOPS, _GRIDIRON, _EQUITIES, _REALTY, _PITCH, _UNIFIED)
}


def get_domain_spec(domain: str) -> DomainSpec:
    """Look up a :class:`~vector_bench.tasks.DomainSpec` by domain name."""
    if domain not in DOMAIN_REGISTRY:
        raise KeyError(f"unknown domain {domain!r}; known: {sorted(DOMAIN_REGISTRY)}")
    return DOMAIN_REGISTRY[domain]


def list_domains() -> list[str]:
    """All registered domain names, sorted."""
    return sorted(DOMAIN_REGISTRY)


def all_targets() -> list[tuple[str, PredictionTarget]]:
    """Every ``(domain, target)`` pair across the registry."""
    return [(d, t) for d, spec in DOMAIN_REGISTRY.items() for t in spec.targets]
