"""Graders for the Chapter 12 lab.

``grade_weak`` is finished on purpose. It passes answers that contain a
few keywords, including answers that state the wrong shop rule.

``grade_hardened`` is the TODO. It should score the constraint fields
on each case. There is no SOLUTION.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Grade:
    """Whether one answer passed, and why it did not."""

    passed: bool
    reasons: list[str] = field(default_factory=list)


def grade_weak(case: dict, answer: str) -> Grade:
    """Pass when every ``weak_keywords`` entry appears in ``answer``.

    This is the grader the lab asks you to game. A wrong sentence that
    mentions the keyword and a file path will pass.
    """
    text = answer.lower()
    reasons: list[str] = []
    for keyword in case.get("weak_keywords", []):
        if str(keyword).lower() not in text:
            reasons.append(f"missing keyword: {keyword}")
    return Grade(passed=not reasons, reasons=reasons)


def grade_hardened(case: dict, answer: str) -> Grade:
    """Score the case constraint, not the keyword costume.

    TODO: fail the answer when any of these is true.

    - A phrase in ``must_contain`` is absent (compare case-insensitively).
    - A phrase in ``must_not_contain`` is present.
    - ``citation`` is absent.

    Return a Grade whose ``passed`` is false when any reason was
    recorded. The starter delegates to ``grade_weak``, so known-bad
    answers still pass until you replace this body.
    """
    return grade_weak(case, answer)
