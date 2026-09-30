#!/usr/bin/env python3
"""Spec for the Chapter 22 trace.

These tests fail on the starter. They pass when emit_restock_trace and
replay_failure match the lab README. No model server.

    python labs/ch22-identity-and-observability/test_trace.py
"""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from trace import (  # noqa: E402
    FAILURE_LOG,
    SUPPLIER_TOKEN,
    emit_restock_trace,
    replay_failure,
)

REQUIRED_SPAN_KEYS = {
    "span_id",
    "trace_id",
    "parent_span_id",
    "name",
    "actor",
    "status",
    "attributes",
}


def load_failure() -> dict:
    return json.loads(FAILURE_LOG.read_text(encoding="utf-8"))


class EmitTests(unittest.TestCase):
    def setUp(self):
        self.document = emit_restock_trace()

    def test_token_is_absent(self):
        blob = json.dumps(self.document)
        self.assertNotIn(SUPPLIER_TOKEN, blob)
        self.assertNotIn("supplier_token", blob)

    def test_identity_of_the_document(self):
        self.assertEqual(self.document["trace_id"], "restock-1842")
        self.assertEqual(self.document["service"], "hearth-lane-restock")
        self.assertIsInstance(self.document["spans"], list)
        self.assertGreaterEqual(len(self.document["spans"]), 4)

    def test_span_shape_and_parents(self):
        spans = self.document["spans"]
        ids = [span["span_id"] for span in spans]
        self.assertEqual(len(ids), len(set(ids)))
        known = set(ids)
        roots = []
        for span in spans:
            self.assertEqual(set(span), REQUIRED_SPAN_KEYS)
            self.assertEqual(span["trace_id"], "restock-1842")
            self.assertIn(span["status"], {"ok", "error"})
            actor = span["actor"]
            self.assertEqual(set(actor), {"kind", "id"})
            self.assertIn(actor["kind"], {"user", "agent", "tool"})
            parent = span["parent_span_id"]
            self.assertIsInstance(parent, str)
            if parent == "":
                roots.append(span)
            else:
                self.assertIn(parent, known)
        self.assertEqual(len(roots), 1)
        self.assertEqual(roots[0]["name"], "restock")

    def test_success_actors_and_quantities(self):
        by_name = {span["name"]: span for span in self.document["spans"]}
        for name in ("read_stock", "draft_order", "confirm", "place_order"):
            self.assertIn(name, by_name)
        read = by_name["read_stock"]
        draft = by_name["draft_order"]
        confirm = by_name["confirm"]
        place = by_name["place_order"]
        self.assertEqual(read["actor"], {"kind": "tool", "id": "inventory"})
        self.assertEqual(read["status"], "ok")
        self.assertEqual(read["attributes"]["sku"], "house-coffee")
        self.assertEqual(read["attributes"]["on_hand"], 4)
        self.assertEqual(read["attributes"]["par"], 16)
        self.assertEqual(draft["actor"], {"kind": "agent", "id": "restock-agent"})
        self.assertEqual(draft["attributes"]["qty"], 12)
        self.assertEqual(confirm["actor"], {"kind": "user", "id": "manager"})
        self.assertEqual(confirm["attributes"]["qty"], 12)
        self.assertEqual(confirm["status"], "ok")
        self.assertEqual(place["actor"], {"kind": "tool", "id": "ledger"})
        self.assertEqual(place["status"], "ok")
        self.assertEqual(place["attributes"]["qty"], 12)
        self.assertEqual(place["attributes"]["order_id"], "po-1842")
        self.assertEqual(place["attributes"]["idempotency_key"], "restock-1842")


class ReplayTests(unittest.TestCase):
    def test_canned_failure(self):
        result = replay_failure(load_failure())
        self.assertEqual(result["trace_id"], "restock-1842")
        self.assertEqual(result["failed_span"], "place_order")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["reason"], "confirm actor was agent, expected user")
        self.assertEqual(result["on_hand"], 4)
        self.assertEqual(result["par"], 16)
        self.assertEqual(result["draft_qty"], 20)
        self.assertEqual(result["expected_qty"], 12)
        self.assertEqual(result["confirm_actor_kind"], "agent")
        self.assertEqual(result["confirm_actor_id"], "restock-agent")
        self.assertIsNone(result["order_id"])

    def test_replay_reads_the_log_instead_of_memorizing_it(self):
        document = load_failure()
        for span in document["spans"]:
            if span["name"] == "draft_order":
                span["attributes"]["qty"] = 18
            if span["name"] == "read_stock":
                span["attributes"]["on_hand"] = 5
                span["attributes"]["par"] = 16
        result = replay_failure(copy.deepcopy(document))
        self.assertEqual(result["draft_qty"], 18)
        self.assertEqual(result["on_hand"], 5)
        self.assertEqual(result["expected_qty"], 11)
        self.assertEqual(result["failed_span"], "place_order")


if __name__ == "__main__":
    unittest.main()
