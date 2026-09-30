#!/usr/bin/env python3
"""Score three proposals against the Chapter 12 suite, then ask the gate.

The suite runs without a model. Merge decisions stay on the TODO until
``decide_merge`` is implemented. This script does not write skill files.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from gate import decide_merge  # noqa: E402
from suite import answers_for, load_cases, run_suite  # noqa: E402


PATCH_ORDER = (
    "good_counter.json",
    "bad_helpful.json",
    "rewrite_grader.json",
)


def load_patch(name: str) -> dict:
    return json.loads((HERE / "patches" / name).read_text(encoding="utf-8"))


def print_report(patch: dict, report: dict) -> None:
    status = "GREEN" if report["passed"] else "RED"
    files = ", ".join(patch["files"])
    print(
        f"{patch['id']:18} {status:5} "
        f"{report['n_passed']}/{report['n']}  files={files}"
    )
    for failure in report["failures"]:
        print(f"  {failure['id']}: {'; '.join(failure['reasons'])}")


def main() -> int:
    cases = load_cases()
    print(f"loaded {len(cases)} Chapter 12 cases")
    print()
    print(f"{'patch':18} {'suite':5} pass  files")
    scored = []
    for name in PATCH_ORDER:
        patch = load_patch(name)
        report = run_suite(cases, answers_for(patch["answers"]))
        print_report(patch, report)
        scored.append((patch, report))

    print()
    print("decisions (reviewer maya, then reviewer agent)")
    for patch, report in scored:
        for reviewer in ("maya", "agent"):
            try:
                decision = decide_merge(patch, report, reviewer)
            except NotImplementedError as exc:
                print(f"TODO: {exc}")
                return 0
            print(f"{patch['id']:18} reviewer={reviewer:6} {decision}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
