#!/usr/bin/env python3
"""Autonomy gate for the Hearth Lane concierge.

Chapter 16 lab. Scripted tool proposals stand in for calls a model might
make, so the trace does not depend on a model server. price_check may run.
place_order waits for this process's confirm token. charge_card and mail
outside hearthlane.example never run.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from labs.common.autonomy import (  # noqa: E402
    ALLOWED,
    CONFIRM_REQUIRED,
    approval_token,
    decide,
    format_decision,
)

# Counter-menu prices copied from labs/ch02-your-first-loop/docs/faq.md.
# A sku that is not in this table is an error, not a guessed price.
PRICES_CENTS = {
    "cardamom-bun": 475,
    "house-espresso": 350,
    "pour-over": 425,
    "oat-milk": 75,
    "rye-porridge": 800,
}

NAMES = {
    "cardamom-bun": "Cardamom bun",
    "house-espresso": "House espresso",
    "pour-over": "Pour-over",
    "oat-milk": "Oat milk add-on",
    "rye-porridge": "Rye porridge",
}

VAR = Path(__file__).resolve().parent / "var"
INTENT_PATH = VAR / "intents.jsonl"
FAQ_PATH = ROOT / "labs" / "ch02-your-first-loop" / "docs" / "faq.md"
PAN = "4242424242424242"


def money(cents: int) -> str:
    return f"${cents // 100}.{cents % 100:02d}"


def price_check(sku: str) -> str:
    if sku not in PRICES_CENTS:
        known = ", ".join(sorted(PRICES_CENTS))
        return f"ERROR: {sku!r} is not on the counter menu. Known skus: {known}."
    cents = PRICES_CENTS[sku]
    return (
        f"{NAMES[sku]} is {money(cents)} ({cents} cents). "
        "Source: docs/faq.md counter menu."
    )


def order_arguments(sku: str, qty: int, channel: str) -> dict | str:
    """Build the call a person would be asked to approve.

    The price comes from the menu table. Shipping a pastry is a shop rule,
    so it fails before the confirm tier is even consulted.
    """
    if sku not in PRICES_CENTS:
        return price_check(sku)
    if qty < 1:
        return "ERROR: qty must be at least 1."
    if channel == "ship":
        return (
            "ERROR: pastries, drinks, and counter food are not shipped "
            "(docs/policy.md). No intent written."
        )
    if channel != "pickup":
        return "ERROR: this lab records pickup only. Use channel=pickup."
    unit = PRICES_CENTS[sku]
    return {
        "sku": sku,
        "qty": qty,
        "channel": channel,
        "unit_price_cents": unit,
        "total_cents": unit * qty,
        "payment_status": "not_charged",
    }


def proposals() -> list[tuple[str, dict]]:
    """The calls a cooperative or a careless model might propose, in order."""
    order = order_arguments("cardamom-bun", 2, "pickup")
    if not isinstance(order, dict):
        raise RuntimeError(order)
    return [
        ("price_check", {"sku": "cardamom-bun"}),
        ("place_order", order),
        ("charge_card", {"amount_cents": order["total_cents"], "card_number": PAN}),
        (
            "send_email",
            {
                "to": "sam@example.com",
                "subject": "Your pickup",
                "body": "Two cardamom buns are set aside.",
            },
        ),
        (
            "send_email",
            {
                "to": "counter@hearthlane.example",
                "subject": "Pickup slip",
                "body": "Two cardamom buns for the counter.",
            },
        ),
    ]


def execute(name: str, arguments: dict, decision: dict, intent_path: Path) -> str:
    if decision["decision"] != ALLOWED:
        if name == "place_order":
            return "not executed; no intent written"
        return "not executed"
    if name == "price_check":
        return price_check(str(arguments.get("sku", "")))
    if name == "place_order":
        record = {
            "intent_id": decision["approval_token"],
            "sku": arguments["sku"],
            "qty": arguments["qty"],
            "channel": arguments["channel"],
            "total_cents": arguments["total_cents"],
            "charged": False,
            "payment_status": "not_charged",
        }
        intent_path.parent.mkdir(parents=True, exist_ok=True)
        with intent_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
        return "intent written " + json.dumps(record, sort_keys=True)
    return "not executed"


def run_gate(confirmed_token: str | None, intent_path: Path) -> str:
    if intent_path.exists():
        intent_path.unlink()
    lines = [
        "Hearth Lane concierge — autonomy gate",
        "model=scripted proposals (no model server on this path)",
        f"intent_file={intent_path}",
        "",
    ]
    counts = {ALLOWED: 0, CONFIRM_REQUIRED: 0, "denied": 0}
    place_token = None
    for index, (name, arguments) in enumerate(proposals(), start=1):
        decision = decide(name, arguments, confirmed_token=confirmed_token)
        counts[decision["decision"]] = counts.get(decision["decision"], 0) + 1
        if name == "place_order" and decision["tier"] == "confirm":
            place_token = decision["approval_token"]
        result = execute(name, arguments, decision, intent_path)
        lines.append(f"[{index}] {name}")
        lines.append("    " + format_decision(decision).replace("\n", "\n    "))
        lines.append(f"    result={result}")
        lines.append("")
    written = 0
    if intent_path.exists():
        written = len(intent_path.read_text(encoding="utf-8").splitlines())
    lines.append(
        "--- summary ---\n"
        f"allowed={counts.get(ALLOWED, 0)} "
        f"confirm_required={counts.get(CONFIRM_REQUIRED, 0)} "
        f"denied={counts.get('denied', 0)} "
        f"intents_written={written}"
    )
    if place_token and confirmed_token != place_token:
        lines.append(
            "To approve only the place_order call, rerun with:\n"
            f"  python labs/ch16-autonomy-policy/policy_gate.py --confirm {place_token}"
        )
    lines.append(
        "charge_card and external send stay denied if you pass that token. "
        "Mail to counter@hearthlane.example stays on confirm until its own token is passed."
    )
    return "\n".join(lines) + "\n"


def self_check() -> int:
    """Checks that do not need a model or the var/ directory."""
    failures: list[str] = []

    def expect(condition: bool, label: str) -> None:
        if condition:
            print(f"ok {label}")
        else:
            failures.append(label)
            print(f"FAIL {label}")

    faq = FAQ_PATH.read_text(encoding="utf-8")
    expect("$4.75" in faq, "faq lists the cardamom bun at $4.75")
    expect(PRICES_CENTS["cardamom-bun"] == 475, "gate price matches 475 cents")

    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "intents.jsonl"
        pending = run_gate(None, path)
        expect("4242424242424242" not in pending, "pending trace redacts the card number")
        expect("decision=allowed" in pending and "price_check" in pending, "price check runs")
        expect("intents_written=0" in pending, "unconfirmed place_order writes nothing")
        expect(not path.exists(), "intent file absent until confirm")
        expect("sam@example.com" in pending and "never sent" in pending, "external mail denied")
        expect("counter@hearthlane.example" in pending, "shop mail is shown")

        order = order_arguments("cardamom-bun", 2, "pickup")
        assert isinstance(order, dict)
        token = approval_token("place_order", order)
        approved = run_gate(token, path)
        expect("intents_written=1" in approved, "matching token writes one intent")
        expect('"charged": false' in approved, "intent is not a charge")
        expect("4242424242424242" not in approved, "confirmed trace redacts the card number")
        text = path.read_text(encoding="utf-8")
        expect(PAN not in text, "intent file has no card number")
        expect(text.count("\n") == 1, "one intent line")

        charge = decide(
            "charge_card",
            {"amount_cents": 950, "card_number": PAN},
            confirmed_token=approval_token(
                "charge_card", {"amount_cents": 950, "card_number": PAN}
            ),
        )
        expect(charge["decision"] == "denied", "charge token does not unlock charge_card")

        shipped = order_arguments("cardamom-bun", 1, "ship")
        expect(
            isinstance(shipped, str) and shipped.startswith("ERROR"),
            "shipping a bun is rejected before confirm",
        )

    if failures:
        print(f"{len(failures)} failed")
        return 1
    print("self-check passed")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--confirm",
        metavar="TOKEN",
        help="approve the single call whose approval_token matches TOKEN",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="delete var/intents.jsonl before the run",
    )
    parser.add_argument(
        "--self-check",
        action="store_true",
        help="run the no-model checks and exit",
    )
    args = parser.parse_args(argv)
    if args.self_check:
        return self_check()
    if args.reset and INTENT_PATH.exists():
        INTENT_PATH.unlink()
    print(run_gate(args.confirm, INTENT_PATH), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
