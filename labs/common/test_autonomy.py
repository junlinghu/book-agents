"""Autonomy-tier tests that do not call a model server.

Run from the repo root:

    python -m unittest labs.common.test_autonomy
"""

from __future__ import annotations

import unittest

from labs.common.autonomy import (
    ALLOWED,
    CONFIRM,
    CONFIRM_REQUIRED,
    DENIED,
    NEVER,
    approval_token,
    decide,
    is_shop_address,
    redact_arguments,
)


PAN = "4242424242424242"


class AddressTests(unittest.TestCase):
    def test_shop_domain_only(self):
        self.assertTrue(is_shop_address("counter@hearthlane.example"))
        self.assertTrue(is_shop_address("Counter@HearthLane.example"))
        self.assertFalse(is_shop_address("sam@example.com"))
        self.assertFalse(is_shop_address("counter@hearthlane.example.evil.com"))
        self.assertFalse(is_shop_address("not-an-email"))
        self.assertFalse(is_shop_address(""))


class DecideTests(unittest.TestCase):
    def test_price_check_is_auto_without_a_token(self):
        decision = decide("price_check", {"sku": "cardamom-bun"})
        self.assertEqual(decision["tier"], "auto")
        self.assertEqual(decision["decision"], ALLOWED)
        self.assertFalse(decision["confirmed"])

    def test_place_order_waits_until_the_exact_token(self):
        args = {"sku": "cardamom-bun", "qty": 2, "channel": "pickup"}
        pending = decide("place_order", args)
        self.assertEqual(pending["tier"], CONFIRM)
        self.assertEqual(pending["decision"], CONFIRM_REQUIRED)
        token = pending["approval_token"]
        approved = decide("place_order", args, confirmed_token=token)
        self.assertEqual(approved["decision"], ALLOWED)
        self.assertTrue(approved["confirmed"])
        wrong = decide("place_order", args, confirmed_token="00000000")
        self.assertEqual(wrong["decision"], CONFIRM_REQUIRED)

    def test_a_different_quantity_is_a_different_approval(self):
        two = {"sku": "cardamom-bun", "qty": 2, "channel": "pickup"}
        twenty = {"sku": "cardamom-bun", "qty": 20, "channel": "pickup"}
        token = approval_token("place_order", two)
        self.assertNotEqual(token, approval_token("place_order", twenty))
        decision = decide("place_order", twenty, confirmed_token=token)
        self.assertEqual(decision["decision"], CONFIRM_REQUIRED)

    def test_charge_card_stays_denied_with_its_own_token(self):
        args = {"amount_cents": 950, "card_number": PAN}
        token = approval_token("charge_card", args)
        decision = decide("charge_card", args, confirmed_token=token)
        self.assertEqual(decision["tier"], NEVER)
        self.assertEqual(decision["decision"], DENIED)
        self.assertNotIn(PAN, str(decision))
        self.assertEqual(decision["arguments"]["card_number"], "[redacted]")
        self.assertIn("does not charge cards", decision["reason"])

    def test_external_mail_is_never_for_the_concierge(self):
        args = {"to": "sam@example.com", "subject": "receipt", "body": "two buns"}
        token = approval_token("send_email", args)
        decision = decide("send_email", args, confirmed_token=token)
        self.assertEqual(decision["decision"], DENIED)
        self.assertIn("never sent", decision["reason"])

    def test_staff_agent_may_confirm_external_mail_and_still_needs_the_token(self):
        args = {"to": "sam@example.com", "subject": "Your bag", "body": "final sale"}
        pending = decide("send_draft", args, allow_external_mail=True)
        self.assertEqual(pending["tier"], CONFIRM)
        self.assertEqual(pending["decision"], CONFIRM_REQUIRED)
        approved = decide(
            "send_draft",
            args,
            confirmed_token=pending["approval_token"],
            allow_external_mail=True,
        )
        self.assertEqual(approved["decision"], ALLOWED)
        self.assertTrue(approved["confirmed"])

    def test_shop_mail_is_confirm_for_the_concierge(self):
        args = {"to": "counter@hearthlane.example", "subject": "note", "body": "hi"}
        pending = decide("send_email", args)
        self.assertEqual(pending["decision"], CONFIRM_REQUIRED)
        approved = decide(
            "send_email", args, confirmed_token=pending["approval_token"]
        )
        self.assertEqual(approved["decision"], ALLOWED)

    def test_missing_address_is_never_even_for_staff(self):
        decision = decide(
            "send_email",
            {"subject": "note", "body": "hi"},
            allow_external_mail=True,
        )
        self.assertEqual(decision["decision"], DENIED)

    def test_unknown_tool_is_never(self):
        decision = decide("delete_ledger", {"path": "orders"})
        self.assertEqual(decision["tier"], NEVER)
        self.assertEqual(decision["decision"], DENIED)
        self.assertIn("unknown tool", decision["reason"])

    def test_redact_walks_nested_values(self):
        cleaned = redact_arguments(
            {"meta": {"note": PAN}, "ok": "cardamom-bun"}
        )
        self.assertEqual(cleaned["meta"]["note"], "[redacted]")
        self.assertEqual(cleaned["ok"], "cardamom-bun")
        self.assertNotIn(PAN, str(cleaned))


if __name__ == "__main__":
    unittest.main()
