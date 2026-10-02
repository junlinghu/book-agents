"""Auto, confirm, and never for the Harbor Jar seller.

FAQ and catalog reads are auto. A discount and an order note wait for a
person. Charging a card, canceling an order, and emailing a customer
never run, even with a matching token.
"""

import re

from tutorial.common.autonomy import approval_token, decide, format_decision
from tutorial.common.hooks import set_hook
from tutorial.common.paths import VAR
from tutorial.common.read_db import row_for
from tutorial.common.tools import HANDLERS, register

ORDERS = VAR / "orders"

# Readings are auto because they are already in HANDLERS and not listed here.
CONFIRM_TOOLS = {"apply_discount", "file_order_note"}
NEVER_TOOLS = {"charge_card", "cancel_order", "send_customer_email"}


def reset_orders():
    ORDERS.mkdir(parents=True, exist_ok=True)
    for path in ORDERS.glob("*.md"):
        path.unlink()


def gate_call(name, arguments, confirmed_tokens):
    """Return allowed, confirm_required, or denied before any side effect."""
    if name in NEVER_TOOLS:
        expected = approval_token(name, arguments)
        token = expected if expected in confirmed_tokens else None
        return decide(name, arguments, confirmed_token=token)
    if name in CONFIRM_TOOLS:
        tier = "confirm"
    elif name in HANDLERS:
        tier = "auto"
    else:
        tier = "never"
    token = approval_token(name, arguments)
    base = {
        "tool": name,
        "tier": tier,
        "arguments": arguments,
        "approval_token": token,
        "confirmed": False,
    }
    if tier == "never":
        return {
            **base,
            "decision": "denied",
            "reason": "DENIED: " + name + " is not a tool this seller may run.",
        }
    if tier == "confirm":
        if token in confirmed_tokens:
            return {
                **base,
                "decision": "allowed",
                "confirmed": True,
                "reason": "A person approved this exact call.",
            }
        return {
            **base,
            "decision": "confirm_required",
            "reason": "Waiting for a person to approve this exact call.",
        }
    return {
        **base,
        "decision": "allowed",
        "reason": "Auto tier. The harness ran the call without a prompt.",
    }


def apply_discount(args):
    """Record a discount request. The gate must allow the call. Prices in the catalog stay put."""
    code = str(args.get("code", "")).strip().upper()
    if not re.fullmatch(r"[A-Z0-9-]{3,12}", code):
        return "ERROR: code must be a short discount code such as JAR10."
    return (
        "DISCOUNT HELD code=" + code
        + ". A person still completes checkout. No card was charged."
    )


def file_order_note(args):
    """Write one order note for a person to see. This does not charge a card."""
    sku = str(args.get("sku", "")).strip()
    if not re.fullmatch(r"[A-Z0-9-]+", sku):
        return "ERROR: sku is not a catalog id."
    row = row_for(sku)
    if row is None:
        return "ERROR: unknown sku."
    try:
        qty = int(args.get("qty"))
    except (TypeError, ValueError):
        return "ERROR: qty must be an integer."
    if qty < 1 or qty > int(row["stock"]):
        return "ERROR: qty must be between 1 and stock (" + str(row["stock"]) + ")."
    ship = bool(args.get("ship", False))
    if ship and not row["shippable"]:
        return "ERROR: " + row["name"] + " does not ship."
    destination = str(args.get("destination", "")).strip() or "(pickup)"
    customer = str(args.get("customer", "")).strip() or "(customer)"
    citation = str(args.get("citation", "")).strip() or "(none)"
    ORDERS.mkdir(parents=True, exist_ok=True)
    path = ORDERS / (sku + ".md")
    path.write_text(
        "\n".join([
            "# Order note " + sku,
            "",
            "- customer: " + customer,
            "- sku: " + sku,
            "- name: " + row["name"],
            "- qty: " + str(qty),
            "- price: " + row["price"],
            "- stock: " + str(row["stock"]),
            "- ship: " + ("yes" if ship else "no"),
            "- destination: " + destination,
            "- citation: " + citation,
            "- status: confirmed",
            "- charged: no",
            "",
        ]),
        encoding="utf-8",
    )
    return "WROTE orders/" + sku + ".md qty=" + str(qty) + " charged=no"


def charge_card(args):
    del args
    return "ERROR: charge_card has no implementation. The gate should have denied it."


def cancel_order(args):
    del args
    return "ERROR: cancel_order has no implementation. The gate should have denied it."


def send_customer_email(args):
    del args
    return "ERROR: send_customer_email has no implementation. The gate should have denied it."


register(
    "apply_discount",
    "Ask to apply a discount code such as JAR10. "
    "The harness requires a person's approval token before this runs. "
    "It does not change the catalog price and it does not charge a card.",
    {"code": {"type": "string"}},
    ["code"],
    apply_discount,
)
register(
    "file_order_note",
    "Write an order note for one sku after verify_cart has accepted the line. "
    "qty must not exceed stock. The harness requires a person's approval token. "
    "This does not charge a card.",
    {
        "customer": {"type": "string"},
        "sku": {"type": "string"},
        "qty": {"type": "integer"},
        "ship": {"type": "boolean"},
        "destination": {"type": "string"},
        "citation": {"type": "string"},
    },
    ["sku", "qty"],
    file_order_note,
)
register(
    "charge_card",
    "Charge a card. This seller never does that. The harness denies the call.",
    {"amount_cents": {"type": "integer"}},
    ["amount_cents"],
    charge_card,
)
register(
    "cancel_order",
    "Cancel an order. This seller never does that. A person at the store handles cancellations.",
    {"order_id": {"type": "string"}},
    ["order_id"],
    cancel_order,
)
register(
    "send_customer_email",
    "Email a customer. That would send personal details. The harness denies the call.",
    {
        "to": {"type": "string"},
        "body": {"type": "string"},
    },
    ["to", "body"],
    send_customer_email,
)

set_hook("gate_call", gate_call)
set_hook("format_decision", format_decision)

__all__ = [
    "ORDERS",
    "approval_token",
    "apply_discount",
    "cancel_order",
    "charge_card",
    "file_order_note",
    "format_decision",
    "gate_call",
    "reset_orders",
    "send_customer_email",
]
