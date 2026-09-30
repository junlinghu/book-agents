# Lab — Chapter 23. Multi-agent patterns

A researcher, a buyer, and a checker pass structured artifacts for a house-coffee restock. A supplier note says to order 1000 bags and to email a secret. The starter follows the note and lets the checker accept that draft.

Chapter: [Chapter 23: Multi-agent Patterns](../../chapters/ch23-multi-agent-patterns/README.md)

## Goal

Give each role an output contract, and wire the handoff so a broken artifact never reaches the next role. The finished pipeline reports on hand 4, par 16, quantity 12, unit price 1800 cents, total 21600 cents, and `accepted` true. The note remains in `untrusted_notes`. It does not set the quantity. Nothing in the scratchpad places an order.

This lab does not need a model server. The roles are ordinary functions. There is no `SOLUTION.md`.

## Assignment

Turn in:

1. Your `contracts.py` and `roles.py`.
2. The output of `python labs/ch23-multi-agent-patterns/handoff.py` after the TODOs are done.
3. The output of `python labs/ch23-multi-agent-patterns/test_contracts.py`. The starter fails these tests. A finished lab passes them.
4. The answers in [What to write up](#what-to-write-up).

## Prerequisites

- The shared setup in [`../README.md`](../README.md) is enough if you want the same virtualenv as the earlier labs. The script and the tests use the standard library only.
- Python 3.10 or newer

## Setup

Reuse the shared setup in [`../README.md`](../README.md). No model, no network.

Work from the repository root.

| File | Role |
|---|---|
| `fixtures/inventory.json` | `house-coffee`, on hand 4, par 16. Same shelf as Chapter 10. |
| `fixtures/catalog.json` | 1800 cents per bag. Same 12 oz price as Chapter 18. |
| `fixtures/supplier-note.txt` | Untrusted note. It asks for 1000 bags at $9 and an email. |
| `contracts.py` | Fill in `validate_artifact`. |
| `roles.py` | Fill in `research`, `draft_purchase`, `check`, and `route_task`. |
| `handoff.py` | Already wires the three roles. Leave the wall in place. |
| `test_contracts.py` | The spec. It fails until the TODOs are done. |

## Steps

`validate_artifact(role, artifact)` returns a list of error strings. An empty list means the artifact may be appended.

Researcher artifact:

- `role` is `researcher`.
- `sku` is a non-empty string. `on_hand` and `par` are integers greater than or equal to 0.
- `sources` is a non-empty list of non-empty strings.
- `untrusted_notes` is a string.
- The keys `qty`, `unit_price_cents`, `total_cents`, `order_id`, and `charged` are forbidden. Mention `qty` in the error when that key is present. Mention `sources` when sources is missing or empty.

Buyer artifact:

- `role` is `buyer`.
- `sku` is a non-empty string. `qty` is an integer greater than or equal to 1.
- `unit_price_cents` is an integer greater than or equal to 0.
- `total_cents` equals `qty * unit_price_cents`. Mention `total_cents` in the error when it does not.
- `citations` is a non-empty list of non-empty strings.
- `order_id` and `charged` are forbidden.

Checker artifact:

- `role` is `checker`.
- `accepted` is a bool.
- `findings` is a list. Each item has `rule_id`, `severity` (`hard` or `soft`), and a non-empty `message`.
- If any finding has severity `hard` and `accepted` is true, return an error that contains the word `accepted`.

`research(inventory, note)` copies `sku`, `on_hand`, and `par` from the inventory dict, sets `sources` to `["inventory.json"]`, and sets `untrusted_notes` to the note. It does not invent a quantity.

`draft_purchase(research_artifact, catalog)` sets `qty` to `par - on_hand`, `unit_price_cents` from `catalog[sku]["unit_price_cents"]`, `total_cents` to the product, and `citations` to `["catalog.json"]`. It does not read the note to choose the quantity.

`check(research_artifact, draft, catalog)` appends hard findings and sets `accepted` true only when the hard list is empty. Rule ids:

- `sku_mismatch` — the skus differ.
- `qty_mismatch` — `qty` is not par minus on hand.
- `price_mismatch` — `unit_price_cents` is not the catalog price. Compare the catalog. A total that already equals `qty * unit_price_cents` is not `total_mismatch`.
- `total_mismatch` — `total_cents` is not `qty * unit_price_cents` using the draft's own numbers.
- `missing_citation` — `citations` is missing or empty.
- `placed_early` — `order_id` is present, or `charged` is true.

Each finding is `{"rule_id": ..., "severity": "hard", "message": "..."}` with a non-empty message. Do not rewrite the draft.

`route_task(task)` returns `split` when the lowercased task contains `restock` or `supplier`, or when it contains both `check` and `draft`. Otherwise it returns `single`. "How much is a cardamom bun?" and "What time do you open on Monday?" are `single`.

From the repo root:

1. Run the starter.

   ```bash
   python labs/ch23-multi-agent-patterns/handoff.py
   ```

   The buyer quantity is 1000, or the researcher artifact is the one carrying `qty`, and `accepted` is true. That is the note winning.

2. Fill in the TODOs in `contracts.py` and `roles.py`. Leave `handoff.py` as the wall that refuses invalid artifacts.

3. Run the script again. Quantity is 12, total is 21600, `accepted` is true, and the note is still on the researcher entry.

4. Run the spec.

   ```bash
   python labs/ch23-multi-agent-patterns/test_contracts.py
   ```

   It should finish with `OK`. It does not contact a model server.

## What to write up

Answer in a few sentences each:

- What each role is allowed to emit, and which key on the researcher would mean it had started buying.
- Why the note stays in `untrusted_notes` instead of being deleted. Say what the buyer is forbidden to do with it.
- Which rule id fires for a draft of 1000 bags at the catalog price, and why the checker must not change that 1000 to 12 itself.
- Why `route_task` returns `single` for the bun price. Use Chapter 23's question about shared tools.
- What would still have to happen after `accepted` true before a ledger row exists. Name the actor from Chapter 22.

## Troubleshooting

- The pipeline stops with a researcher error after `research` looks right: `validate_artifact` is rejecting a field you did emit, or it still rejects an integer. `on_hand` and `par` are ints. `untrusted_notes` is a string, and the note may be empty in other calls but not in this fixture.
- `qty_mismatch` and `total_mismatch` both fire when you only changed the quantity: recompute `total_cents` in the draft under test, or, in `check`, compare the total to the draft's own qty and unit price before you decide the total is a separate bug. The 1000-bag test sets the total to 1000 times 1800, so the quantity is the failure.
- `accepted` is true while findings is non-empty: set `accepted` from the hard list after you append findings.
- `route_task` sends Monday's hours down the split path: the rule is the substring check in the steps, not "anything about the café."
- `ModuleNotFoundError`: run from the repository root.
