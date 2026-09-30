#!/usr/bin/env python3
"""Print checker verdicts for every saved proposal.

The starter checker accepts every cart. After you fill in checker.py,
hard failures and soft warnings show up here. This script does not
call a model server.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from checker import check_cart  # noqa: E402


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def format_findings(rows: list) -> str:
    if not rows:
        return "(none)"
    return "; ".join(f"{row.rule_id}: {row.message}" for row in rows)


def main() -> int:
    catalog = load_json(HERE / "catalog.json")
    paths = sorted((HERE / "proposals").glob("*.json"))
    if not paths:
        print("No proposals found.", file=sys.stderr)
        return 1

    accepted = 0
    for path in paths:
        proposal = load_json(path)
        verdict = check_cart(proposal, catalog)
        if verdict.accepted:
            accepted += 1
        print(f"--- {proposal.get('id', path.name)} ---")
        print(f"accepted={verdict.accepted}")
        print(f"hard: {format_findings(verdict.hard)}")
        print(f"soft: {format_findings(verdict.soft)}")
        print()

    print(f"{accepted} of {len(paths)} proposals accepted.")
    if accepted == len(paths):
        print(
            "NOTE: every proposal was accepted. The starter checker does that "
            "until the TODOs in checker.py are filled in."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
