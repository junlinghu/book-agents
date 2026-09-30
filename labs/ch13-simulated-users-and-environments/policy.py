"""Agent under test for the Chapter 13 personas.

Replace ``choose_actions``. The starter proposes an almond bun for
delivery and then charges a card, so every persona fails.

There is no SOLUTION.md. The assertions live in ``world.py``.
"""

from __future__ import annotations


def choose_actions(persona: dict, world: dict) -> list[dict]:
    """Return the actions this persona's episode should take.

    ``persona`` is one object from ``personas.json``. ``world`` has
    ``clock`` and ``stock`` for that episode. Branch on ``persona["id"]``.

    Allowed action types:

    - ``propose_cart`` with ``fulfillment``, ``stated_total_cents``, and
      ``items`` of ``{sku, qty, citations}``.
    - ``propose_restock`` with ``items`` listing SKUs that are actually out.
    - ``ask`` with ``text``, at most ``patience_asks`` times.

    ``charge_card``, ``send_email``, and ``delete_inventory`` are forbidden.
    TODO: replace the body below.
    """
    del world
    return [
        {
            "type": "propose_cart",
            "fulfillment": "delivery",
            "stated_total_cents": 1,
            "items": [{"sku": "cardamom-bun", "qty": 2, "citations": []}],
        },
        {"type": "charge_card", "cents": 100},
    ]
