"""One-page metrics for a week of Concierge tasks.

``load_events`` is done. ``summarize`` is the TODO. There is no
SOLUTION.md. Definitions are in the lab README.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def load_events(path: Path) -> list[dict]:
    """Load a JSONL file of task records."""
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def summarize(events: list[dict]) -> dict:
    """Aggregate Chapter 14 metrics for ``events``.

    TODO: return a dict with these keys.

    - ``n``: number of tasks.
    - ``clean_successes``: outcome ``clean_success``.
    - ``eventual_completions``: outcome ``clean_success`` or
      ``corrected_success``. An override is not an eventual completion.
    - ``model_said_successes``: ``model_said_success`` is true. This is
      the proxy. Do not use it as ``clean_successes``.
    - ``proposals_shown``: ``proposal_shown`` is true.
    - ``confirms``: ``confirmed`` and ``proposal_shown``.
    - ``corrections``: ``corrected`` and ``proposal_shown``.
    - ``abandons_after_proposal``: ``abandoned`` and ``proposal_shown``.
    - ``cost_micro_usd``: sum of ``cost_micro_usd`` over every task,
      including failures.
    - ``cost_per_clean_success_micro_usd``: that sum divided by
      ``clean_successes``, integer floor. ``None`` when there are no
      clean successes.
    - ``cost_per_eventual_completion_micro_usd``: the same sum divided
      by ``eventual_completions``, integer floor. ``None`` when there
      are none.
    - ``latency_p50_clean_ms``: lower median of ``latency_ms`` on clean
      successes. Sort ascending and take index ``(count - 1) // 2``.
      ``None`` when there are no clean successes.
    - ``hard_fail_counts``: a dict of rule id to how many times it
      appears in any task's ``hard_fails`` list.

    The starter raises so a half-filled report is not mistaken for a
    finished page.
    """
    raise NotImplementedError(
        "summarize is not implemented. See the lab README for the keys."
    )


def format_report(summary: dict) -> str:
    """Render ``summary`` as a one-page text report."""
    lines = [
        "Hearth Lane Concierge — task report",
        f"tasks: {summary['n']}",
        f"clean successes: {summary['clean_successes']}",
        f"eventual completions: {summary['eventual_completions']}",
        f"model said success: {summary['model_said_successes']}",
        f"proposals shown: {summary['proposals_shown']}",
        f"confirms: {summary['confirms']}",
        f"corrections: {summary['corrections']}",
        f"abandons after a proposal: {summary['abandons_after_proposal']}",
        f"spend micro-usd: {summary['cost_micro_usd']}",
        f"micro-usd per clean success: {summary['cost_per_clean_success_micro_usd']}",
        (
            "micro-usd per eventual completion: "
            f"{summary['cost_per_eventual_completion_micro_usd']}"
        ),
        f"clean-success latency p50 ms: {summary['latency_p50_clean_ms']}",
        "hard fails:",
    ]
    counts = summary["hard_fail_counts"]
    if not counts:
        lines.append("  (none)")
    else:
        for rule_id in sorted(counts):
            lines.append(f"  {rule_id}: {counts[rule_id]}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    path = Path(__file__).resolve().parent / "fixtures" / "events.jsonl"
    events = load_events(path)
    print(f"loaded {len(events)} tasks from {path.name}")
    try:
        summary = summarize(events)
    except NotImplementedError as exc:
        print(f"TODO: {exc}")
        return 0
    print(format_report(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())
