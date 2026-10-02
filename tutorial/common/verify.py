"""Cart checker. It reads stock and the shippable flag itself."""

import json

from tutorial.common.read_db import row_for
from tutorial.common.tools import register

# A destination is served when it names a US state and is not a PO box or an export.
_BLOCKED = ("po box", "p.o. box", "international", "abroad", "canada", "mexico", "europe")
_US_STATES = (
    "alabama", "alaska", "arizona", "arkansas", "california", "colorado",
    "connecticut", "delaware", "florida", "georgia", "hawaii", "idaho",
    "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana",
    "maine", "maryland", "massachusetts", "michigan", "minnesota",
    "mississippi", "missouri", "montana", "nebraska", "nevada",
    "new hampshire", "new jersey", "new mexico", "new york",
    "north carolina", "north dakota", "ohio", "oklahoma", "oregon",
    "pennsylvania", "rhode island", "south carolina", "south dakota",
    "tennessee", "texas", "utah", "vermont", "virginia", "washington",
    "west virginia", "wisconsin", "wyoming", "district of columbia",
)


def destination_served(destination):
    """True for a US state name. Ohio is the lesson's example."""
    text = str(destination or "").strip().lower()
    if not text:
        return False
    if any(word in text for word in _BLOCKED):
        return False
    return any(state in text for state in _US_STATES)


def verify_cart(args):
    """Separate checker. It does not trust qty, ship, or a citation written by the proposer."""
    sku = str(args.get("sku", "")).strip()
    row = row_for(sku)
    findings = []
    stock = None
    if row is None:
        findings.append("unknown_sku")
    else:
        stock = int(row["stock"])
        try:
            qty = int(args.get("qty"))
        except (TypeError, ValueError):
            qty = None
            findings.append("bad_qty")
        if qty is not None and qty < 1:
            findings.append("bad_qty")
        if qty is not None and stock is not None and qty > stock:
            findings.append("qty_exceeds_stock_" + str(stock))
        ship = bool(args.get("ship", False))
        if ship and not row["shippable"]:
            findings.append("not_shippable")
        if ship and not destination_served(args.get("destination", "")):
            findings.append("destination_not_served")
    citation = str(args.get("citation", "")).strip()
    if not citation:
        findings.append("missing_citation")
    status = "rejected" if findings else "accepted"
    return json.dumps({
        "status": status,
        "sku": sku,
        "stock": stock,
        "findings": findings,
    })


register(
    "verify_cart",
    "Check a customer cart before it counts as accepted. "
    "qty must be at least 1 and must not exceed stock. "
    "ship must be false for items that are not shippable. "
    "destination must be a US state such as Ohio when ship is true. "
    "citation must be non-empty. This checker is a separate step from the proposal.",
    {
        "sku": {"type": "string"},
        "qty": {"type": "integer"},
        "ship": {"type": "boolean"},
        "destination": {"type": "string", "description": "State or city and state, such as Ohio."},
        "citation": {"type": "string"},
    },
    ["sku", "qty"],
    verify_cart,
)

__all__ = [
    "destination_served",
    "verify_cart",
]
