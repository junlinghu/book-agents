# Lab — Chapter 11. Verification loops

A recommender proposes carts. A separate checker accepts or rejects them. The starter checker accepts every cart, including missing citations, nut-allergy hits, and totals over budget.

Chapter: [Chapter 11: Verification Loops](../../chapters/ch11-verification-loops/README.md)

## Goal

Implement `check_cart` in `checker.py` so a proposal is scored against `catalog.json`, not against the recommender's opinion of itself. Hard findings block the cart. Soft findings are attached to a cart that is otherwise allowed. The checker must not rewrite the cart.

This lab does not call a model. The proposals in `proposals/` are the recommender. There is no `SOLUTION.md`.

## Assignment

Turn in:

1. Your `checker.py`.
2. The output of `python labs/ch11-verification-loops/run_check.py` after your checker is in place.
3. The output of `python labs/ch11-verification-loops/test_checker.py`. The starter fails these tests. A finished checker passes them.
4. A short note naming one hard failure and one soft warning from the printed verdicts, with the rule id and the proposal id.
5. A sentence on what the starter was doing before your edit (every cart accepted) and which rule you would promote or demote if Maya disagreed with it.

## Prerequisites

- The shared setup in [`../README.md`](../README.md) is enough for Python. This lab does not read `.env` and does not start Ollama.

## Setup

Do the shared setup in [`../README.md`](../README.md) once if you have not. Work from the repository root. You only need the standard library besides what the shared venv already has. No extra packages.

Files:

| File | Role |
|---|---|
| `catalog.json` | Prices, allergens, and whether the SKU can ship. This is the source of truth. |
| `proposals/*.json` | Carts the recommender already produced, including carts that should fail. |
| `checker.py` | The checker. Fill in the TODOs. |
| `run_check.py` | Prints a verdict for every proposal. |
| `test_checker.py` | The spec. It fails until the TODOs are done. |

## Rules the checker enforces

Prices come from the catalog. Ignore any unit price on the proposal. Quantities are the recommender's.

**Computed total.** Merchandise is `qty * unit_price_cents` for known SKUs. Then add a fulfillment fee:

- `pickup`: 0
- `ship`: 600 cents when merchandise is under 4000 cents, otherwise 0
- `delivery`: 450 cents when merchandise is under 3500 cents, otherwise 0

`computed_total_cents` is where that sum belongs. `check_cart` should use it for the budget and for the stated total.

**Hard rule ids** (block the cart):

- `unknown_sku` — a SKU is not in the catalog.
- `bad_qty` — a quantity is not an integer greater than or equal to 1.
- `bad_fulfillment` — `fulfillment` is not `pickup`, `ship`, or `delivery`.
- `missing_citation` — an item's `citations` list has no path in `docs/faq.md` or `docs/policy.md`. A path such as `docs/blog.md` does not count. One allowed path is enough.
- `allergen` — a catalog allergen hits the guest's avoid list. Compare case-insensitively. The word `nuts` also covers almonds, walnuts, pecans, and hazelnuts. Use the catalog list, not a field the proposal invents. Butter is not milk.
- `over_budget` — the computed total is greater than `budget_cents`. Use the computed total, not `stated_total_cents`.
- `total_mismatch` — `stated_total_cents` is missing or is not the computed total.
- `not_shippable` — `fulfillment` is `ship` and a line's catalog `shippable` value is false. Cardamom buns, drinks, and oat milk do not ship. Coffee does.
- `outside_delivery_window` — `fulfillment` is `delivery` and the first word of `now` is Saturday, Sunday, or Monday. If `now` is absent, do not emit this rule. This lab checks the weekday word, not the hour.

**Soft rule id:**

- `nut_free_prep` — `claims_nut_free_prep` is true. The cart can still be accepted when no hard rule fired. The shop has no nut-free preparation area; the warning flags the sentence.

`Verdict.accepted` is true only when the hard list is empty. A finding needs a non-empty `message` so the printed verdict is readable. Wording is yours. The tests look at `rule_id`.

## Steps

From the repo root, with the virtualenv active.

1. Run the starter. Every proposal is accepted.

   ```bash
   python labs/ch11-verification-loops/run_check.py
   ```

2. Read `checker.py`, `catalog.json`, and two proposals: `nut_allergy.json` and `good_pickup_espresso.json`.

3. Implement `computed_total_cents` and `check_cart`. Re-run the script. You should see hard failures for the bad carts and a soft warning on `nut_free_claim`.

4. Run the spec.

   ```bash
   python labs/ch11-verification-loops/test_checker.py
   ```

   The command does not contact Ollama or a hosted API.

## What to write up

Record:

- One proposal id that is accepted, and one that is not, with the hard rule ids.
- The soft warning you observed: proposal id and rule id.
- Whether `ship_coffee_under_40` stayed accepted. That cart is $18.00 of coffee plus the $6.00 fee, stated as 2400 cents. A checker that forgets the fee will call it a mismatch.
- Whether `nut_allergy` fails because the avoid list says `nuts` and the catalog says `almonds`.
- The sentence from item 5 of Assignment.

## Troubleshooting

- Every cart still accepted: `check_cart` is still the starter. The functions return an empty verdict until you append findings.
- `ship_coffee_under_40` fails `total_mismatch`: the stated total includes the 600-cent fee. Merchandise alone is 1800.
- `ship_coffee_free_over_40` fails `total_mismatch`: three bags are 5400 cents, which is $40 or more, so the ship fee is 0.
- `delivery_wednesday` fails `outside_delivery_window`: Wednesday is inside the Tuesday–Friday window. Saturday is not.
- `nut_free_claim` is a hard failure: that claim is soft. The espresso itself is allowed.
- Tests error on import: run the command from the repo root as written above.
