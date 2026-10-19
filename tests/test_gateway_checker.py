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

# Mirrors vector-hoops master assets/mtnn_meta.json headline fields so page
# tests stay hermetic. The live script still fetches GitHub raw in CI.
SERVED_META_FIXTURE = {
    "built": "2026-07-25",
    "model": "mtnn_v5_concat_b2_h160_t32_d64_mlp128_fus256",
    "dim": 64,
    "rows": 12966,
}


class GatewayCheckerAdversarialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(
            (ROOT / "public" / "assets" / "data" / "products.json").read_text(
                encoding="utf-8"
            )
        )
        cls._truth = patch.object(
            check_gateway,
            "load_served_model_truth",
            return_value=(SERVED_META_FIXTURE, None),
        )
        cls._truth.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls._truth.stop()

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

    def css_errors(self, mutate) -> list[str]:
        css = (ROOT / "public" / "drafting.css").read_text(encoding="utf-8")
        css = mutate(css)
        with tempfile.TemporaryDirectory() as directory:
            css_file = Path(directory) / "drafting.css"
            css_file.write_text(css, encoding="utf-8")
            errors: list[str] = []
            products = check_gateway.check_products(errors)
            with patch.object(check_gateway, "STYLES", css_file):
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
        errors = self.css_errors(
            lambda css: css.replace(
                "min-width:44px;min-height:44px",
                "",
                1,
            )
        )
        self.assertTrue(
            any("brand target" in error for error in errors),
            errors,
        )

    def test_rejects_horizontal_overflow_clipping(self) -> None:
        errors = self.css_errors(
            lambda css: css.replace(
                "html{scroll-behavior:smooth;overflow-wrap:anywhere}",
                "html{scroll-behavior:smooth;overflow-wrap:anywhere;overflow-x:hidden}",
                1,
            )
        )
        self.assertTrue(
            any("overflow clipping" in error for error in errors),
            errors,
        )

    def test_requires_focus_visible(self) -> None:
        errors = self.css_errors(
            lambda css: css.replace(":focus-visible", ":focus", 1)
        )
        self.assertTrue(
            any("visible focus styling is missing" in error for error in errors),
            errors,
        )

    def test_requires_reduced_motion(self) -> None:
        errors = self.css_errors(
            lambda css: css.replace(
                "@media (prefers-reduced-motion: reduce)",
                "@media (prefers-reduced-data: reduce)",
                1,
            )
        )
        self.assertTrue(
            any("reduced-motion handling is missing" in error for error in errors),
            errors,
        )

    def test_requires_overflow_wrap(self) -> None:
        errors = self.css_errors(
            lambda css: css.replace("overflow-wrap:anywhere", "overflow-wrap:normal")
        )
        self.assertTrue(
            any("horizontal overflow" in error for error in errors),
            errors,
        )

    def test_requires_skip_link(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace('href="#main"', 'href="#top"', 1)
        )
        self.assertTrue(
            any("no skip link targets #main" in error for error in errors),
            errors,
        )

    def test_requires_headline_player_season_count(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace("12,966", "12,452")
        )
        self.assertTrue(
            any("player-seasons count" in error for error in errors),
            errors,
        )

    def test_changed_served_rows_fail_stale_page(self) -> None:
        """A vector-hoops promote that changes rows must fail until copy matches."""
        promoted = dict(SERVED_META_FIXTURE, rows=12452)
        with patch.object(
            check_gateway,
            "load_served_model_truth",
            return_value=(promoted, None),
        ):
            errors: list[str] = []
            products = check_gateway.check_products(errors)
            check_gateway.check_page(errors, products)
        self.assertTrue(
            any(
                "player-seasons count" in error and "12,452" in error
                for error in errors
            ),
            errors,
        )

    def test_changed_served_champion_fails_stale_page(self) -> None:
        promoted = dict(
            SERVED_META_FIXTURE,
            model="mtnn_v6_concat_b3_h256_t64_d128_mlp256_fus512",
        )
        with patch.object(
            check_gateway,
            "load_served_model_truth",
            return_value=(promoted, None),
        ):
            errors: list[str] = []
            products = check_gateway.check_products(errors)
            check_gateway.check_page(errors, products)
        self.assertTrue(
            any("champion model" in error and "MTNN v6" in error for error in errors),
            errors,
        )

    def test_served_meta_fetch_error_fails_check(self) -> None:
        with patch.object(
            check_gateway,
            "load_served_model_truth",
            side_effect=RuntimeError("could not fetch mtnn_meta.json: timed out"),
        ):
            errors: list[str] = []
            check_gateway.check_page(errors, [])
        self.assertTrue(
            any("served-model truth" in error and "timed out" in error for error in errors),
            errors,
        )

    def test_requires_mtnn_v5_champion(self) -> None:
        errors = self.page_errors(lambda page: page.replace("MTNN v5", "MTNN v6"))
        self.assertTrue(
            any("champion model" in error for error in errors),
            errors,
        )

    def test_requires_era_twin_count(self) -> None:
        errors = self.page_errors(lambda page: page.replace("1,313", "1,308"))
        self.assertTrue(
            any("era-twin players" in error for error in errors),
            errors,
        )

    def test_requires_forecast_mae(self) -> None:
        errors = self.page_errors(lambda page: page.replace("0.4382", "0.4400"))
        self.assertTrue(
            any("forecasting macro-MAE" in error for error in errors),
            errors,
        )

    def test_requires_explanation_not_storefront(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                "not a lab and not a storefront",
                "a storefront for the vector product family",
                1,
            )
        )
        self.assertTrue(
            any("site purpose" in error or "vector product family" in error for error in errors),
            errors,
        )

    def test_rejects_product_storefront_cta(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                '<a href="/model">Model card →</a>',
                '<a href="https://hoops.dumbmodel.com/">Open Hoops</a>',
                1,
            )
        )
        self.assertTrue(
            any("storefront CTA" in error for error in errors),
            errors,
        )

    def test_rejects_vector_product_family_framing(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                "methodology notebook",
                "vector product family",
                1,
            )
        )
        self.assertTrue(
            any("vector product family" in error for error in errors),
            errors,
        )

    def test_requires_section_nav_hrefs(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace('href="/career-trails"', 'href="/missing"')
        )
        self.assertTrue(
            any("missing notebook links" in error for error in errors),
            errors,
        )

    def test_rejects_generated_map_on_home(self) -> None:
        errors = self.page_errors(
            lambda page: page.replace(
                "<main class=\"sheet\" id=\"main\">",
                "<main class=\"sheet\" id=\"main\"><canvas id=\"map\"></canvas>",
                1,
            )
        )
        self.assertTrue(
            any("generated map" in error for error in errors),
            errors,
        )

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

    def test_live_methodology_home_passes(self) -> None:
        errors: list[str] = []
        products = check_gateway.check_products(errors)
        check_gateway.check_page(errors, products)
        check_gateway.check_notebook(errors)
        self.assertEqual(errors, [])

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
