#!/usr/bin/env python3
"""Route a restock step and summarize recorded cost and wall-clock.

The rows are one restock scenario run three ways. You do not call a
model. There is no SOLUTION.md.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

ARMS = ("all_small", "all_large", "routed")


def load_jsonl(path: Path) -> list[dict]:
    """Load a JSONL file of recorded restock steps."""
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def route(step: dict) -> str:
    """Return ``small`` or ``large`` for one restock step.

    TODO: route by ``tool``.

    - ``read_par``, ``read_stock``, and ``write_qty`` go to ``small``.
    - ``draft_note`` goes to ``large``.
    - Any other tool raises ``ValueError``. Do not default an unknown
      tool to the small model. ``place_order`` and ``charge_card`` are
      not model steps.

    The starter raises ``NotImplementedError``.
    """
    del step
    raise NotImplementedError("route is not implemented. See the lab README.")


def summarize_runs(rows: list[dict]) -> dict:
    """Summarize recorded runs of the same restock scenario.

    TODO: return a dict keyed by ``all_small``, ``all_large``, and
    ``routed``. Group each arm's rows by ``task_id``.

    A task is a clean success only when every one of its steps has
    ``clean_success`` true.

    A task's wall-clock is the sum of its steps' ``latency_ms``. The
    fixture is sequential. Do not take a max across steps.

    Each arm value is a dict with:

    - ``tasks``: how many distinct ``task_id`` values the arm has.
    - ``clean_successes``: tasks that are clean successes.
    - ``cost_micro_usd``: sum of ``cost_micro_usd`` over every step in
      the arm, including steps on tasks that failed.
    - ``cost_per_clean_success_micro_usd``: that sum floor-divided by
      ``clean_successes`` (``//``). ``None`` when there are no clean
      successes.
    - ``wall_clock_p50_clean_ms``: lower median of wall-clock on clean
      tasks only. Sort ascending and take index ``(count - 1) // 2``.
      ``None`` when there are no clean tasks.
    - ``wall_clock_ms``: sum of ``latency_ms`` over every step in the
      arm, including failures.

    The starter raises.
    """
    del rows
    raise NotImplementedError(
        "summarize_runs is not implemented. See the lab README."
    )


def format_table(summary: dict) -> str:
    """Render ``summary`` as a text table."""
    header = (
        f"{'arm':12} {'clean':8} {'tasks':6} "
        f"{'micro$/clean':14} {'p50 ms':8} {'wait ms':8}"
    )
    lines = [header]
    for arm in ARMS:
        row = summary[arm]
        lines.append(
            f"{arm:12} {row['clean_successes']:8} {row['tasks']:6} "
            f"{str(row['cost_per_clean_success_micro_usd']):14} "
            f"{str(row['wall_clock_p50_clean_ms']):8} "
            f"{row['wall_clock_ms']:8}"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    path = HERE / "fixtures" / "restock_runs.jsonl"
    rows = load_jsonl(path)
    print(f"loaded {len(rows)} recorded steps from {path.name}")
    try:
        summary = summarize_runs(rows)
    except NotImplementedError as exc:
        print(f"TODO: {exc}")
        return 0
    print(format_table(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())
