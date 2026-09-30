"""Score recorded answers with the Chapter 12 constraint check.

This module is the gate's harness. It reads the Chapter 12 fixtures and
does not modify them. The merge policy lives in ``gate.py``, which is
the TODO. There is no SOLUTION.md.
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CH12_FIXTURES = (
    HERE.parent / "ch12-evals-from-real-failures" / "fixtures"
)


def load_jsonl(path: Path) -> list[dict]:
    """Load a JSONL file."""
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def load_cases() -> list[dict]:
    """Return the Chapter 12 failure cases, in file order."""
    return load_jsonl(CH12_FIXTURES / "failures.jsonl")


def answers_for(which: str) -> dict[str, str]:
    """Return recorded answers for ``good`` or ``bad``.

    ``good`` is the Chapter 12 known-good set. ``bad`` is the logged
    miss on each case. Other names raise ``ValueError``.
    """
    cases = load_cases()
    if which == "bad":
        return {row["id"]: row["bad_answer"] for row in cases}
    if which == "good":
        rows = load_jsonl(CH12_FIXTURES / "good_answers.jsonl")
        return {row["id"]: row["answer"] for row in rows}
    raise ValueError(f"unknown answer set: {which}")


def score_case(case: dict, answer: str) -> dict:
    """Score one answer against the case constraint.

    This is the hardened check from Chapter 12: required phrases,
    forbidden phrases, and the citation, compared case-insensitively.
    ``passed`` is false when any reason was recorded.
    """
    text = answer.lower()
    reasons: list[str] = []
    for phrase in case.get("must_contain", []):
        if str(phrase).lower() not in text:
            reasons.append(f"missing required phrase: {phrase}")
    for phrase in case.get("must_not_contain", []):
        if str(phrase).lower() in text:
            reasons.append(f"forbidden phrase: {phrase}")
    citation = case.get("citation") or ""
    if citation and citation.lower() not in text:
        reasons.append(f"missing citation: {citation}")
    return {"passed": not reasons, "reasons": reasons}


def run_suite(cases: list[dict], answers: dict[str, str]) -> dict:
    """Score every case. A missing answer is a failure.

    The report is green only when every case passed. ``failures`` lists
    ``id`` and ``reasons`` for the cases that did not, in case order.
    """
    failures = []
    n_passed = 0
    for case in cases:
        case_id = case["id"]
        answer = answers.get(case_id)
        if answer is None:
            failures.append(
                {"id": case_id, "reasons": ["missing recorded answer"]}
            )
            continue
        grade = score_case(case, answer)
        if grade["passed"]:
            n_passed += 1
        else:
            failures.append({"id": case_id, "reasons": grade["reasons"]})
    return {
        "passed": not failures and len(cases) > 0,
        "failures": failures,
        "n": len(cases),
        "n_passed": n_passed,
    }
