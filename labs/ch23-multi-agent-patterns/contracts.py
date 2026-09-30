"""Contracts for the Chapter 23 roles.

validate_artifact is the wall between roles. The starter accepts every
dict. Fill in the TODO. There is no SOLUTION.md.
"""

from __future__ import annotations


def validate_artifact(role: str, artifact: dict) -> list[str]:
    """Return contract errors. An empty list means the artifact may be handed off.

    TODO: implement the rules in the lab README.

    Researcher output requires role, sku, on_hand, par, sources, and
    untrusted_notes. It must not include qty, unit_price_cents,
    total_cents, order_id, or charged.

    Buyer output requires role, sku, qty, unit_price_cents, total_cents,
    and citations. total_cents must equal qty times unit_price_cents.
    It must not include order_id or charged.

    Checker output requires role, accepted, and findings. Each finding
    has rule_id, severity (hard or soft), and a non-empty message.
    accepted true is an error when any finding is hard. The error string
    for that case must contain the word accepted.

    Name the offending field in the error string (qty, sources,
    total_cents, accepted) so the tests can see which rule fired.

    The starter returns no errors.
    """
    del role, artifact
    return []
