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
                "  min-height:44px;\n  display:inline-flex;\n"
                "  align-items:center;\n  font:700 .78rem",
                "  display:inline-flex;\n  align-items:center;\n  font:700 .78rem",
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
                "Explore basketball players through a dedicated vector product.",
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
                'href="https://hoops.dumbmodel.com/">Open Hoops',
                'href="https://gridiron.dumbmodel.com/">Open Hoops',
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
                '          || evidenceLink.getAttribute("href") !== product.evidence_url',
                "",
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
                'data-state="ready">Complete built-in product records are shown.',
                'data-state="loading">Checking the local product record…',
                1,
            )
        )
        self.assertTrue(any("static status" in error for error in errors), errors)

    def test_requires_runtime_exact_key_contract(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                '  const productKeys = ["availability", "availability_checked_at", '
                '"availability_http_status", "availability_method", "description", '
                '"evidence_url", "name", "pushed_at", "slug", "url"];\n',
                "",
                1,
            )
        )
        self.assertTrue(any("runtime exact keys" in error for error in errors), errors)

    def test_requires_runtime_name_validation(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                '      && typeof product.name === "string"\n',
                "",
                1,
            )
        )
        self.assertTrue(any("runtime field validation" in error for error in errors), errors)

    def test_requires_runtime_description_validation(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                '      && typeof product.description === "string"\n',
                "",
                1,
            )
        )
        self.assertTrue(any("runtime field validation" in error for error in errors), errors)

    def test_requires_runtime_exact_utc_timestamp_shape(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                "      && pushedAtPattern.test(product.pushed_at)\n",
                "",
                1,
            )
        )
        self.assertTrue(any("runtime pushed_at shape" in error for error in errors), errors)

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

    def test_unified_static_record_forbids_product_link(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                '<span class="product-unavailable">Product unavailable</span>',
                '<a class="action action--primary product-link" '
                'href="https://unified.dumbmodel.com/">Open Unified</a>',
                1,
            )
        )
        self.assertTrue(
            any("unavailable product link" in error for error in errors),
            errors,
        )

    def test_unified_direct_navigation_is_not_a_link(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                '<span class="direct-unavailable" data-product="unified">'
                "Unified — unavailable</span>",
                '<a href="https://unified.dumbmodel.com/">Unified</a>',
                1,
            )
        )
        self.assertTrue(
            any("direct navigation" in error for error in errors),
            errors,
        )

    def test_requires_static_availability_check_semantics(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                '<time class="availability-checked" '
                'datetime="2026-09-09T03:48:23Z">'
                "Availability checked: 2026-09-09T03:48:23Z</time>",
                "",
                1,
            )
        )
        self.assertTrue(
            any("availability check semantics" in error for error in errors),
            errors,
        )

    def test_requires_runtime_unavailable_link_guard(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                "        if (anchors.length !== 1 || anchors[0] !== evidenceLink\n",
                "        if (anchors.length > 1\n",
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
                "product.name.trim().length > 0",
                "product.name.length > 0",
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

    def test_rejects_alternate_class_absolute_anchor_in_unified_product(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                '<span class="product-unavailable">Product unavailable</span>',
                '<span class="product-unavailable">Product unavailable</span>'
                '<a class="other-link" href="https://unified.dumbmodel.com">'
                "Unexpected Unified link</a>",
                1,
            )
        )
        self.assertTrue(any("unavailable product anchors" in error for error in errors), errors)

    def test_rejects_relative_anchor_in_unified_product(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                '<span class="product-unavailable">Product unavailable</span>',
                '<span class="product-unavailable">Product unavailable</span>'
                '<a href="/unified">Unexpected Unified link</a>',
                1,
            )
        )
        self.assertTrue(any("unavailable product anchors" in error for error in errors), errors)

    def test_rejects_alternate_class_absolute_anchor_in_unified_direct_nav(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                "Unified — unavailable</span>",
                'Unified — unavailable</span><a class="other-link" '
                'href="https://unified.dumbmodel.com">Unexpected Unified link</a>',
                1,
            )
        )
        self.assertTrue(any("direct navigation anchors" in error for error in errors), errors)

    def test_rejects_relative_anchor_in_unified_direct_nav(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                "Unified — unavailable</span>",
                'Unified — unavailable</span><a href="/unified">Unexpected Unified link</a>',
                1,
            )
        )
        self.assertTrue(any("direct navigation anchors" in error for error in errors), errors)

    def test_rejects_earlier_duplicate_unified_product_entry(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                '<li class="product product--unified" data-product="unified">',
                '<li class="product" data-product="unified">'
                '<a href="/unified">Forbidden duplicate CTA</a></li>'
                '<li class="product product--unified" data-product="unified">',
                1,
            )
        )
        self.assertTrue(any("duplicate product entries" in error for error in errors), errors)

    def test_rejects_earlier_duplicate_unified_direct_nav_entry(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                '<li data-product="unified"><span class="direct-unavailable"',
                '<li data-product="unified"><a href="/unified">'
                "Forbidden duplicate CTA</a></li>"
                '<li data-product="unified"><span class="direct-unavailable"',
                1,
            )
        )
        self.assertTrue(any("duplicate direct navigation entries" in error for error in errors), errors)

    def test_requires_runtime_unique_product_match(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                'const matches = list.querySelectorAll(`[data-product="${product.slug}"]`);',
                'const item = list.querySelector(`[data-product="${product.slug}"]`);',
                1,
            )
        )
        self.assertTrue(any("dynamic associations" in error for error in errors), errors)

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
