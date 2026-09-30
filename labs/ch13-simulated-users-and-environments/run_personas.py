#!/usr/bin/env python3
"""CI-style run of the three personas.

Exits 1 when any persona fails. The starter fails all three. No model
server is contacted.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from policy import choose_actions  # noqa: E402
from world import personas, run_episode  # noqa: E402


def main() -> int:
    failed = 0
    for persona in personas():
        world = {"clock": persona["clock"], "stock": dict(persona["stock"])}
        result = run_episode(persona, choose_actions(persona, world))
        status = "ok" if result["ok"] else "FAIL"
        print(f"{result['persona']}: {status}")
        for problem in result["problems"]:
            print(f"  {problem}")
        if not result["ok"]:
            failed += 1
    print(f"{failed} of {len(personas())} personas failed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
