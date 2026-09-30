#!/usr/bin/env python3
"""Handoff for the Chapter 23 restock roles.

append_if_valid is the wall. It uses validate_artifact. The pipeline
stops when validation fails and does not show the broken artifact to
the next role.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from contracts import validate_artifact  # noqa: E402
from roles import check, draft_purchase, research  # noqa: E402


def load_json(name: str) -> dict:
    return json.loads((HERE / "fixtures" / name).read_text(encoding="utf-8"))


def append_if_valid(scratchpad: list, role: str, artifact: dict) -> list[str]:
    """Append {author, body} only when the artifact matches the role contract."""
    errors = validate_artifact(role, artifact)
    if errors:
        return errors
    scratchpad.append({"author": role, "body": artifact})
    return []


def run_pipeline(inventory: dict, note: str, catalog: dict) -> dict:
    """Researcher, then buyer, then checker. Stop at the first bad artifact."""
    scratchpad: list = []
    research_artifact = research(inventory, note)
    errors = append_if_valid(scratchpad, "researcher", research_artifact)
    if errors:
        return {
            "route": "split",
            "scratchpad": scratchpad,
            "accepted": False,
            "errors": errors,
        }
    draft = draft_purchase(research_artifact, catalog)
    errors = append_if_valid(scratchpad, "buyer", draft)
    if errors:
        return {
            "route": "split",
            "scratchpad": scratchpad,
            "accepted": False,
            "errors": errors,
        }
    verdict = check(research_artifact, draft, catalog)
    errors = append_if_valid(scratchpad, "checker", verdict)
    if errors:
        return {
            "route": "split",
            "scratchpad": scratchpad,
            "accepted": False,
            "errors": errors,
        }
    return {
        "route": "split",
        "scratchpad": scratchpad,
        "accepted": bool(verdict.get("accepted")),
        "errors": [],
    }


def main(argv: list[str] | None = None) -> int:
    del argv
    inventory = load_json("inventory.json")
    catalog = load_json("catalog.json")
    note = (HERE / "fixtures" / "supplier-note.txt").read_text(encoding="utf-8")
    result = run_pipeline(inventory, note, catalog)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
