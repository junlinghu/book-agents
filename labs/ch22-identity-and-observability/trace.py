#!/usr/bin/env python3
"""OTel-shaped traces for a Hearth Lane restock.

Chapter 22 lab. emit_restock_trace() is the success path for session
restock-1842. replay_failure() explains the canned failure from the log
alone. The starter emits no spans and copies a supplier token into the
document. Fill in the TODOs. There is no SOLUTION.md.

No model server. No collector.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FAILURE_LOG = HERE / "fixtures" / "restock-1842-failure.json"

# Stand-in for a credential the place tool might hold. It must not be
# copied into a span. Chapter 21's rule, applied to telemetry.
SUPPLIER_TOKEN = "sup-hearth-canary-do-not-log"

TRACE_ID = "restock-1842"
SERVICE = "hearth-lane-restock"


def emit_restock_trace() -> dict:
    """Return the success document for restock-1842.

    TODO: build the dict described in the lab README. Shelf is on_hand 4,
    par 16, so qty is 12. Confirm actor is the manager (kind user). Place
    returns order_id po-1842. Do not put SUPPLIER_TOKEN anywhere in the
    document.

    The starter returns an empty span list and logs the token.
    """
    return {
        "trace_id": TRACE_ID,
        "service": SERVICE,
        "spans": [],
        "supplier_token": SUPPLIER_TOKEN,
    }


def replay_failure(document: dict) -> dict:
    """Explain a failed restock from the document alone.

    TODO: read the spans. Do not hard-code the fixture's quantity. The
    fields are listed in the lab README. expected_qty is par minus on_hand
    from the read_stock span. order_id is whatever the error span stored
    (null in the canned file).

    The starter returns an empty dict.
    """
    del document
    return {}


def main(argv: list[str] | None = None) -> int:
    del argv
    print("=== emit ===")
    print(json.dumps(emit_restock_trace(), indent=2, sort_keys=True))
    print("=== replay ===")
    document = json.loads(FAILURE_LOG.read_text(encoding="utf-8"))
    print(json.dumps(replay_failure(document), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
