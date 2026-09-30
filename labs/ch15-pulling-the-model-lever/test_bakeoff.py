#!/usr/bin/env python3
"""Spec for preference pairs and the recorded bake-off.

Both checks fail on the starter.

    python labs/ch15-pulling-the-model-lever/test_bakeoff.py
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from bakeoff import summarize_bakeoff  # noqa: E402
from pairs import build_pairs, load_jsonl  # noqa: E402


REJECTS = load_jsonl(HERE / "fixtures" / "rejects.jsonl")
ROWS = load_jsonl(HERE / "fixtures" / "bakeoff_rows.jsonl")


class PairTests(unittest.TestCase):
    def test_pairs_keep_only_real_repairs(self):
        pairs = build_pairs(REJECTS)
        self.assertEqual(
            [row["case_id"] for row in pairs],
            [
                "allergy_saturday",
                "budget_shipping",
                "citation_hours",
                "ship_pastry",
                "menu_citation",
            ],
        )

    def test_each_pair_has_two_sides_and_a_rule(self):
        for row in build_pairs(REJECTS):
            self.assertIsInstance(row["rejected"], dict)
            self.assertIsInstance(row["preferred"], dict)
            self.assertNotEqual(row["rejected"], row["preferred"])
            self.assertTrue(row["rule_ids"])
            self.assertIn("source", row)


class BakeoffTests(unittest.TestCase):
    def test_recorded_rows_cover_three_arms(self):
        arms = {row["arm"] for row in ROWS}
        self.assertEqual(arms, {"small_v1", "small_v2", "large_v1"})
        self.assertEqual(len(ROWS), 18)

    def test_skill_patch_and_model_swap_move_different_cases(self):
        summary = summarize_bakeoff(ROWS)
        self.assertEqual(summary["small_v1"]["clean_successes"], 1)
        self.assertEqual(summary["small_v2"]["clean_successes"], 5)
        self.assertEqual(summary["large_v1"]["clean_successes"], 3)
        for arm in summary.values():
            self.assertEqual(arm["tasks"], 6)

    def test_cost_per_clean_success_includes_failed_rows(self):
        summary = summarize_bakeoff(ROWS)
        self.assertEqual(summary["small_v1"]["cost_micro_usd"], 46000)
        self.assertEqual(summary["small_v1"]["cost_per_clean_success_micro_usd"], 46000)
        self.assertEqual(summary["small_v2"]["cost_micro_usd"], 72000)
        self.assertEqual(summary["small_v2"]["cost_per_clean_success_micro_usd"], 14400)
        self.assertEqual(summary["large_v1"]["cost_micro_usd"], 240000)
        self.assertEqual(summary["large_v1"]["cost_per_clean_success_micro_usd"], 80000)

    def test_latency_p50_uses_clean_successes_only(self):
        summary = summarize_bakeoff(ROWS)
        self.assertEqual(summary["small_v1"]["latency_p50_clean_ms"], 900)
        self.assertEqual(summary["small_v2"]["latency_p50_clean_ms"], 1400)
        self.assertEqual(summary["large_v1"]["latency_p50_clean_ms"], 650)


if __name__ == "__main__":
    unittest.main()
