#!/usr/bin/env python3
"""Score logged failures, known-good answers, and an example cheat.

No model server. The weak grader should pass the bad answers. After
you harden ``grade_hardened``, those answers should fail and the
known-good answers should still pass.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from grader import grade_hardened, grade_weak  # noqa: E402


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def score_pair(label: str, case: dict, answer: str) -> None:
    weak = grade_weak(case, answer)
    hard = grade_hardened(case, answer)
    print(
        f"{case['id']:28} {label:12} "
        f"weak={'pass' if weak.passed else 'FAIL'} "
        f"hardened={'pass' if hard.passed else 'FAIL'}"
    )
    if hard.reasons and hard.reasons != weak.reasons:
        print(f"  hardened: {'; '.join(hard.reasons)}")


def main() -> int:
    fixtures = HERE / "fixtures"
    failures = load_jsonl(fixtures / "failures.jsonl")
    good = {row["id"]: row["answer"] for row in load_jsonl(fixtures / "good_answers.jsonl")}
    cheats = load_jsonl(fixtures / "example_cheat.jsonl")
    by_id = {row["id"]: row for row in failures}

    print("id                           set          weak     hardened")
    for case in failures:
        score_pair("bad", case, case["bad_answer"])
        score_pair("good", case, good[case["id"]])
    for cheat in cheats:
        score_pair("cheat", by_id[cheat["id"]], cheat["answer"])

    mine = fixtures / "my_cheats.jsonl"
    if mine.is_file():
        for cheat in load_jsonl(mine):
            score_pair("my_cheat", by_id[cheat["id"]], cheat["answer"])
    else:
        print()
        print("No fixtures/my_cheats.jsonl yet. Add your own cheats there.")
        print('Each line: {"id": "<case id>", "answer": "<wrong answer the weak grader passes>"}')
    return 0


if __name__ == "__main__":
    sys.exit(main())
