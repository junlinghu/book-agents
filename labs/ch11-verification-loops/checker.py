"""Cart checker for the Chapter 11 lab.

The recommender proposes a cart. This module is the separate checker.
The starter accepts every cart. Replace the bodies marked TODO.

There is no SOLUTION.md for this lab.
"""

from __future__ import annotations

from dataclasses import dataclass, field


ALLOWED_CITATIONS = {"docs/faq.md", "docs/policy.md"}

# "nuts" on a guest's avoid list covers these catalog allergen strings.
NUT_WORDS = ("almonds", "walnuts", "pecans", "hazelnuts")


@dataclass
class Finding:
    """One rule result. ``severity`` is ``hard`` or ``soft``."""

    severity: str
    rule_id: str
    message: str


@dataclass
class Verdict:
    """Hard findings block the cart. Soft findings ride along."""

    hard: list[Finding] = field(default_factory=list)
    soft: list[Finding] = field(default_factory=list)

    @property
    def accepted(self) -> bool:
        return not self.hard

    def rule_ids(self, severity: str) -> list[str]:
        rows = self.hard if severity == "hard" else self.soft
        return [row.rule_id for row in rows]


def computed_total_cents(proposal: dict, catalog: dict) -> int:
    """Return the catalog total in cents, including the fulfillment fee.

    TODO: price each line from ``catalog`` (not from the proposal) and add:
      - ship: 600 cents when merchandise is under 4000, else 0
      - delivery: 450 cents when merchandise is under 3500, else 0
      - pickup: 0
    Unknown SKUs can be skipped here; ``check_cart`` reports them.
    The starter returns 0 so every stated total looks like a mismatch
    once you start filling ``check_cart`` in. Wire this function in.
    """
    del proposal, catalog
    return 0


def check_cart(proposal: dict, catalog: dict) -> Verdict:
    """Score ``proposal`` against ``catalog``.

    TODO: append hard findings for unknown_sku, bad_qty, missing_citation,
    allergen, over_budget, total_mismatch, not_shippable,
    outside_delivery_window, and bad_fulfillment, using the rules in
    the lab README. Append a soft finding for nut_free_prep when
    ``claims_nut_free_prep`` is true.

    The starter returns an empty verdict, so every cart is accepted.
    """
    del proposal, catalog
    return Verdict()
