#!/usr/bin/env python3
"""Spec for the skill-patch gate.

Suite tests pass on the starter. Surface and merge tests fail until
the TODOs in ``gate.py`` are done.

    python labs/ch25-self-improving-agents/test_gate.py
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from gate import decide_merge, patch_surface_ok  # noqa: E402
from suite import answers_for, load_cases, run_suite  # noqa: E402


CASES = load_cases()
GOOD = run_suite(CASES, answers_for("good"))
BAD = run_suite(CASES, answers_for("bad"))


def load_patch(name: str) -> dict:
    return json.loads((HERE / "patches" / name).read_text(encoding="utf-8"))


class SuiteTests(unittest.TestCase):
    def test_known_good_answers_stay_green(self):
        self.assertTrue(GOOD["passed"], GOOD["failures"])
        self.assertEqual(GOOD["failures"], [])
        self.assertEqual(GOOD["n"], 10)
        self.assertEqual(GOOD["n_passed"], 10)

    def test_logged_misses_stay_red(self):
        self.assertFalse(BAD["passed"])
        self.assertEqual(
            [row["id"] for row in BAD["failures"]],
            [case["id"] for case in CASES],
        )
        for failure in BAD["failures"]:
            self.assertTrue(failure["reasons"], failure["id"])


class SurfaceTests(unittest.TestCase):
    def test_a_skill_file_is_allowed(self):
        self.assertTrue(
            patch_surface_ok({"files": ["skills/counter.md"]})
        )

    def test_grader_and_traversal_are_rejected(self):
        rejected = [
            ["labs/ch12-evals-from-real-failures/grader.py"],
            ["skills/../grader.py"],
            ["skills/counter.md", "grader.py"],
            ["skills/counter.txt"],
            ["/tmp/skills/counter.md"],
            ["skills\\counter.md"],
            ["skills//counter.md"],
            ["skills/./counter.md"],
            [],
        ]
        for files in rejected:
            self.assertFalse(
                patch_surface_ok({"files": files}), files
            )


class MergeTests(unittest.TestCase):
    def test_green_skill_merges_for_a_person(self):
        patch = load_patch("good_counter.json")
        self.assertEqual(decide_merge(patch, GOOD, "maya"), "merge")
        extra = {
            "id": "thursday_note",
            "files": ["skills/restock-note.md"],
        }
        self.assertEqual(decide_merge(extra, GOOD, "Ellis"), "merge")

    def test_red_suite_rejects(self):
        patch = load_patch("bad_helpful.json")
        self.assertEqual(decide_merge(patch, BAD, "maya"), "reject")

    def test_grader_edit_rejects_even_when_answers_pass(self):
        patch = load_patch("rewrite_grader.json")
        self.assertTrue(GOOD["passed"])
        self.assertEqual(decide_merge(patch, GOOD, "maya"), "reject")

    def test_agent_and_blank_reviewer_reject(self):
        patch = {"id": "counter", "files": ["skills/counter.md"]}
        self.assertEqual(decide_merge(patch, GOOD, "agent"), "reject")
        self.assertEqual(decide_merge(patch, GOOD, "Agent"), "reject")
        self.assertEqual(decide_merge(patch, GOOD, "  "), "reject")
        self.assertEqual(decide_merge(patch, GOOD, ""), "reject")

    def test_green_flag_with_failures_rejects(self):
        patch = {"id": "counter", "files": ["skills/counter.md"]}
        report = {
            "passed": True,
            "failures": [
                {"id": "opened-coffee-window", "reasons": ["still wrong"]}
            ],
        }
        self.assertEqual(decide_merge(patch, report, "maya"), "reject")


if __name__ == "__main__":
    unittest.main()
