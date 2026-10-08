from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "check_gateway", ROOT / "scripts" / "check_gateway.py"
)
assert SPEC and SPEC.loader
check_gateway = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check_gateway)


class GatewayCheckerAdversarialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(
            (ROOT / "public" / "assets" / "data" / "products.json").read_text(
                encoding="utf-8"
            )
        )

    def product_errors(self, mutate) -> list[str]:
        payload = copy.deepcopy(self.payload)
        mutate(payload["products"])
        with tempfile.TemporaryDirectory() as directory:
            product_file = Path(directory) / "products.json"
            product_file.write_text(json.dumps(payload), encoding="utf-8")
            errors: list[str] = []
            with patch.object(check_gateway, "PRODUCTS", product_file):
                check_gateway.check_products(errors)
        return errors

    def page_errors(self, mutate) -> list[str]:
        page = (ROOT / "public" / "index.html").read_text(encoding="utf-8")
        page = mutate(page)
        with tempfile.TemporaryDirectory() as directory:
            page_file = Path(directory) / "index.html"
            page_file.write_text(page, encoding="utf-8")
            errors: list[str] = []
            products = check_gateway.check_products(errors)
            with patch.object(check_gateway, "PAGE", page_file):
                check_gateway.check_page(errors, products)
        return errors

    def test_rejects_numeric_rendered_fields(self) -> None:
        errors = self.product_errors(
            lambda products: products[0].update(name=2026)
        )
        self.assertTrue(
            any("name must be a non-empty string" in error for error in errors),
            errors,
        )

    def test_rejects_ordinary_count_claim_in_description(self) -> None:
        errors = self.product_errors(
            lambda products: products[0].update(
                description="Explore 99 basketball players."
            )
        )
        self.assertTrue(
            any("canonical description" in error for error in errors),
            errors,
        )

    def test_rejects_score_claim_in_description(self) -> None:
        errors = self.product_errors(
            lambda products: products[0].update(
                description="Explore basketball players with similarity score 9.2."
            )
        )
        self.assertTrue(
            any("forbidden rendered claim" in error for error in errors),
            errors,
        )

    def test_rejects_specification_claim_in_description(self) -> None:
        errors = self.product_errors(
            lambda products: products[0].update(
                description="Explore basketball players with fusion 0.60."
            )
        )
        self.assertTrue(
            any("forbidden rendered claim" in error for error in errors),
            errors,
        )

    def test_rejects_swapped_product_and_evidence_urls(self) -> None:
        def swap(products) -> None:
            products[0]["url"], products[1]["url"] = (
                products[1]["url"],
                products[0]["url"],
            )
            products[0]["evidence_url"], products[1]["evidence_url"] = (
                products[1]["evidence_url"],
                products[0]["evidence_url"],
            )

        errors = self.product_errors(swap)
        self.assertTrue(any("exact URL mapping" in error for error in errors), errors)

    def test_rejects_phishing_url_components(self) -> None:
        errors = self.product_errors(
            lambda products: products[0].update(
                url="https://user@hoops.dumbmodel.com/?next=gridiron#open"
            )
        )
        self.assertTrue(any("exact URL mapping" in error for error in errors), errors)

    def test_rejects_future_repository_timestamp(self) -> None:
        errors = self.product_errors(
            lambda products: products[0].update(
                pushed_at="2999-01-01T00:00:00Z"
            )
        )
        self.assertTrue(any("future" in error for error in errors), errors)

    def test_requires_target_size_for_each_interactive_contract(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                ".brand {\n  min-width:44px; min-height:44px;",
                ".brand {",
                1,
            )
        )
        self.assertTrue(
            any("brand target" in error for error in errors),
            errors,
        )

    def test_rejects_horizontal_overflow_clipping(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                "html { scroll-behavior:smooth; }",
                "html { scroll-behavior:smooth; overflow-x:hidden; }",
                1,
            )
        )
        self.assertTrue(
            any("overflow clipping" in error for error in errors),
            errors,
        )

    def test_requires_complete_static_product_truth(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                "12,966 NBA player-seasons on one interactive map.",
                "",
                1,
            )
        )
        self.assertTrue(
            any("static product truth" in error for error in errors),
            errors,
        )

    def test_rejects_swapped_static_product_link(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                'product-link" href="https://hoops.dumbmodel.com/">Open Hoops',
                'product-link" href="https://gridiron.dumbmodel.com/">Open Hoops',
                1,
            )
        )
        self.assertTrue(
            any("static product truth: hoops available product link" in error for error in errors),
            errors,
        )

    def test_requires_dynamic_link_association_guard(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                'evidenceLink.getAttribute("href") !== p.evidence_url',
                "true",
                1,
            )
        )
        self.assertTrue(
            any("dynamic associations" in error for error in errors),
            errors,
        )

    def test_requires_truthful_ready_static_status(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                'data-state="ready">Product records are shown below.',
                'data-state="loading">Checking the local product record…',
                1,
            )
        )
        self.assertTrue(any("static status" in error for error in errors), errors)

    def test_requires_runtime_exact_key_contract(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                'var required = ["availability", "availability_checked_at", '
                '"availability_http_status", "availability_method", "description", '
                '"evidence_url", "name", "pushed_at", "slug", "url"];',
                "",
                1,
            )
        )
        self.assertTrue(any("runtime exact keys" in error for error in errors), errors)

    def test_requires_runtime_name_validation(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                'typeof p[k] !== "string"',
                "false",
                1,
            )
        )
        self.assertTrue(any("runtime field validation" in error for error in errors), errors)

    def test_requires_runtime_description_validation(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                '"description", "evidence_url"',
                '"description"',
                1,
            )
        )
        self.assertTrue(any("runtime exact keys" in error for error in errors), errors)

    def test_requires_runtime_exact_utc_timestamp_shape(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                "isoUtc.test(p.pushed_at)",
                "true",
                1,
            )
        )
        self.assertTrue(any("runtime timestamp shape" in error for error in errors), errors)

    def test_requires_availability_checked_at(self) -> None:
        errors = self.product_errors(
            lambda products: products[0].pop("availability_checked_at")
        )
        self.assertTrue(
            any("availability_checked_at" in error for error in errors),
            errors,
        )

    def test_rejects_future_availability_check(self) -> None:
        errors = self.product_errors(
            lambda products: products[0].update(
                availability_checked_at="2999-01-01T00:00:00Z"
            )
        )
        self.assertTrue(
            any("availability_checked_at is in the future" in error for error in errors),
            errors,
        )

    def test_requires_measured_availability_states(self) -> None:
        errors = self.product_errors(
            lambda products: products[0].update(availability="unavailable")
        )
        self.assertTrue(
            any("measured availability" in error for error in errors),
            errors,
        )

    def test_unified_static_record_requires_product_link(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                '<a class="action action--primary product-link" '
                'href="https://unified.dumbmodel.com/">Open Unified</a>',
                '<span class="product-unavailable">Product unavailable</span>',
                1,
            )
        )
        self.assertTrue(
            any("static product truth" in error for error in errors),
            errors,
        )

    def test_requires_static_availability_check_label(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                'class="availability-checked"',
                'class="availability-unchecked"',
            )
        )
        self.assertTrue(
            any("availability check label" in error for error in errors),
            errors,
        )

    def test_requires_point_in_time_caveat(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                "reflects the most recent check",
                "reflects the latest vibe",
                1,
            )
        )
        self.assertTrue(
            any("point-in-time limitation" in error for error in errors),
            errors,
        )

    def test_requires_runtime_unavailable_link_guard(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                "if (productLink) productLink.remove();",
                "",
                1,
            )
        )
        self.assertTrue(
            any("runtime availability associations" in error for error in errors),
            errors,
        )

    def test_runtime_strings_require_trimmed_content(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                '!p[k].trim()',
                'p[k].trim()',
                1,
            )
        )
        self.assertTrue(any("runtime field validation" in error for error in errors), errors)

    def test_requires_exact_get_availability_method(self) -> None:
        errors = self.product_errors(
            lambda products: products[0].update(availability_method="HEAD")
        )
        self.assertTrue(any("availability_method" in error for error in errors), errors)

    def test_requires_measured_numeric_http_status(self) -> None:
        errors = self.product_errors(
            lambda products: products[0].update(availability_http_status=204)
        )
        self.assertTrue(any("availability_http_status" in error for error in errors), errors)

    def test_rejects_extra_absolute_anchor_in_unified_product(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                '<a class="action action--primary product-link" '
                'href="https://unified.dumbmodel.com/">Open Unified</a>',
                '<a class="action action--primary product-link" '
                'href="https://unified.dumbmodel.com/">Open Unified</a>'
                '<a class="other-link" href="https://unified.dumbmodel.com">'
                "Unexpected Unified link</a>",
                1,
            )
        )
        self.assertTrue(
            any(
                "static product truth" in error or "available product" in error
                for error in errors
            ),
            errors,
        )

    def test_rejects_relative_extra_anchor_in_unified_product(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                '<a class="action action--primary product-link" '
                'href="https://unified.dumbmodel.com/">Open Unified</a>',
                '<a class="action action--primary product-link" '
                'href="https://unified.dumbmodel.com/">Open Unified</a>'
                '<a href="/unified">Unexpected Unified link</a>',
                1,
            )
        )
        self.assertTrue(
            any(
                "static product truth" in error or "available product" in error
                for error in errors
            ),
            errors,
        )

    def test_rejects_earlier_duplicate_unified_product_entry(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                '<li class="product" data-product="unified">',
                '<li class="product" data-product="unified">'
                '<a href="/unified">Forbidden duplicate CTA</a></li>'
                '<li class="product" data-product="unified">',
                1,
            )
        )
        self.assertTrue(any("duplicate product entries" in error for error in errors), errors)

    def test_requires_runtime_unique_product_match(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                'var matches = list.querySelectorAll(\'[data-product="\' + p.slug + \'"]\');',
                'var item = list.querySelector(\'[data-product="\' + p.slug + \'"]\');',
                1,
            )
        )
        self.assertTrue(any("dynamic associations" in error for error in errors), errors)

    def test_accepts_six_product_family(self) -> None:
        errors: list[str] = []
        check_gateway.check_products(errors)
        self.assertEqual(errors, [])

    def test_rejects_unverified_comma_count_claim(self) -> None:
        errors = self.product_errors(
            lambda products: products[1].update(
                description="Every NFL player-season mapped by playing style. 48,000 plays charted."
            )
        )
        self.assertTrue(
            any("forbidden rendered claim" in error for error in errors),
            errors,
        )

    def test_live_vercelignore_packages_products_json(self) -> None:
        errors: list[str] = []
        check_gateway.check_vercelignore(errors)
        self.assertEqual(errors, [])

    def test_bare_data_rule_would_strip_products_json(self) -> None:
        """Adversarial: the production-breaking pattern must fail the gate."""
        broken = (
            "# adversarial regression fixture\n"
            "pipeline/\n"
            "data/\n"
            "datasets/\n"
        )
        self.assertTrue(
            check_gateway.path_ignored_by_vercelignore(
                broken, check_gateway.PRODUCTS_DEPLOY_PATH
            ),
            "bare data/ must ignore public/assets/data/products.json",
        )
        with tempfile.TemporaryDirectory() as directory:
            fake = Path(directory) / ".vercelignore"
            fake.write_text(broken, encoding="utf-8")
            with patch.object(check_gateway, "VERCELIGNORE", fake):
                errors: list[str] = []
                check_gateway.check_vercelignore(errors)
        self.assertTrue(
            any("products.json must not be ignored" in error for error in errors),
            errors,
        )

    def test_fixed_rules_keep_heavy_public_dataset_ignored(self) -> None:
        rules = (ROOT / ".vercelignore").read_text(encoding="utf-8")
        self.assertFalse(
            check_gateway.path_ignored_by_vercelignore(
                rules, check_gateway.PRODUCTS_DEPLOY_PATH
            )
        )
        for probe in check_gateway.HEAVY_PUBLIC_DATA_PROBES:
            self.assertTrue(
                check_gateway.path_ignored_by_vercelignore(rules, probe),
                probe,
            )

    def test_products_only_ignore_leaves_heavy_datasets_exposed(self) -> None:
        """Adversarial: packaging products while leaving hoops unignored must fail."""
        weak = (
            "# adversarial: products kept, but bulk datasets not ignored\n"
            "pipeline/\n"
            "/data/\n"
            "datasets/\n"
        )
        self.assertFalse(
            check_gateway.path_ignored_by_vercelignore(
                weak, check_gateway.PRODUCTS_DEPLOY_PATH
            )
        )
        self.assertFalse(
            check_gateway.path_ignored_by_vercelignore(
                weak, check_gateway.HEAVY_PUBLIC_DATA_PROBES[0]
            )
        )
        with tempfile.TemporaryDirectory() as directory:
            fake = Path(directory) / ".vercelignore"
            fake.write_text(weak, encoding="utf-8")
            with patch.object(check_gateway, "VERCELIGNORE", fake):
                errors: list[str] = []
                check_gateway.check_vercelignore(errors)
        self.assertTrue(
            any("hoops.json must remain ignored" in error for error in errors),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
