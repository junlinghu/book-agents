#!/usr/bin/env python3
"""Spec for the Chapter 11 checker.

These tests fail on the starter, which accepts every cart. They pass
when checker.py implements the rules in the lab README. No model server.

    python labs/ch11-verification-loops/test_checker.py
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from checker import check_cart  # noqa: E402


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


CATALOG = load_json(HERE / "catalog.json")


def proposal(name: str) -> dict:
    return load_json(HERE / "proposals" / name)


def hard_ids(proposal_obj: dict) -> set[str]:
    return set(check_cart(proposal_obj, CATALOG).rule_ids("hard"))


class CheckerTests(unittest.TestCase):
    def test_good_pickup_is_accepted_without_warnings(self):
        verdict = check_cart(proposal("good_pickup_espresso.json"), CATALOG)
        self.assertTrue(verdict.accepted)
        self.assertEqual(verdict.soft, [])

    def test_missing_citation_is_a_hard_failure(self):
        self.assertIn("missing_citation", hard_ids(proposal("missing_citation.json")))

    def test_blog_path_does_not_count_as_a_citation(self):
        cart = proposal("good_pickup_espresso.json")
        cart["items"][0]["citations"] = ["docs/blog.md"]
        self.assertIn("missing_citation", hard_ids(cart))

    def test_nuts_covers_almonds_on_the_bun(self):
        self.assertIn("allergen", hard_ids(proposal("nut_allergy.json")))

    def test_almonds_on_the_avoid_list_are_a_hard_failure(self):
        cart = proposal("nut_allergy.json")
        cart["avoid_allergens"] = ["Almonds"]
        self.assertIn("allergen", hard_ids(cart))

    def test_milk_avoidance_blocks_rye_porridge(self):
        cart = proposal("good_pickup_espresso.json")
        cart["items"] = [{"sku": "rye-porridge", "qty": 1, "citations": ["docs/faq.md"]}]
        cart["stated_total_cents"] = 800
        cart["budget_cents"] = 2000
        cart["avoid_allergens"] = ["milk"]
        self.assertIn("allergen", hard_ids(cart))

    def test_over_budget_uses_the_catalog_sum(self):
        ids = hard_ids(proposal("over_budget.json"))
        self.assertIn("over_budget", ids)
        self.assertNotIn("total_mismatch", ids)

    def test_stated_total_under_budget_does_not_hide_the_catalog_sum(self):
        cart = proposal("over_budget.json")
        cart["stated_total_cents"] = 100
        ids = hard_ids(cart)
        self.assertIn("over_budget", ids)
        self.assertIn("total_mismatch", ids)

    def test_total_mismatch_when_the_arithmetic_is_otherwise_in_budget(self):
        ids = hard_ids(proposal("total_mismatch.json"))
        self.assertIn("total_mismatch", ids)
        self.assertNotIn("over_budget", ids)

    def test_pastry_cannot_ship(self):
        self.assertIn("not_shippable", hard_ids(proposal("ship_bun.json")))

    def test_shipping_fee_under_forty_dollars(self):
        verdict = check_cart(proposal("ship_coffee_under_40.json"), CATALOG)
        self.assertTrue(verdict.accepted, verdict.hard)

    def test_shipping_is_free_at_forty_dollars_and_above(self):
        verdict = check_cart(proposal("ship_coffee_free_over_40.json"), CATALOG)
        self.assertTrue(verdict.accepted, verdict.hard)

    def test_saturday_delivery_is_outside_the_window(self):
        self.assertIn(
            "outside_delivery_window", hard_ids(proposal("delivery_saturday.json"))
        )

    def test_wednesday_delivery_with_the_fee_is_accepted(self):
        verdict = check_cart(proposal("delivery_wednesday.json"), CATALOG)
        self.assertTrue(verdict.accepted, verdict.hard)
        self.assertNotIn("outside_delivery_window", verdict.rule_ids("hard"))

    def test_delivery_without_a_clock_does_not_invent_a_day(self):
        cart = proposal("delivery_wednesday.json")
        del cart["now"]
        verdict = check_cart(cart, CATALOG)
        self.assertTrue(verdict.accepted, verdict.hard)
        self.assertNotIn("outside_delivery_window", verdict.rule_ids("hard"))

    def test_unknown_sku(self):
        self.assertIn("unknown_sku", hard_ids(proposal("unknown_sku.json")))

    def test_bad_qty(self):
        self.assertIn("bad_qty", hard_ids(proposal("bad_qty.json")))

    def test_unknown_fulfillment(self):
        cart = proposal("good_pickup_espresso.json")
        cart["fulfillment"] = "courier"
        self.assertIn("bad_fulfillment", hard_ids(cart))

    def test_nut_free_prep_claim_is_a_soft_warning(self):
        verdict = check_cart(proposal("nut_free_claim.json"), CATALOG)
        self.assertTrue(verdict.accepted, verdict.hard)
        self.assertIn("nut_free_prep", verdict.rule_ids("soft"))


if __name__ == "__main__":
    unittest.main()
