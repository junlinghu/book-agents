import json

from tutorial.common.harness import register
from tutorial.common.shelf import gap_for, row_for


def verify_proposal(args):
    """Separate checker. It does not trust qty, ship, or a citation written by the proposer."""
    sku = str(args.get("sku", "")).strip()
    row = row_for(sku)
    findings = []
    expected = None
    if row is None:
        findings.append("unknown_sku")
    else:
        expected = gap_for(row)
        try:
            qty = int(args.get("qty"))
        except (TypeError, ValueError):
            qty = None
            findings.append("bad_qty")
        if qty is not None and qty != expected:
            findings.append("qty_must_be_" + str(expected))
        ship = bool(args.get("ship", False))
        blocked = row["category"] in {"dairy", "bakery"} or "milk" in row["name"].lower()
        if ship and blocked:
            findings.append("not_shippable")
    citation = str(args.get("citation", "")).strip()
    if not citation:
        findings.append("missing_citation")
    status = "rejected" if findings else "accepted"
    return json.dumps({
        "status": status,
        "sku": sku,
        "expected_qty": expected,
        "findings": findings,
    })


register(
    "verify_proposal",
    "Check a restock proposal. qty must be the shelf gap (par minus on_hand). "
    "ship must be false for dairy and bakery. citation must be non-empty. "
    "This checker is not the same step as the proposal.",
    {
        "sku": {"type": "string"},
        "qty": {"type": "integer"},
        "ship": {"type": "boolean"},
        "citation": {"type": "string"},
    },
    ["sku", "qty"],
    verify_proposal,
)
