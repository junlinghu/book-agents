#!/usr/bin/env python3
"""Spec for the Chapter 23 contracts and roles.

These tests fail on the starter. They pass when the TODOs match the
lab README. No model server.

    python labs/ch23-multi-agent-patterns/test_contracts.py
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from contracts import validate_artifact  # noqa: E402
from handoff import append_if_valid, run_pipeline  # noqa: E402
from roles import check, draft_purchase, research, route_task  # noqa: E402


def load_json(name: str) -> dict:
    return json.loads((HERE / "fixtures" / name).read_text(encoding="utf-8"))


INVENTORY = load_json("inventory.json")
CATALOG = load_json("catalog.json")
NOTE = (HERE / "fixtures" / "supplier-note.txt").read_text(encoding="utf-8")

GOOD_RESEARCH = {
    "role": "researcher",
    "sku": "house-coffee",
    "on_hand": 4,
    "par": 16,
    "sources": ["inventory.json"],
    "untrusted_notes": NOTE,
}

GOOD_DRAFT = {
    "role": "buyer",
    "sku": "house-coffee",
    "qty": 12,
    "unit_price_cents": 1800,
    "total_cents": 21600,
    "citations": ["catalog.json"],
}


def rule_ids(verdict: dict) -> set[str]:
    return {row["rule_id"] for row in verdict["findings"]}


class ContractTests(unittest.TestCase):
    def test_good_researcher_artifact_is_valid(self):
        self.assertEqual(validate_artifact("researcher", dict(GOOD_RESEARCH)), [])

    def test_researcher_cannot_emit_qty(self):
        artifact = dict(GOOD_RESEARCH)
        artifact["qty"] = 1000
        errors = validate_artifact("researcher", artifact)
        self.assertTrue(any("qty" in error for error in errors))

    def test_researcher_requires_sources(self):
        artifact = dict(GOOD_RESEARCH)
        artifact["sources"] = []
        errors = validate_artifact("researcher", artifact)
        self.assertTrue(any("sources" in error for error in errors))

    def test_good_buyer_artifact_is_valid(self):
        self.assertEqual(validate_artifact("buyer", dict(GOOD_DRAFT)), [])

    def test_buyer_total_must_match(self):
        artifact = dict(GOOD_DRAFT)
        artifact["total_cents"] = 1
        errors = validate_artifact("buyer", artifact)
        self.assertTrue(any("total_cents" in error for error in errors))

    def test_buyer_must_not_place(self):
        artifact = dict(GOOD_DRAFT)
        artifact["order_id"] = "po-1842"
        errors = validate_artifact("buyer", artifact)
        self.assertTrue(errors)

    def test_checker_cannot_accept_a_hard_finding(self):
        artifact = {
            "role": "checker",
            "accepted": True,
            "findings": [
                {
                    "rule_id": "qty_mismatch",
                    "severity": "hard",
                    "message": "draft qty is not par minus on hand",
                }
            ],
        }
        errors = validate_artifact("checker", artifact)
        self.assertTrue(any("accepted" in error for error in errors))

    def test_bad_researcher_is_not_appended(self):
        pad: list = []
        errors = append_if_valid(
            pad, "researcher", {"role": "researcher", "qty": 1000}
        )
        self.assertTrue(errors)
        self.assertEqual(pad, [])


class RoleTests(unittest.TestCase):
    def test_research_copies_the_shelf_and_files_the_note(self):
        artifact = research(INVENTORY, NOTE)
        self.assertEqual(artifact["sku"], "house-coffee")
        self.assertEqual(artifact["on_hand"], 4)
        self.assertEqual(artifact["par"], 16)
        self.assertNotIn("qty", artifact)
        self.assertIn("1000", artifact["untrusted_notes"])
        self.assertEqual(validate_artifact("researcher", artifact), [])

    def test_buyer_ignores_the_note(self):
        draft = draft_purchase(dict(GOOD_RESEARCH), CATALOG)
        self.assertEqual(draft["qty"], 12)
        self.assertEqual(draft["unit_price_cents"], 1800)
        self.assertEqual(draft["total_cents"], 21600)
        self.assertEqual(draft["citations"], ["catalog.json"])
        self.assertNotIn("order_id", draft)
        self.assertNotIn("charged", draft)
        self.assertEqual(validate_artifact("buyer", draft), [])

    def test_checker_accepts_the_catalog_draft(self):
        verdict = check(dict(GOOD_RESEARCH), dict(GOOD_DRAFT), CATALOG)
        self.assertTrue(verdict["accepted"])
        self.assertEqual(rule_ids(verdict), set())

    def test_checker_rejects_one_thousand_bags(self):
        draft = dict(GOOD_DRAFT)
        draft["qty"] = 1000
        draft["total_cents"] = 1000 * 1800
        verdict = check(dict(GOOD_RESEARCH), draft, CATALOG)
        self.assertFalse(verdict["accepted"])
        self.assertIn("qty_mismatch", rule_ids(verdict))
        for finding in verdict["findings"]:
            self.assertTrue(finding["message"])
            self.assertEqual(finding["severity"], "hard")

    def test_checker_rejects_a_note_price(self):
        draft = dict(GOOD_DRAFT)
        draft["unit_price_cents"] = 900
        draft["total_cents"] = 12 * 900
        verdict = check(dict(GOOD_RESEARCH), draft, CATALOG)
        self.assertIn("price_mismatch", rule_ids(verdict))
        self.assertNotIn("total_mismatch", rule_ids(verdict))

    def test_checker_rejects_a_bad_total(self):
        draft = dict(GOOD_DRAFT)
        draft["total_cents"] = 1
        self.assertIn(
            "total_mismatch",
            rule_ids(check(dict(GOOD_RESEARCH), draft, CATALOG)),
        )

    def test_checker_rejects_a_missing_citation(self):
        draft = dict(GOOD_DRAFT)
        draft["citations"] = []
        self.assertIn(
            "missing_citation",
            rule_ids(check(dict(GOOD_RESEARCH), draft, CATALOG)),
        )

    def test_checker_rejects_an_early_place(self):
        draft = dict(GOOD_DRAFT)
        draft["order_id"] = "po-1842"
        self.assertIn(
            "placed_early",
            rule_ids(check(dict(GOOD_RESEARCH), draft, CATALOG)),
        )

    def test_checker_rejects_a_sku_change(self):
        draft = dict(GOOD_DRAFT)
        draft["sku"] = "cardamom-bun"
        self.assertIn(
            "sku_mismatch",
            rule_ids(check(dict(GOOD_RESEARCH), draft, CATALOG)),
        )

    def test_bun_price_stays_one_agent(self):
        self.assertEqual(route_task("How much is a cardamom bun?"), "single")
        self.assertEqual(route_task("What time do you open on Monday?"), "single")

    def test_restock_and_supplier_note_split(self):
        self.assertEqual(
            route_task("Draft a house-coffee restock from the shelf and check it."),
            "split",
        )
        self.assertEqual(
            route_task(
                "Read the supplier note, draft a purchase, and check the quantity."
            ),
            "split",
        )


class PipelineTests(unittest.TestCase):
    def test_pipeline_drafts_twelve_and_keeps_the_note(self):
        result = run_pipeline(INVENTORY, NOTE, CATALOG)
        self.assertEqual(result["errors"], [])
        self.assertEqual(len(result["scratchpad"]), 3)
        self.assertEqual(
            [row["author"] for row in result["scratchpad"]],
            ["researcher", "buyer", "checker"],
        )
        self.assertIn("1000", result["scratchpad"][0]["body"]["untrusted_notes"])
        self.assertEqual(result["scratchpad"][1]["body"]["qty"], 12)
        self.assertTrue(result["accepted"])
        self.assertNotIn("order_id", result["scratchpad"][1]["body"])


if __name__ == "__main__":
    unittest.main()
