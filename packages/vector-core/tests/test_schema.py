from vector_core.schema import FleetEntry, validate_entry


def _valid_entry() -> dict:
    return {
        "repo": "vector-hoops",
        "domain": "hoops",
        "embeddingDim": 48,
        "status": "shipped",
        "headlineMetric": {"name": "top1", "value": 0.55, "baseline": 0.44},
    }


def test_validate_entry_accepts_well_formed_entry():
    assert validate_entry(_valid_entry()) == []


def test_validate_entry_reports_each_missing_required_field():
    problems = validate_entry({})
    for key in ("repo", "domain", "embeddingDim", "status", "headlineMetric"):
        assert any(key in p for p in problems), f"expected a problem mentioning {key!r}"
    assert len(problems) == 5  # exactly the 5 required fields, no extras


def test_validate_entry_rejects_invalid_status():
    d = _valid_entry()
    d["status"] = "made-up-status"
    problems = validate_entry(d)
    assert any("invalid status" in p for p in problems)


def test_validate_entry_accepts_all_valid_statuses():
    for status in ("production", "shipped", "wip", "blocked"):
        d = _valid_entry()
        d["status"] = status
        assert validate_entry(d) == []


def test_validate_entry_rejects_non_int_embedding_dim():
    d = _valid_entry()
    d["embeddingDim"] = "48"
    problems = validate_entry(d)
    assert any("embeddingDim must be an int" in p for p in problems)


def test_validate_entry_rejects_float_embedding_dim():
    d = _valid_entry()
    d["embeddingDim"] = 48.0
    problems = validate_entry(d)
    assert any("embeddingDim must be an int" in p for p in problems)


def test_validate_entry_headline_metric_missing_name_or_value():
    d = _valid_entry()
    d["headlineMetric"] = {"baseline": 0.4}
    problems = validate_entry(d)
    assert any("headlineMetric missing name" in p for p in problems)
    assert any("headlineMetric missing value" in p for p in problems)


def test_validate_entry_headline_metric_null_is_rejected():
    d = _valid_entry()
    d["headlineMetric"] = None
    problems = validate_entry(d)
    assert any("headlineMetric must be an object" in p for p in problems)
    # required-field check should NOT also fire since the key IS present
    assert not any("missing required field: headlineMetric" in p for p in problems)


def test_validate_entry_headline_metric_wrong_type_is_rejected():
    d = _valid_entry()
    d["headlineMetric"] = "top1: 0.55"
    problems = validate_entry(d)
    assert any("headlineMetric must be an object" in p for p in problems)


def test_fleet_entry_to_dict_round_trips_through_from_dict():
    entry = FleetEntry(
        repo="vector-gridiron",
        domain="gridiron",
        embeddingDim=32,
        status="production",
        headlineMetric={"name": "mae", "value": 3.8, "baseline": 4.268},
        strengths="real nflverse features",
        gaps="",
    )
    d = entry.to_dict()
    assert d["repo"] == "vector-gridiron"
    assert d["visibility"] == "public"  # default preserved through asdict
    assert validate_entry(d) == []

    round_tripped = FleetEntry.from_dict(d)
    assert round_tripped == entry


def test_fleet_entry_from_dict_ignores_unknown_keys_defensively():
    d = _valid_entry()
    d["someFutureField"] = "not part of the dataclass yet"
    entry = FleetEntry.from_dict(d)
    assert entry.repo == "vector-hoops"
    assert not hasattr(entry, "someFutureField")


def test_fleet_entry_defaults():
    entry = FleetEntry(
        repo="vector-pitch",
        domain="pitch",
        embeddingDim=24,
        status="wip",
        headlineMetric={"name": "recall@10", "value": 0.7},
    )
    assert entry.metrics == {}
    assert entry.strengths == ""
    assert entry.gaps == ""
    assert entry.visibility == "public"
    assert entry.liveUrl == ""
    assert entry.archTag == ""
