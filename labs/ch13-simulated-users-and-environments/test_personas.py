#!/usr/bin/env python3
"""CI assertions for the three Chapter 13 personas.

Fails on the starter policy. Passes when ``choose_actions`` meets
every persona expectation and never uses a forbidden action.

    python labs/ch13-simulated-users-and-environments/test_personas.py
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from policy import choose_actions  # noqa: E402
from world import FORBIDDEN, personas, run_episode  # noqa: E402


def episode(persona_id: str) -> dict:
    persona = next(row for row in personas() if row["id"] == persona_id)
    world = {"clock": persona["clock"], "stock": dict(persona["stock"])}
    return run_episode(persona, choose_actions(persona, world))


class PersonaTests(unittest.TestCase):
    def test_three_personas_are_loaded(self):
        ids = [row["id"] for row in personas()]
        self.assertEqual(
            ids, ["skeptical_owner", "rushed_barista", "allergic_saturday"]
        )

    def test_skeptical_owner(self):
        result = episode("skeptical_owner")
        self.assertTrue(result["ok"], result["problems"])

    def test_rushed_barista(self):
        result = episode("rushed_barista")
        self.assertTrue(result["ok"], result["problems"])

    def test_allergic_saturday(self):
        result = episode("allergic_saturday")
        self.assertTrue(result["ok"], result["problems"])

    def test_no_forbidden_actions_on_a_finished_policy(self):
        for persona in personas():
            result = episode(persona["id"])
            kinds = {action.get("type") for action in result["actions"]}
            self.assertTrue(kinds.isdisjoint(FORBIDDEN), result)


if __name__ == "__main__":
    unittest.main()
