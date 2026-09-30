#!/usr/bin/env python3
"""Spec for the restock router and the recorded cost receipt.

``test_fixture_is_one_scenario`` passes on the starter. The route and
summary tests fail until the TODOs in ``router.py`` are done.

    python labs/ch24-cost-latency-and-architecture/test_router.py
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from router import load_jsonl, route, summarize_runs  # noqa: E402


ROWS = load_jsonl(HERE / "fixtures" / "restock_runs.jsonl")


class FixtureTests(unittest.TestCase):
    def test_fixture_is_one_scenario(self):
        arms = {row["arm"] for row in ROWS}
        self.assertEqual(arms, {"all_small", "all_large", "routed"})
        scenarios = {row["scenario"] for row in ROWS}
        self.assertEqual(scenarios, {"weekday_restock"})
        tasks = {row["task_id"] for row in ROWS}
        self.assertEqual(tasks, {"tue_rush", "wed_dairy", "fri_close"})
        tools = {row["tool"] for row in ROWS}
        self.assertEqual(
            tools, {"read_par", "read_stock", "write_qty", "draft_note"}
        )
        self.assertEqual(len(ROWS), 36)


class RouteTests(unittest.TestCase):
    def test_crud_tools_go_to_the_small_model(self):
        for tool in ("read_par", "read_stock", "write_qty"):
            self.assertEqual(route({"tool": tool}), "small", tool)

    def test_draft_note_goes_to_the_large_model(self):
        self.assertEqual(route({"tool": "draft_note"}), "large")

    def test_unknown_tools_are_not_silently_small(self):
        for tool in ("place_order", "charge_card", "send_email"):
            with self.assertRaises(ValueError):
                route({"tool": tool})

    def test_routed_arm_matches_the_router(self):
        routed = [row for row in ROWS if row["arm"] == "routed"]
        self.assertEqual(len(routed), 12)
        for row in routed:
            self.assertEqual(row["model"], route(row), row["step_id"])


class SummaryTests(unittest.TestCase):
    def test_clean_success_requires_every_step(self):
        summary = summarize_runs(ROWS)
        self.assertEqual(summary["all_small"]["tasks"], 3)
        self.assertEqual(summary["all_small"]["clean_successes"], 0)
        self.assertEqual(summary["all_large"]["tasks"], 3)
        self.assertEqual(summary["all_large"]["clean_successes"], 3)
        self.assertEqual(summary["routed"]["tasks"], 3)
        self.assertEqual(summary["routed"]["clean_successes"], 3)

    def test_cost_includes_failed_steps_and_uses_floor_division(self):
        summary = summarize_runs(ROWS)
        self.assertEqual(summary["all_small"]["cost_micro_usd"], 22500)
        self.assertIsNone(summary["all_small"]["cost_per_clean_success_micro_usd"])
        self.assertEqual(summary["all_large"]["cost_micro_usd"], 111000)
        self.assertEqual(
            summary["all_large"]["cost_per_clean_success_micro_usd"], 37000
        )
        self.assertEqual(summary["routed"]["cost_micro_usd"], 50700)
        self.assertEqual(
            summary["routed"]["cost_per_clean_success_micro_usd"], 16900
        )

    def test_wall_clock_sums_steps_and_median_skips_failures(self):
        summary = summarize_runs(ROWS)
        self.assertEqual(summary["all_small"]["wall_clock_ms"], 3470)
        self.assertIsNone(summary["all_small"]["wall_clock_p50_clean_ms"])
        self.assertEqual(summary["all_large"]["wall_clock_ms"], 11080)
        self.assertEqual(summary["all_large"]["wall_clock_p50_clean_ms"], 3680)
        self.assertEqual(summary["routed"]["wall_clock_ms"], 6570)
        self.assertEqual(summary["routed"]["wall_clock_p50_clean_ms"], 2170)


if __name__ == "__main__":
    unittest.main()
