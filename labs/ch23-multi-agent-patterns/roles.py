"""Researcher, buyer, and checker for a house-coffee restock.

Chapter 23 lab. The supplier note is untrusted. The starter lets that
note set the quantity to 1000 and lets the checker accept the draft.
Fill in the TODOs. There is no SOLUTION.md.

No model server.
"""

from __future__ import annotations


def research(inventory: dict, note: str) -> dict:
    """Report the shelf. File the note as untrusted text.

    TODO: return role, sku, on_hand, and par copied from inventory,
    sources ["inventory.json"], and untrusted_notes equal to note.
    Do not set qty from the note. Do not include a price or an order id.

    The starter emits qty 1000 when the note asks for 1000.
    """
    if "1000" in note:
        return {"role": "researcher", "qty": 1000, "untrusted_notes": note}
    return {"role": "researcher", "untrusted_notes": note}


def draft_purchase(research_artifact: dict, catalog: dict) -> dict:
    """Draft a purchase from the shelf and the catalog.

    TODO: qty is par minus on_hand. unit_price_cents comes from
    catalog[sku]["unit_price_cents"]. total_cents is qty times that
    price. citations is ["catalog.json"]. Ignore untrusted_notes.
    Do not include order_id or charged.

    The starter uses 1000 when the note contains 1000.
    """
    notes = str(research_artifact.get("untrusted_notes", ""))
    qty = 1000 if "1000" in notes else 0
    return {"role": "buyer", "qty": qty}


def check(research_artifact: dict, draft: dict, catalog: dict) -> dict:
    """Accept or reject the draft. Do not rewrite it.

    TODO: append hard findings, then set accepted to true only when
    none are hard. Rule ids:

    - sku_mismatch — draft sku != research sku
    - qty_mismatch — draft qty != par minus on_hand
    - price_mismatch — unit_price_cents != catalog price for the sku
    - total_mismatch — total_cents != qty times unit_price_cents
    - missing_citation — citations missing or empty
    - placed_early — order_id is present or charged is true

    Each finding is {"rule_id", "severity": "hard", "message": "..."}.
    message must be non-empty. Leave the draft's numbers as they are.

    The starter accepts every draft.
    """
    del research_artifact, draft, catalog
    return {"role": "checker", "accepted": True, "findings": []}


def route_task(task: str) -> str:
    """Return 'single' or 'split'.

    TODO: return split when the lowercase task contains 'restock' or
    'supplier', or when it contains both 'check' and 'draft'.
    Otherwise return single.

    The starter always returns split, so a bun-price question takes
    the multi-agent path.
    """
    del task
    return "split"
