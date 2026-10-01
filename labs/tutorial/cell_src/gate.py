from labs.tutorial.common.autonomy import approval_token, decide, format_decision

TICKETS = VAR / "tickets"

# Reads and drafts are auto. A ticket waits. Charging and outside mail never run.
AUTO_TOOLS = {
    "get_shop_fact",
    "read_shop_file",
    "query_inventory",
    "list_notes",
    "read_note",
    "memory_search",
    "memory_set",
    "load_skill",
    "fetch_page",
    "verify_proposal",
}
CONFIRM_TOOLS = {"write_ticket"}


def reset_tickets():
    TICKETS.mkdir(parents=True, exist_ok=True)
    for path in TICKETS.glob("*.md"):
        path.unlink()


def gate_call(name, arguments, confirmed_tokens):
    """Same three outcomes as labs.tutorial.common.autonomy.decide: allowed, confirm_required, denied."""
    if name in {"charge_card", "send_email"}:
        expected = approval_token(name, arguments)
        token = expected if expected in confirmed_tokens else None
        return decide(name, arguments, confirmed_token=token)
    if name in AUTO_TOOLS:
        tier = "auto"
    elif name in CONFIRM_TOOLS:
        tier = "confirm"
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
            "reason": "DENIED: " + name + " is not a tool this concierge may run.",
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


def write_ticket(args):
    """File one restock note. The gate must allow the call before this runs."""
    sku = str(args.get("sku", "")).strip()
    if not re.fullmatch(r"[A-Z0-9-]+", sku):
        return "ERROR: sku is not a shelf id."
    row = row_for(sku)
    if row is None:
        return "ERROR: unknown sku."
    expected = gap_for(row)
    try:
        qty = int(args.get("qty"))
    except (TypeError, ValueError):
        return "ERROR: qty must be an integer."
    if qty != expected:
        return "ERROR: qty must be the gap to par (" + str(expected) + ")."
    reason = str(args.get("reason", "")).strip() or "low stock"
    citation = str(args.get("citation", "")).strip() or "(none)"
    TICKETS.mkdir(parents=True, exist_ok=True)
    path = TICKETS / (sku + ".md")
    path.write_text(
        "\n".join([
            "# Restock ticket " + sku,
            "",
            "- sku: " + sku,
            "- name: " + row["name"],
            "- qty: " + str(qty),
            "- on_hand: " + str(row["on_hand"]),
            "- par: " + str(row["par"]),
            "- reason: " + reason,
            "- citation: " + citation,
            "- status: confirmed",
            "",
        ]),
        encoding="utf-8",
    )
    return "WROTE tickets/" + sku + ".md qty=" + str(qty)


def charge_card(args):
    del args
    return "ERROR: charge_card has no implementation. The gate should have denied it."


def send_email(args):
    del args
    return "ERROR: send_email has no implementation. The gate should have denied or held it."


register(
    "write_ticket",
    "Write a restock ticket for one sku. qty must be the shelf gap. "
    "The harness requires a person's approval token before this runs.",
    {
        "sku": {"type": "string"},
        "qty": {"type": "integer"},
        "reason": {"type": "string"},
        "citation": {"type": "string"},
    },
    ["sku", "qty"],
    write_ticket,
)
register(
    "charge_card",
    "Charge a card. This concierge never does that. The harness denies the call.",
    {"amount_cents": {"type": "integer"}},
    ["amount_cents"],
    charge_card,
)
register(
    "send_email",
    "Send email. Mail outside hearthlane.example is never sent. "
    "Mail to the counter waits for a different confirmation.",
    {
        "to": {"type": "string"},
        "body": {"type": "string"},
    },
    ["to", "body"],
    send_email,
)
