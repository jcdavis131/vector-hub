#!/usr/bin/env python3
"""Validate Season Clock demo page and committed sample dataset."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "season-clock.html"
INDEX = ROOT / "public" / "index.html"
DEMO = ROOT / "public" / "assets" / "data" / "season_clock_demo.json"
VERCELIGNORE = ROOT / ".vercelignore"
DEMO_DEPLOY_PATH = "public/assets/data/season_clock_demo.json"
EXPECTED_TRACK_IDS = (
    "hoops_seasons",
    "gridiron_seasons",
    "sponsor_windows",
    "equities_fy",
)
EXPECTED_KINDS = {
    "hoops_seasons": "athlete_season",
    "gridiron_seasons": "athlete_season",
    "sponsor_windows": "sponsor_naming",
    "equities_fy": "equities_fy",
}
PRODUCT_URLS = {
    "hoops": "https://hoops.dumbmodel.com/",
    "gridiron": "https://gridiron.dumbmodel.com/",
    "equities": "https://equities.dumbmodel.com/",
}
FORBIDDEN = {
    "generated map": (r"<canvas\b", r"\b20[,\s]?719\b", r"\bgenerated layout\b"),
    "internal layout/model specification": (
        r"\bLCG\b",
        r"\bfusion\s+0\.",
        r"\bLOD\s*\d+",
        r"\bMTNN\s+v",
        r"\b7/7/0",
    ),
    "fabricated roster scoring": (r"\bAR\s*/\s*stretch\b",),
    "stale news tower": (r"\bnews tower\b", r"\bhonest 503\b"),
}
FORBIDDEN_JSON = (
    r"\b\d{1,3}(?:,\d{3})+\b",
    r"\b\d+\s*(?:entities|objects|points|pts)\b",
    r"\bscore(?:s|d|ing)?\b",
    r"\b(?:LCG|fusion|LOD|MTNN|UMAP|news tower)\b",
    r"\bAR\s*/\s*stretch\b",
    r"\b7/7/0\b",
)
ISO_DAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def path_ignored_by_vercelignore(rules_text: str, relative_path: str) -> bool:
    normalized = relative_path.replace("\\", "/")
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / ".gitignore").write_text(rules_text, encoding="utf-8")
        target = root.joinpath(*normalized.split("/"))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("", encoding="utf-8")
        init = subprocess.run(
            ["git", "init", "-q"],
            cwd=root,
            capture_output=True,
            text=True,
        )
        if init.returncode != 0:
            raise RuntimeError(
                f"git init failed while probing .vercelignore: {init.stderr.strip()}"
            )
        probe = subprocess.run(
            ["git", "check-ignore", "-q", normalized],
            cwd=root,
            capture_output=True,
            text=True,
        )
        if probe.returncode == 0:
            return True
        if probe.returncode == 1:
            return False
        raise RuntimeError(
            f"git check-ignore failed for {normalized!r}: {probe.stderr.strip()}"
        )


def iter_strings(value: object, path: str = "$"):
    if type(value) is str:
        yield path, value
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from iter_strings(item, f"{path}[{index}]")
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from iter_strings(item, f"{path}.{key}")


def check_demo(errors: list[str]) -> dict[str, object] | None:
    if not DEMO.exists():
        fail(errors, "season clock: public/assets/data/season_clock_demo.json is missing")
        return None
    try:
        payload = json.loads(DEMO.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(errors, f"season clock: demo JSON is unreadable: {exc}")
        return None
    if not isinstance(payload, dict):
        fail(errors, "season clock: demo payload must be an object")
        return None
    meta = payload.get("meta")
    if not isinstance(meta, dict) or meta.get("demo") is not True:
        fail(errors, "season clock: meta.demo must be true")
    honesty = meta.get("honesty") if isinstance(meta, dict) else None
    if type(honesty) is not str or "not endorsement" not in honesty.lower():
        fail(errors, "season clock: meta.honesty must deny endorsement/NIL claims")
    range_meta = meta.get("range") if isinstance(meta, dict) else None
    if not isinstance(range_meta, dict):
        fail(errors, "season clock: meta.range is required")
    else:
        if range_meta.get("start_year") != 2015 or range_meta.get("end_year") != 2025:
            fail(errors, "season clock: demo range must span 2015–2025")
    products = payload.get("products")
    if not isinstance(products, dict):
        fail(errors, "season clock: products map is required")
    else:
        for slug, url in PRODUCT_URLS.items():
            entry = products.get(slug)
            if not isinstance(entry, dict) or entry.get("url") != url:
                fail(errors, f"season clock: products.{slug}.url must be {url}")
    tracks = payload.get("tracks")
    if not isinstance(tracks, list):
        fail(errors, "season clock: tracks must be a list")
        return payload
    track_ids = tuple(
        item.get("id") for item in tracks if isinstance(item, dict)
    )
    if track_ids != EXPECTED_TRACK_IDS:
        fail(
            errors,
            f"season clock: expected tracks {EXPECTED_TRACK_IDS}, got {track_ids}",
        )
    for track in tracks:
        if not isinstance(track, dict):
            fail(errors, "season clock: every track must be an object")
            continue
        track_id = track.get("id")
        if track.get("kind") != EXPECTED_KINDS.get(track_id):
            fail(errors, f"season clock: track {track_id} has unexpected kind")
        events = track.get("events")
        if not isinstance(events, list) or not (2 <= len(events) <= 8):
            fail(
                errors,
                f"season clock: track {track_id} needs a small sample event set",
            )
            continue
        for event in events:
            if not isinstance(event, dict):
                fail(errors, f"season clock: track {track_id} has a non-object event")
                continue
            for field in ("id", "label", "entity", "start", "end"):
                value = event.get(field)
                if type(value) is not str or not value.strip():
                    fail(
                        errors,
                        f"season clock: track {track_id} event missing {field}",
                    )
            if (
                type(event.get("start")) is str
                and ISO_DAY.fullmatch(event["start"]) is None
            ) or (
                type(event.get("end")) is str
                and ISO_DAY.fullmatch(event["end"]) is None
            ):
                fail(
                    errors,
                    f"season clock: track {track_id} event dates must be YYYY-MM-DD",
                )
    for path, value in iter_strings(payload):
        matches = [
            pattern
            for pattern in FORBIDDEN_JSON
            if re.search(pattern, value, re.IGNORECASE)
        ]
        if matches:
            fail(
                errors,
                f"season clock: forbidden claim at {path}: {value!r}",
            )
    return payload


def check_page(errors: list[str]) -> None:
    if not PAGE.exists():
        fail(errors, "season clock: public/season-clock.html is missing")
        return
    text = PAGE.read_text(encoding="utf-8")
    lower = text.lower()
    for label, patterns in FORBIDDEN.items():
        matches = [
            pattern for pattern in patterns if re.search(pattern, text, re.IGNORECASE)
        ]
        if matches:
            fail(errors, f"season clock page: {label} remains ({', '.join(matches)})")
    if "<h1" not in lower or "season clock" not in lower:
        fail(errors, "season clock page: branded Season Clock heading is missing")
    if "named-window co-occurrence" not in lower and "not endorsement" not in lower:
        fail(errors, "season clock page: honesty disclaimer is missing")
    if 'id="year-scrub"' not in lower or 'min="2015"' not in lower or 'max="2025"' not in lower:
        fail(errors, "season clock page: year scrubber spanning 2015–2025 is missing")
    if "assets/data/season_clock_demo.json" not in lower:
        fail(errors, "season clock page: must fetch the committed demo JSON")
    for url in PRODUCT_URLS.values():
        if url not in text:
            fail(errors, f"season clock page: product link {url} is missing")
    if "unified.dumbmodel.com" in lower and 'href="https://unified.dumbmodel.com/' in lower:
        fail(errors, "season clock page: must not link Unified while unavailable")
    if "<canvas" in lower:
        fail(errors, "season clock page: canvas map claims are forbidden")
    if "@media (prefers-reduced-motion: reduce)" not in lower:
        fail(errors, "season clock page: reduced-motion handling is missing")
    if ":focus-visible" not in text:
        fail(errors, "season clock page: visible focus styling is missing")


def check_index_link(errors: list[str]) -> None:
    if not INDEX.exists():
        fail(errors, "season clock: public/index.html is missing")
        return
    text = INDEX.read_text(encoding="utf-8")
    if 'href="/season-clock.html"' not in text and 'href="season-clock.html"' not in text:
        fail(errors, "season clock: gateway index must link to Season Clock")
    if "nav-secondary" not in text:
        fail(errors, "season clock: gateway Season Clock link should be secondary nav")


def check_vercelignore(errors: list[str]) -> None:
    if not VERCELIGNORE.exists():
        fail(errors, "season clock deploy: .vercelignore is missing")
        return
    try:
        rules = VERCELIGNORE.read_text(encoding="utf-8")
        ignored = path_ignored_by_vercelignore(rules, DEMO_DEPLOY_PATH)
    except (OSError, RuntimeError) as exc:
        fail(errors, f"season clock deploy: {exc}")
        return
    if ignored:
        fail(
            errors,
            "season clock deploy: season_clock_demo.json must not be ignored by "
            ".vercelignore",
        )


def main() -> int:
    errors: list[str] = []
    check_demo(errors)
    check_page(errors)
    check_index_link(errors)
    check_vercelignore(errors)
    if errors:
        print(f"SEASON CLOCK CHECK FAILED ({len(errors)} invariant(s))")
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("SEASON CLOCK CHECK PASSED")
    print("PASS: demo JSON parses with sample tracks spanning 2015–2025")
    print("PASS: page exists with scrubber, product links, and honesty note")
    print("PASS: gateway index secondary nav points at Season Clock")
    print("PASS: .vercelignore keeps season_clock_demo.json packaged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
