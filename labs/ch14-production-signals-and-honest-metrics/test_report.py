#!/usr/bin/env python3
"""Spec for the Chapter 14 report.

Fails on the starter because ``summarize`` is not implemented.

    python labs/ch14-production-signals-and-honest-metrics/test_report.py
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from report import load_events, summarize  # noqa: E402


EVENTS = load_events(HERE / "fixtures" / "events.jsonl")


class ReportTests(unittest.TestCase):
    def test_fixture_has_twelve_tasks(self):
        self.assertEqual(len(EVENTS), 12)

    def test_summary_counts(self):
        summary = summarize(EVENTS)
        self.assertEqual(summary["n"], 12)
        self.assertEqual(summary["clean_successes"], 5)
        self.assertEqual(summary["eventual_completions"], 7)
        self.assertEqual(summary["model_said_successes"], 10)
        self.assertNotEqual(
            summary["clean_successes"], summary["model_said_successes"]
        )
        self.assertEqual(summary["proposals_shown"], 9)
        self.assertEqual(summary["confirms"], 6)
        self.assertEqual(summary["corrections"], 2)
        self.assertEqual(summary["abandons_after_proposal"], 1)

    def test_cost_includes_failures_in_the_numerator(self):
        summary = summarize(EVENTS)
        self.assertEqual(summary["cost_micro_usd"], 206000)
        self.assertEqual(summary["cost_per_clean_success_micro_usd"], 41200)
        self.assertEqual(summary["cost_per_eventual_completion_micro_usd"], 29428)

    def test_latency_p50_is_the_lower_median_of_clean_successes(self):
        summary = summarize(EVENTS)
        self.assertEqual(summary["latency_p50_clean_ms"], 900)

    def test_hard_fail_counts(self):
        summary = summarize(EVENTS)
        self.assertEqual(
            summary["hard_fail_counts"],
            {"allergen": 2, "missing_citation": 1, "total_mismatch": 1},
        )


if __name__ == "__main__":
    unittest.main()
