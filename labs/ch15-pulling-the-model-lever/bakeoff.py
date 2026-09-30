#!/usr/bin/env python3
"""Score a recorded skill-patch vs model-swap bake-off.

The rows already carry checker verdicts. You aggregate them. No cluster
and no model server. There is no SOLUTION.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from pairs import load_jsonl  # noqa: E402


def summarize_bakeoff(rows: list[dict]) -> dict:
    """Summarize each ``arm``.

    TODO: return a dict keyed by arm id (``small_v1``, ``small_v2``,
    ``large_v1``). Each value is a dict with:

    - ``tasks``: rows in that arm.
    - ``clean_successes``: rows whose ``clean_success`` is true.
    - ``cost_micro_usd``: sum of ``cost_micro_usd`` for every row in the
      arm, including failures.
    - ``cost_per_clean_success_micro_usd``: that sum floor-divided by
      ``clean_successes``. ``None`` when there are no clean successes.
    - ``latency_p50_clean_ms``: lower median of ``latency_ms`` on the
      clean successes only. Sort ascending and take index
      ``(count - 1) // 2``. ``None`` when there are none.

    The starter raises.
    """
    del rows
    raise NotImplementedError(
        "summarize_bakeoff is not implemented. See the lab README."
    )


def format_table(summary: dict) -> str:
    header = (
        f"{'arm':12} {'clean':8} {'tasks':6} "
        f"{'micro$/clean':14} {'p50 ms':8}"
    )
    lines = [header]
    for arm in ("small_v1", "small_v2", "large_v1"):
        row = summary[arm]
        lines.append(
            f"{arm:12} {row['clean_successes']:8} {row['tasks']:6} "
            f"{str(row['cost_per_clean_success_micro_usd']):14} "
            f"{str(row['latency_p50_clean_ms']):8}"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    path = HERE / "fixtures" / "bakeoff_rows.jsonl"
    rows = load_jsonl(path)
    print(f"loaded {len(rows)} recorded rows from {path.name}")
    try:
        summary = summarize_bakeoff(rows)
    except NotImplementedError as exc:
        print(f"TODO: {exc}")
        return 0
    print(format_table(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())
