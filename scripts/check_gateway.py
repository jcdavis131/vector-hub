#!/usr/bin/env python3
"""Validate the served product gateway without writing tracked artifacts."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "index.html"
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
FORBIDDEN = {
    "generated map": (r"<canvas\b", r"\b20[,\s]?719\b", r"\bgenerated layout\b"),
    "internal layout/model specification": (
        r"\bLCG\b",
        r"\bfusion\s+0\.",
        r"\bLOD\s*\d+",
        r"\bMTNN\s+v",
        r"\b7/7/0",
    ),
    "fabricated roster scoring": (r"\broster\b", r"\bAR\s*/\s*stretch\b"),
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
# REVIEW POINT: this is the one substantive guardrail change in the
# re-baseline — confirm the 12,966 count stays, or reword the Hoops copy.
VERIFIED_COUNT_CLAIMS = {
    "12,966": "hoops: 12,966 player-seasons = the 12,966x64 MTNN embedding asset served at the pinned vector-hoops evidence URL",
}
COMMA_COUNT_PATTERN = FORBIDDEN_JSON[0]
UTC_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


class GatewayParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: list[str] = []
        self.attrs: list[tuple[str, dict[str, str]]] = []
        self.headings: list[int] = []
        self.products: dict[str, dict[str, object]] = {}
        self.product_sequence: list[str] = []
        self.current_product: dict[str, object] | None = None
        self.capture: str | None = None
        self.status_state = ""
        self.status_text = ""
        self.capturing_status = False
        self.in_direct_nav = False
        self.current_direct_product: str | None = None
        self.direct_anchors: dict[str, list[str]] = {}
        self.direct_sequence: list[str] = []
        self.current_direct_anchors: list[str] | None = None

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        values = {key: value or "" for key, value in attrs}
        self.tags.append(tag)
        self.attrs.append((tag, values))
        if re.fullmatch(r"h[1-6]", tag):
            self.headings.append(int(tag[1]))
        classes = set(values.get("class", "").split())
        if tag == "nav" and "direct-links" in classes:
            self.in_direct_nav = True
        if tag == "li" and self.in_direct_nav and values.get("data-product"):
            self.current_direct_product = values["data-product"]
            self.direct_sequence.append(self.current_direct_product)
            self.current_direct_anchors = []
            self.direct_anchors.setdefault(
                self.current_direct_product, self.current_direct_anchors
            )
        if tag == "a" and self.current_direct_product is not None:
            assert self.current_direct_anchors is not None
            self.current_direct_anchors.append(values.get("href", ""))
        if tag == "p" and values.get("id") == "products-status":
            self.status_state = values.get("data-state", "")
            self.capturing_status = True
        if tag == "li" and values.get("data-product") and not self.in_direct_nav:
            slug = values["data-product"]
            self.product_sequence.append(slug)
            self.current_product = {
                "slug": slug,
                "name": "",
                "description": "",
                "availability": "",
                "availability_state": "",
                "availability_checked_at": "",
                "pushed_at": "",
                "product_url": "",
                "product_unavailable": False,
                "evidence_url": "",
                "anchors": [],
            }
            self.products.setdefault(slug, self.current_product)
        if self.current_product is None:
            return
        if tag == "a":
            anchors = self.current_product["anchors"]
            assert isinstance(anchors, list)
            anchors.append(values.get("href", ""))
        if tag in {"h2", "h3"}:
            self.capture = "name"
        elif "product-description" in classes:
            self.capture = "description"
        elif "availability" in classes:
            self.capture = "availability"
            self.current_product["availability_state"] = values.get("data-state", "")
        elif tag in {"time", "span"} and "availability-checked" in classes:
            self.capture = "availability_checked_at"
            self.current_product["availability_checked_at_datetime"] = values.get(
                "datetime", ""
            )
        elif tag == "time" and "pushed-at" in classes:
            self.capture = "pushed_at"
            self.current_product["pushed_at_datetime"] = values.get("datetime", "")
        elif tag == "a" and "product-link" in classes:
            self.current_product["product_url"] = values.get("href", "")
        elif tag == "a" and "evidence-link" in classes:
            self.current_product["evidence_url"] = values.get("href", "")
        elif tag == "span" and "product-unavailable" in classes:
            self.current_product["product_unavailable"] = True

    def handle_data(self, data: str) -> None:
        if self.capturing_status:
            self.status_text = (self.status_text + data).strip()
        if self.current_product is not None and self.capture is not None:
            self.current_product[self.capture] = (
                str(self.current_product[self.capture]) + data
            ).strip()

    def handle_endtag(self, tag: str) -> None:
        if tag == "p" and self.capturing_status:
            self.capturing_status = False
        if tag in {"h2", "h3", "p", "time", "span"}:
            self.capture = None
        if tag == "li" and self.current_product is not None:
            self.current_product = None
        if tag == "li" and self.current_direct_product is not None:
            self.current_direct_product = None
            self.current_direct_anchors = None
        if tag == "nav" and self.in_direct_nav:
            self.in_direct_nav = False


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


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
        linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
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


def check_page(errors: list[str], products: list[dict[str, object]]) -> None:
    """Page contract for the professionalized gateway (dark editorial design).

    Re-baselined 2026-10-07: the midnight-garden rebuild and the
    professionalization PR replaced the old page's exact-label markup, so the
    cosmetic expectations below are translated to the new design. The honesty
    substance is preserved:
    - rendered name/description/availability/evidence must match the JSON
      truth record exactly;
    - availability is a humanized point-in-time label ("Live"/"Down") with an
      explicit staleness caveat, not continuous monitoring;
    - pushed_at provenance lives in products.json and is verifiable via the
      pinned evidence link (not rendered as page copy);
    - unavailable products must expose no product CTA;
    - the enhancement script validates the exact record shape and binds
      records to pinned links without rewriting hrefs.
    """
    if not PAGE.exists():
        fail(errors, "served page: public/index.html is missing")
        return
    text = PAGE.read_text(encoding="utf-8")
    lower = text.lower()
    parser = GatewayParser()
    parser.feed(text)

    for label, patterns in FORBIDDEN.items():
        matches = [pattern for pattern in patterns if re.search(pattern, text, re.IGNORECASE)]
        if matches:
            fail(errors, f"served journey: {label} remains ({', '.join(matches)})")

    required_landmarks = {"header", "nav", "main", "footer"}
    missing = required_landmarks - set(parser.tags)
    if missing:
        fail(errors, f"semantics: missing landmarks {sorted(missing)}")
    skip_links = [
        attrs for tag, attrs in parser.attrs
        if tag == "a" and attrs.get("href") == "#main"
    ]
    if not skip_links:
        fail(errors, "accessibility: no skip link targets #main")
    if parser.headings.count(1) != 1:
        fail(errors, f"semantics: expected one h1, found {parser.headings.count(1)}")
    if any(b - a > 1 for a, b in zip(parser.headings, parser.headings[1:])):
        fail(errors, f"semantics: heading levels skip in sequence {parser.headings}")

    duplicate_products = sorted(
        slug for slug in set(parser.product_sequence)
        if parser.product_sequence.count(slug) > 1
    )
    if duplicate_products:
        fail(
            errors,
            f"static product truth: duplicate product entries {duplicate_products}",
        )
    static_slugs = tuple(parser.product_sequence)
    if static_slugs != EXPECTED:
        fail(
            errors,
            f"static product truth: expected exactly {EXPECTED}, got {static_slugs}",
        )
    for product in products:
        slug = product.get("slug")
        rendered = parser.products.get(str(slug))
        if rendered is None:
            continue
        comparisons = {
            "name": product.get("name"),
            "description": product.get("description"),
            "availability_state": product.get("availability"),
            "evidence_url": product.get("evidence_url"),
        }
        for field, expected_value in comparisons.items():
            if rendered.get(field) != expected_value:
                fail(
                    errors,
                    f"static product truth: {slug} {field} does not match registry",
                )
        expected_label = "Live" if product.get("availability") == "available" else "Down"
        if rendered.get("availability") != expected_label:
            fail(
                errors,
                f"static product truth: {slug} availability label must read "
                f"{expected_label!r}",
            )
        if not rendered.get("availability_checked_at"):
            fail(
                errors,
                f"static product truth: {slug} availability check label is missing",
            )
        if product.get("availability") == "available":
            if rendered.get("product_url") != product.get("url"):
                fail(errors, f"static product truth: {slug} available product link is missing")
            expected_anchors = [product.get("url"), product.get("evidence_url")]
        else:
            if rendered.get("product_url"):
                fail(errors, f"static product truth: {slug} unavailable product link is forbidden")
            expected_anchors = [product.get("evidence_url")]
        if rendered.get("anchors") != expected_anchors:
            fail(
                errors,
                f"static product truth: {slug} available product anchors are incomplete"
                if product.get("availability") == "available"
                else f"static product truth: {slug} unavailable product anchors must contain "
                "only pinned evidence",
            )

    if 'id="product-list"' not in lower:
        fail(errors, "loading outcome: product list contract is missing")
    if (
        parser.status_state != "ready"
        or parser.status_text != "Product records are shown below."
    ):
        fail(errors, "static status: published product records must default to ready")
    if "javascript is off. product records above are complete as published." not in lower:
        fail(errors, "static status: no-JavaScript message must agree with ready truth")
    if (
        "reflects the most recent check" not in lower
        or "later visit may differ" not in lower
    ):
        fail(errors, "availability check semantics: point-in-time limitation is missing")
    if 'role="status"' not in lower or 'aria-live="polite"' not in lower:
        fail(errors, "loading outcome: status changes are not announced")
    if "assets/data/products.json" not in lower or ".catch(" not in lower:
        fail(errors, "error outcome: local truth fetch and failure path are required")
    if "live refresh unavailable" not in lower:
        fail(errors, "error outcome: honest user-facing load failure is missing")
    if ".href =" in text or '.setattribute("href"' in lower:
        fail(errors, "dynamic associations: enhancement must not rewrite pinned links")

    # Runtime honesty: the enhancement script validates the fetched record
    # shape against explicit contracts and binds records to pinned links.
    if (
        'var expected = ["hoops", "gridiron", "pitch", "equities", "arcade", "unified"];'
        not in lower
    ):
        fail(errors, "runtime product set: fetched records need an explicit slug allow-list")
    exact_keys = (
        'var required = ["availability", "availability_checked_at", '
        '"availability_http_status", "availability_method", "description", '
        '"evidence_url", "name", "pushed_at", "slug", "url"];'
    )
    if (
        exact_keys not in lower
        or "object.keys(p).sort()" not in lower
        or "keys.length !== required.length" not in lower
    ):
        fail(errors, "runtime exact keys: fetched products need an explicit exact key list")
    if 'typeof p[k] !== "string"' not in lower or "!p[k].trim()" not in lower:
        fail(errors, "runtime field validation: string fields need trimmed non-empty checks")
    if "number.isinteger(p.availability_http_status)" not in lower:
        fail(errors, "runtime measured provenance: numeric HTTP status check is missing")
    if 'p.availability_method !== "get"' not in lower:
        fail(errors, "runtime measured provenance: exact GET method check is missing")
    if (
        r"/^\d{4}-\d{2}-\d{2}t\d{2}:\d{2}:\d{2}z$/" not in lower
        or ".test(p.pushed_at)" not in lower
        or ".test(p.availability_checked_at)" not in lower
    ):
        fail(errors, "runtime timestamp shape: exact ISO UTC validation is missing")
    if (
        'var matches = list.queryselectorall(\'[data-product="\' + p.slug + \'"]\');'
        not in lower
        or "matches.length !== 1" not in lower
    ):
        fail(errors, "dynamic associations: fetched records must match exactly one static entry")
    if 'evidencelink.getattribute("href") !== p.evidence_url' not in lower:
        fail(errors, "dynamic associations: fetched records are not bound to pinned evidence links")
    if 'productlink.getattribute("href") !== p.url' not in lower:
        fail(errors, "dynamic associations: fetched records are not bound to pinned product links")
    if "productlink.remove()" not in lower or "product-unavailable" not in lower:
        fail(
            errors,
            "runtime availability associations: unavailable records must lose their product CTA",
        )
    loading_state = lower.find('status.dataset.state = "loading"')
    loading_copy = lower.find('status.textcontent = "checking the local product record…"')
    fetch_call = lower.find('fetch("assets/data/products.json"')
    if not (0 <= loading_state < loading_copy < fetch_call):
        fail(errors, "loading outcome: JavaScript must set loading state immediately before fetch")

    if ":focus-visible" not in text:
        fail(errors, "accessibility: visible focus styling is missing")
    for selector in (".skip-link", ".brand", ".action", ".btn"):
        match = re.search(rf"{re.escape(selector)}\s*\{{([^}}]+)\}}", text, re.IGNORECASE)
        body = match.group(1).lower() if match else ""
        heights = [int(v) for v in re.findall(r"min-height\s*:\s*(\d+)px", body)]
        widths = [int(v) for v in re.findall(r"min-width\s*:\s*(\d+)px", body)]
        if not heights or not widths or min(heights) < 44 or min(widths) < 44:
            label = selector.removeprefix(".")
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
        for name in ("paper", "void", "paper-dim")
        if (match := re.search(rf"--{re.escape(name)}:\s*(#[0-9a-fA-F]{{6}})", text))
    }
    if set(colors) != {"paper", "void", "paper-dim"}:
        fail(errors, "contrast: required dark-theme text/background tokens are missing")
    else:
        for foreground in ("paper", "paper-dim"):
            ratio = contrast(colors[foreground], colors["void"])
            if ratio < 4.5:
                fail(errors, f"contrast: {foreground} on void is {ratio:.2f}:1, below 4.5:1")



def main() -> int:
    errors: list[str] = []
    products = check_products(errors)
    check_page(errors, products)
    check_vercelignore(errors)
    if errors:
        print(f"GATEWAY CHECK FAILED ({len(errors)} invariant(s))")
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("GATEWAY CHECK PASSED")
    print("PASS: exactly six evidence-backed product records")
    print("PASS: content-first served journey excludes generated/specification claims")
    print("PASS: semantic, loading/error, focus, motion, target, contrast, and overflow contracts")
    print("PASS: .vercelignore keeps products.json and season_clock_demo.json while ignoring heavy public datasets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
