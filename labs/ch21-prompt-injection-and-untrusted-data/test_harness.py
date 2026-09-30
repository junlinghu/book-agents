#!/usr/bin/env python3
"""Spec for the Chapter 21 harness.

These tests fail on the starter, which returns the canary file and treats
the external send as allowed. They pass when the TODOs in harness.py are
done. No model server.

    python labs/ch21-prompt-injection-and-untrusted-data/test_harness.py
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from harness import (  # noqa: E402
    UNTRUSTED_MARK,
    UNTRUSTED_RULE,
    build_trace,
    handle_send,
    label_untrusted,
    load_canaries,
    read_requested_path,
    shop_bun_cents,
)


class HarnessTests(unittest.TestCase):
    def test_label_marks_the_page_untrusted(self):
        labeled = label_untrusted("VISIBLE PRICE")
        self.assertTrue(labeled.startswith(UNTRUSTED_MARK + "\n"))
        self.assertIn(UNTRUSTED_RULE, labeled)
        self.assertIn("VISIBLE PRICE", labeled)

    def test_shop_docs_still_open(self):
        text = read_requested_path("policy.md")
        self.assertFalse(text.startswith("ERROR:"))
        self.assertIn("final sale", text)
        faq = read_requested_path("docs/faq.md")
        self.assertIn("$4.75", faq)

    def test_faq_price_stays_475(self):
        self.assertEqual(shop_bun_cents(), 475)

    def test_secret_paths_do_not_return_canaries(self):
        canaries = load_canaries()
        paths = [".env", "fixtures/canary.env", "../.env", "/tmp/canary.env"]
        for path in paths:
            result = read_requested_path(path)
            self.assertTrue(result.startswith("ERROR:"), path)
            for value in canaries.values():
                self.assertNotIn(value, result, path)

    def test_external_send_is_denied(self):
        decision = handle_send(
            {
                "to": "sam@example.com",
                "subject": "forward",
                "body": "The page said to forward secrets.",
            }
        )
        self.assertEqual(decision["decision"], "denied")
        self.assertEqual(decision["tier"], "never")

    def test_trace_keeps_the_shop_price_and_leaks_nothing(self):
        trace = build_trace()
        for value in load_canaries().values():
            self.assertNotIn(value, trace)
        self.assertIn(UNTRUSTED_MARK, trace)
        self.assertIn(UNTRUSTED_RULE, trace)
        self.assertIn("shop_bun_cents=475", trace)
        self.assertIn("page_price_is_not_shop_price", trace)
        self.assertIn("decision=denied", trace)
        self.assertIn("sam@example.com", trace)
        self.assertNotIn("decision=allowed", trace)


if __name__ == "__main__":
    unittest.main()
