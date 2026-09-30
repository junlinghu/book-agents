#!/usr/bin/env python3
"""Spec for the Chapter 12 graders.

Weak-grader tests pass on the starter. Hardened-grader tests fail
until ``grade_hardened`` enforces the case constraints.

    python labs/ch12-evals-from-real-failures/test_grader.py
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from grader import grade_hardened, grade_weak  # noqa: E402


def load_jsonl(name: str) -> list[dict]:
    rows = []
    for line in (HERE / "fixtures" / name).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


FAILURES = load_jsonl("failures.jsonl")
GOOD = {row["id"]: row["answer"] for row in load_jsonl("good_answers.jsonl")}
CHEATS = load_jsonl("example_cheat.jsonl")
BY_ID = {row["id"]: row for row in FAILURES}


class WeakGraderTests(unittest.TestCase):
    def test_known_bad_answers_pass_the_weak_grader(self):
        for case in FAILURES:
            grade = grade_weak(case, case["bad_answer"])
            self.assertTrue(grade.passed, case["id"])

    def test_known_good_answers_pass_the_weak_grader(self):
        for case in FAILURES:
            grade = grade_weak(case, GOOD[case["id"]])
            self.assertTrue(grade.passed, case["id"])

    def test_example_cheat_passes_the_weak_grader(self):
        for cheat in CHEATS:
            grade = grade_weak(BY_ID[cheat["id"]], cheat["answer"])
            self.assertTrue(grade.passed, cheat["id"])


class HardenedGraderTests(unittest.TestCase):
    def test_known_good_answers_still_pass(self):
        for case in FAILURES:
            grade = grade_hardened(case, GOOD[case["id"]])
            self.assertTrue(grade.passed, (case["id"], grade.reasons))

    def test_known_bad_answers_fail(self):
        for case in FAILURES:
            grade = grade_hardened(case, case["bad_answer"])
            self.assertFalse(grade.passed, case["id"])
            self.assertTrue(grade.reasons, case["id"])

    def test_example_cheat_fails(self):
        for cheat in CHEATS:
            grade = grade_hardened(BY_ID[cheat["id"]], cheat["answer"])
            self.assertFalse(grade.passed, cheat["answer"])


if __name__ == "__main__":
    unittest.main()
