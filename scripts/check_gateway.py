#!/usr/bin/env python3
"""Validate the served methodology notebook and remaining product-truth record."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "index.html"
STYLES = ROOT / "public" / "drafting.css"
PRODUCTS = ROOT / "public" / "assets" / "data" / "products.json"
VERCELIGNORE = ROOT / ".vercelignore"
PRODUCTS_DEPLOY_PATH = "public/assets/data/products.json"
SEASON_CLOCK_DEPLOY_PATH = "public/assets/data/season_clock_demo.json"
HEAVY_PUBLIC_DATA_PROBES = (
    "public/assets/data/hoops.json",
    "public/assets/data/boards_2026_08_18.json",
)
GATEWAY_JSON_KEEP = (PRODUCTS_DEPLOY_PATH, SEASON_CLOCK_DEPLOY_PATH)
EXPECTED = ("hoops", "gridiron", "pitch", "equities", "arcade", "unified")
AVAILABILITY = {"available", "unavailable", "unknown", "stale"}
# Pinned "measured" availability timestamp. This must be bumped together with
# public/assets/data/products.json whenever the availability record is
# refreshed: the pin is what stops stale availability data from shipping as
# fresh. See spec/vector-hub-real-product-gateway.md ("Contract maintenance").
AVAILABILITY_CHECKED_AT = "2026-10-07T22:56:47Z"
MEASURED_AVAILABILITY = {
    "hoops": "available",
    "gridiron": "available",
    "pitch": "available",
    "equities": "available",
    "arcade": "available",
    "unified": "available",
}
MEASURED_HTTP_STATUS = {
    "hoops": 200,
    "gridiron": 200,
    "pitch": 200,
    "equities": 200,
    "arcade": 200,
    "unified": 200,
}
URLS = {
    slug: {
        "url": f"https://{slug}.dumbmodel.com/",
        "evidence_url": f"https://github.com/jcdavis131/vector-{slug}",
    }
    for slug in EXPECTED
}
CANONICAL_COPY = {
    "hoops": {
        "name": "Hoops",
        "description": "12,966 NBA player-seasons on one interactive map. Play Twenty Questions, the Daily Court slate, or open packs in Pack Battle.",
    },
    "gridiron": {
        "name": "Gridiron",
        "description": "Every NFL player-season mapped by playing style. Find the quarterbacks, receivers, and defenders whose games mirror each other.",
    },
    "pitch": {
        "name": "Pitch",
        "description": "Clubs and tournaments mapped by how they actually play. Discover stylistic twins across leagues you thought had nothing in common.",
    },
    "equities": {
        "name": "Equities",
        "description": "Thousands of public companies mapped by behavior. Spot lookalikes hiding in different sectors.",
    },
    "arcade": {
        "name": "Arcade",
        "description": "Quick games on the same similarity engine. Five-minute plays, no learning curve.",
    },
    "unified": {
        "name": "Unified",
        "description": "One front door to every sports map. Start here and follow your curiosity.",
    },
}
RENDERED_FIELDS = (
    "slug",
    "name",
    "description",
    "url",
    "availability",
    "availability_checked_at",
    "availability_method",
    "evidence_url",
    "pushed_at",
)
SECTION_PAGES = (
    "index.html",
    "model.html",
    "embeddings.html",
    "era-twins.html",
    "career-trails.html",
    "forecasting.html",
    "data.html",
    "methodology.html",
    "provenance.html",
    "glossary.html",
)
SECTION_HREFS = (
    "/",
    "/model",
    "/embeddings",
    "/era-twins",
    "/career-trails",
    "/forecasting",
    "/data",
    "/methodology",
    "/provenance",
    "/glossary",
)
# Live served-model truth on vector-hoops master. Fetching beats a vendored
# pin: a promote that changes rows/model/built must fail this repo's CI even
# if nobody remembered to bump a checked-in copy. The files are public JSON
# (~15KB); CI retries the GET. mtnn_lineage.json is not on master yet.
HOOPS_TRUTH_REPO = "jcdavis131/vector-hoops"
HOOPS_TRUTH_REF = "master"
HOOPS_META_URL = (
    f"https://raw.githubusercontent.com/{HOOPS_TRUTH_REPO}/{HOOPS_TRUTH_REF}"
    "/assets/mtnn_meta.json"
)
HOOPS_LINEAGE_URL = (
    f"https://raw.githubusercontent.com/{HOOPS_TRUTH_REPO}/{HOOPS_TRUTH_REF}"
    "/assets/mtnn_lineage.json"
)
FETCH_ATTEMPTS = 3
FETCH_TIMEOUT_S = 15
# Not present in mtnn_meta.json or mtnn_lineage.json (lineage is unpublished
# on vector-hoops master as of 2026-10-18). Keep as literals until those
# files grow the fields. Era-twin count is len(assets/eratwins.json players);
# forecast MAE is assets/arc_forecasts_v1.json metrics.challenger.macro_mae.
LITERAL_HEADLINE_CLAIMS = (
    ("1,313", "era-twin players"),  # not in mtnn_meta.json / mtnn_lineage.json
    ("0.4382", "forecasting macro-MAE"),  # not in mtnn_meta.json / mtnn_lineage.json
    ("not a lab and not a storefront", "site purpose"),
)
STOREFRONT_URLS = tuple(f"https://{slug}.dumbmodel.com/" for slug in EXPECTED)
# Generated-map / fabricated-spec leaks remain forbidden on the served notebook.
# MTNN v5 is the documented champion and is pinned as a headline claim, not a leak.
FORBIDDEN = {
    "generated map": (r"<canvas\b", r"\b20[,\s]?719\b", r"\bgenerated layout\b"),
    "internal layout/model specification": (
        r"\bLCG\b",
        r"\bfusion\s+0\.",
        r"\bLOD\s*\d+",
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
# Narrow carve-out from the comma-formatted-count rule above. A hard count is
# honest only when it names a real, pinned, evidence-backed dataset a visitor
# can verify at the product's evidence_url. Each entry documents the claim and
# its evidence; anything not listed here still fails the gate.
VERIFIED_COUNT_CLAIMS = {
    "12,966": "hoops: 12,966 player-seasons = the 12,966x64 MTNN embedding asset served at the pinned vector-hoops evidence URL",
}
COMMA_COUNT_PATTERN = FORBIDDEN_JSON[0]
UTC_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
TARGET_SELECTORS = (".skip", ".brand", ".nav .links a", ".toggle")


class GatewayParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: list[str] = []
        self.attrs: list[tuple[str, dict[str, str]]] = []
        self.headings: list[int] = []
        self.hrefs: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        values = {key: value or "" for key, value in attrs}
        self.tags.append(tag)
        self.attrs.append((tag, values))
        if re.fullmatch(r"h[1-6]", tag):
            self.headings.append(int(tag[1]))
        if tag == "a":
            self.hrefs.append(values.get("href", ""))


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def fetch_json(url: str, *, required: bool) -> dict[str, object] | None:
    """GET JSON from public GitHub raw. 404 on an optional file returns None."""
    headers = {
        "User-Agent": "vector-hub-gateway-check/1.0 (+https://github.com/jcdavis131/vector-hub)",
        "Accept": "application/json",
    }
    last_error: Exception | None = None
    for attempt in range(FETCH_ATTEMPTS):
        try:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=FETCH_TIMEOUT_S) as response:
                payload = json.loads(response.read().decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError(f"{url} is not a JSON object")
            return payload
        except urllib.error.HTTPError as exc:
            if exc.code == 404 and not required:
                return None
            last_error = exc
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            last_error = exc
    raise RuntimeError(f"could not fetch {url}: {last_error}")


def load_served_model_truth() -> tuple[dict[str, object] | None, dict[str, object] | None]:
    """Return (mtnn_meta.json, mtnn_lineage.json-or-None) from vector-hoops master."""
    meta = fetch_json(HOOPS_META_URL, required=True)
    lineage = fetch_json(HOOPS_LINEAGE_URL, required=False)
    return meta, lineage


def champion_copy(model: object) -> str | None:
    if type(model) is not str:
        return None
    match = re.match(r"mtnn_v(\d+)", model, re.IGNORECASE)
    if match is None:
        return None
    return f"MTNN v{match.group(1)}"


def comma_count(rows: object) -> str | None:
    if type(rows) is not int or rows < 0:
        return None
    return f"{rows:,}"


def headline_claims_from_truth(
    meta: dict[str, object] | None,
    lineage: dict[str, object] | None,
    errors: list[str],
) -> list[tuple[str, str]]:
    """Build page pins from served-model files; literals fill gaps those files lack."""
    _ = lineage  # no headline fields on master yet; see LITERAL_HEADLINE_CLAIMS
    claims: list[tuple[str, str]] = []
    if meta is None:
        fail(errors, "served-model truth: mtnn_meta.json could not be loaded")
        return list(LITERAL_HEADLINE_CLAIMS)
    rows_copy = comma_count(meta.get("rows"))
    if rows_copy is None:
        fail(
            errors,
            "served-model truth: mtnn_meta.json rows must be a non-negative int",
        )
    else:
        claims.append((rows_copy, "player-seasons count"))
    model_copy = champion_copy(meta.get("model"))
    if model_copy is None:
        fail(
            errors,
            "served-model truth: mtnn_meta.json model must look like mtnn_vN_…",
        )
    else:
        claims.append((model_copy, "champion model"))
    built = meta.get("built")
    if type(built) is not str or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", built):
        fail(
            errors,
            "served-model truth: mtnn_meta.json built must be a YYYY-MM-DD date",
        )
    else:
        claims.append((built, "incumbent date"))
    claims.extend(LITERAL_HEADLINE_CLAIMS)
    return claims


def path_ignored_by_vercelignore(rules_text: str, relative_path: str) -> bool:
    """Return True if gitignore-style .vercelignore rules ignore relative_path.

    Vercel applies .vercelignore with gitignore semantics. Using git
    check-ignore in an ephemeral repo keeps the gate stdlib-only and faithful.
    """
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


def check_vercelignore(errors: list[str]) -> None:
    if not VERCELIGNORE.exists():
        fail(errors, "deploy packaging: .vercelignore is missing")
        return
    try:
        rules = VERCELIGNORE.read_text(encoding="utf-8")
    except OSError as exc:
        fail(errors, f"deploy packaging: .vercelignore is unreadable: {exc}")
        return
    try:
        keep_results = {
            path: path_ignored_by_vercelignore(rules, path)
            for path in GATEWAY_JSON_KEEP
        }
        heavy_results = {
            probe: path_ignored_by_vercelignore(rules, probe)
            for probe in HEAVY_PUBLIC_DATA_PROBES
        }
    except RuntimeError as exc:
        fail(errors, f"deploy packaging: {exc}")
        return
    for path, ignored in keep_results.items():
        if ignored:
            fail(
                errors,
                f"deploy packaging: {path} must not be ignored by .vercelignore "
                "(bare data/ strips gateway JSON)",
            )
    for probe, ignored in heavy_results.items():
        if not ignored:
            fail(
                errors,
                f"deploy packaging: {probe} must remain ignored by .vercelignore",
            )


def parse_timestamp(value: object) -> datetime | None:
    if type(value) is not str or UTC_TIMESTAMP.fullmatch(value) is None:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def iter_strings(value: object, path: str = "$"):
    if type(value) is str:
        yield path, value
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from iter_strings(item, f"{path}[{index}]")
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from iter_strings(item, f"{path}.{key}")


def contrast(hex_a: str, hex_b: str) -> float:
    def luminance(value: str) -> float:
        channels = [int(value[index : index + 2], 16) / 255 for index in (1, 3, 5)]
        linear = [
            c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
            for c in channels
        ]
        return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

    light, dark = sorted((luminance(hex_a), luminance(hex_b)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def check_products(errors: list[str]) -> list[dict[str, object]]:
    if not PRODUCTS.exists():
        fail(errors, "product truth: public/assets/data/products.json is missing")
        return []
    try:
        payload = json.loads(PRODUCTS.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(errors, f"product truth: products.json is unreadable: {exc}")
        return []
    products = payload.get("products") if isinstance(payload, dict) else None
    if not isinstance(products, list):
        fail(errors, "product truth: top-level products must be a list")
        return []
    slugs = tuple(item.get("slug") for item in products if isinstance(item, dict))
    if len(products) != 6 or set(slugs) != set(EXPECTED) or len(set(slugs)) != 6:
        fail(errors, f"product truth: expected exactly {EXPECTED}, got {slugs}")
    for item in products:
        if not isinstance(item, dict):
            fail(errors, "product truth: every product must be an object")
            continue
        slug_value = item.get("slug")
        slug = slug_value if type(slug_value) is str else "<invalid>"
        for field in RENDERED_FIELDS:
            value = item.get(field)
            if type(value) is not str or not value.strip():
                fail(errors, f"product truth: {slug} {field} must be a non-empty string")
        if item.get("availability_method") != "GET":
            fail(errors, f"product truth: {slug} availability_method must be exact GET")
        expected_http_status = MEASURED_HTTP_STATUS.get(slug)
        if (
            type(item.get("availability_http_status")) is not int
            or item.get("availability_http_status") != expected_http_status
        ):
            fail(
                errors,
                f"product truth: {slug} availability_http_status must match measured "
                f"{expected_http_status}",
            )
        expected_urls = URLS.get(slug)
        if expected_urls is None:
            fail(errors, f"product truth: {slug} has no pinned URL association")
        else:
            for field, expected_url in expected_urls.items():
                if item.get(field) != expected_url:
                    fail(
                        errors,
                        f"product truth: {slug} {field} violates exact URL mapping "
                        f"(expected {expected_url!r})",
                    )
        expected_copy = CANONICAL_COPY.get(slug)
        if expected_copy is None:
            fail(errors, f"product truth: {slug} has no canonical copy association")
        else:
            for field, expected_value in expected_copy.items():
                if item.get(field) != expected_value:
                    fail(
                        errors,
                        f"product truth: {slug} violates canonical {field} "
                        f"(expected {expected_value!r})",
                    )
        if item.get("availability") not in AVAILABILITY:
            fail(errors, f"product truth: {slug} has invalid availability")
        expected_availability = MEASURED_AVAILABILITY.get(slug)
        if item.get("availability") != expected_availability:
            fail(
                errors,
                f"product truth: {slug} does not match measured availability "
                f"{expected_availability!r}",
            )
        availability_checked_at = parse_timestamp(
            item.get("availability_checked_at")
        )
        if availability_checked_at is None:
            fail(
                errors,
                f"product truth: {slug} availability_checked_at must be an "
                "ISO-8601 UTC timestamp",
            )
        elif availability_checked_at > datetime.now(timezone.utc):
            fail(
                errors,
                f"product truth: {slug} availability_checked_at is in the future",
            )
        elif item.get("availability_checked_at") != AVAILABILITY_CHECKED_AT:
            fail(
                errors,
                f"product truth: {slug} availability_checked_at does not match "
                "the measured HTTP check",
            )
        pushed_at = parse_timestamp(item.get("pushed_at"))
        if pushed_at is None:
            fail(
                errors,
                f"product truth: {slug} pushed_at must be an ISO-8601 UTC timestamp",
            )
        elif pushed_at > datetime.now(timezone.utc):
            fail(errors, f"product truth: {slug} pushed_at is in the future")
        unsupported = set(item) & {"count", "score", "metric", "model", "dimensions"}
        if unsupported:
            fail(errors, f"product truth: {slug} contains unsupported claims {sorted(unsupported)}")
    for path, value in iter_strings(payload):
        matches = []
        for pattern in FORBIDDEN_JSON:
            found = re.findall(pattern, value, re.IGNORECASE)
            if not found:
                continue
            if pattern == COMMA_COUNT_PATTERN and all(
                hit in VERIFIED_COUNT_CLAIMS for hit in found
            ):
                continue
            matches.append(pattern)
        if matches:
            fail(
                errors,
                f"product truth: forbidden rendered claim at {path}: {value!r}",
            )
    return products


def check_markup(errors: list[str], text: str, label: str) -> GatewayParser:
    parser = GatewayParser()
    parser.feed(text)
    for forbidden_label, patterns in FORBIDDEN.items():
        matches = [
            pattern for pattern in patterns if re.search(pattern, text, re.IGNORECASE)
        ]
        if matches:
            fail(
                errors,
                f"{label}: {forbidden_label} remains ({', '.join(matches)})",
            )
    required_landmarks = {"nav", "main", "footer"}
    missing = required_landmarks - set(parser.tags)
    if missing:
        fail(errors, f"{label}: missing landmarks {sorted(missing)}")
    skip_links = [
        attrs
        for tag, attrs in parser.attrs
        if tag == "a" and attrs.get("href") == "#main"
    ]
    if not skip_links:
        fail(errors, f"{label}: no skip link targets #main")
    if parser.headings.count(1) != 1:
        fail(errors, f"{label}: expected one h1, found {parser.headings.count(1)}")
    if any(b - a > 1 for a, b in zip(parser.headings, parser.headings[1:])):
        fail(errors, f"{label}: heading levels skip in sequence {parser.headings}")
    return parser


def check_page(errors: list[str], _products: list[dict[str, object]]) -> None:
    """Page contract for the methodology notebook (Drafting Board shell).

    Re-baselined 2026-10-18 after PR #24 replaced the product-hub landing page
    with the hoops methodology notebook. Honesty substance is preserved:

    - headline numbers for rows / champion / incumbent date come from
      vector-hoops mtnn_meta.json (and mtnn_lineage.json when present);
    - the home is an explanation site, not a six-product storefront;
    - generated-map and fabricated-spec leaks remain forbidden;
    - accessibility (skip link, focus, 44px targets, reduced motion,
      overflow-wrap, contrast) still applies, now against drafting.css.
    """
    if not PAGE.exists():
        fail(errors, "served page: public/index.html is missing")
        return
    try:
        meta, lineage = load_served_model_truth()
    except RuntimeError as exc:
        fail(errors, f"served-model truth: {exc}")
        meta, lineage = None, None
    claims = headline_claims_from_truth(meta, lineage, errors)
    text = PAGE.read_text(encoding="utf-8")
    parser = check_markup(errors, text, "served journey")

    for claim, label in claims:
        if claim not in text:
            fail(errors, f"methodology truth: missing pinned {label} ({claim!r})")
    if "vector product family" in text.lower():
        fail(errors, "cut list: product-hub 'vector product family' framing remains")
    for url in STOREFRONT_URLS:
        if url in text:
            fail(errors, f"cut list: storefront CTA {url} remains on the methodology home")
    missing_sections = [href for href in SECTION_HREFS if href not in parser.hrefs]
    if missing_sections:
        fail(errors, f"section nav: missing notebook links {missing_sections}")

    if not STYLES.exists():
        fail(errors, "served styles: public/drafting.css is missing")
        return
    css = STYLES.read_text(encoding="utf-8")
    combined = f"{text}\n{css}"
    lower = combined.lower()

    if ":focus-visible" not in combined:
        fail(errors, "accessibility: visible focus styling is missing")
    for selector in TARGET_SELECTORS:
        match = re.search(
            rf"{re.escape(selector)}\s*\{{([^}}]+)\}}", css, re.IGNORECASE
        )
        body = match.group(1).lower() if match else ""
        heights = [int(value) for value in re.findall(r"min-height\s*:\s*(\d+)px", body)]
        widths = [int(value) for value in re.findall(r"min-width\s*:\s*(\d+)px", body)]
        if not heights or not widths or min(heights) < 44 or min(widths) < 44:
            label = selector.removeprefix(".").replace(".", " ")
            fail(errors, f"accessibility: {label} target is not guaranteed 44px square")
    if "@media (prefers-reduced-motion: reduce)" not in lower:
        fail(errors, "accessibility: reduced-motion handling is missing")
    if re.search(r"overflow-x\s*:\s*hidden", lower):
        fail(errors, "responsive layout: horizontal overflow clipping conceals defects")
    if "overflow-wrap:anywhere" not in lower:
        fail(errors, "responsive layout: long URLs/text can cause horizontal overflow")
    if re.search(r"grid-template-columns:\s*repeat\([^,]+,\s*minmax\((?!0)", lower):
        fail(errors, "responsive layout: grid tracks need minmax(0, ...) to shrink")

    colors = {
        name: match.group(1)
        for name in ("paper", "ink", "ink-60")
        if (match := re.search(rf"--{re.escape(name)}:\s*(#[0-9a-fA-F]{{6}})", css))
    }
    if set(colors) != {"paper", "ink", "ink-60"}:
        fail(errors, "contrast: required Japandi text/background tokens are missing")
        return
    for foreground in ("ink", "ink-60"):
        ratio = contrast(colors[foreground], colors["paper"])
        if ratio < 4.5:
            fail(errors, f"contrast: {foreground} on paper is {ratio:.2f}:1, below 4.5:1")


def check_notebook(errors: list[str]) -> None:
    public = ROOT / "public"
    for name in SECTION_PAGES:
        path = public / name
        if not path.exists():
            fail(errors, f"notebook: public/{name} is missing")
            continue
        if name == "index.html":
            continue
        text = path.read_text(encoding="utf-8")
        check_markup(errors, text, f"notebook {name}")


def main() -> int:
    errors: list[str] = []
    products = check_products(errors)
    check_page(errors, products)
    check_notebook(errors)
    check_vercelignore(errors)
    if errors:
        print(f"GATEWAY CHECK FAILED ({len(errors)} invariant(s))")
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("GATEWAY CHECK PASSED")
    print("PASS: six evidence-backed product records remain internally consistent")
    print("PASS: methodology headlines match vector-hoops served-model truth")
    print("PASS: semantic, focus, motion, target, contrast, and overflow contracts")
    print("PASS: .vercelignore keeps products.json and season_clock_demo.json while ignoring heavy public datasets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
