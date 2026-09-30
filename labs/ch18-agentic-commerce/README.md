# Lab — Chapter 18. Agentic commerce

A mock checkout for Hearth Lane Café. A confirmed quote inserts one row in a local SQLite `orders` table. Payment status stays `mock_not_charged`. There is no card charge and no payment network.

Chapter: [Chapter 18: Agentic Commerce](../../chapters/ch18-agentic-commerce/README.md)

## Goal

Walk catalog, quote, and checkout until you can point at a receipt. The unconfirmed run must leave `orders=0`. The confirmed run must print one receipt for a single 12 oz bag shipped on Tuesday, and that receipt must say the card was not charged.

The bag price is catalog data: $18.00 in `catalog.json`. It is not listed in `docs/faq.md`. Menu prices that do appear in the FAQ (the bun at $4.75, the espresso at $3.50) match the catalog. Shipping and delivery rules come from `docs/policy.md`.

## Assignment

Turn in:

1. The full trace of the unconfirmed run (`--reset` first), including the bun rejection, the Monday rejection, the $24.00 quote waiting on confirm, the three-bag quote with a $0.00 fee, the `charge_card` denial, and `orders=0`.
2. The full trace of `--reset --confirm TOKEN` for the one-bag quote, including the receipt and `house_coffee_on_hand=19`.
3. The output of `--self-check`.
4. The answers in [What to write up](#what-to-write-up).

Do not add a payment SDK, a processor key, or a card column. A trace that shows a live or sandbox charge does not complete this lab.

## Prerequisites

- The shared setup in [`../README.md`](../README.md). The required traces do not call a model server.
- Python 3.10 or newer, with the standard-library `sqlite3` module
- The confirm gate from `labs/common/autonomy.py` (Chapter 16)

## Setup

Reuse the shared setup in [`../README.md`](../README.md). This exercise does not need a new account or a network credential.

Work from the repository root. The database is `labs/ch18-agentic-commerce/var/shop.db`, created on the first run and replaced when you pass `--reset`. It is local output. The seed catalog is `labs/ch18-agentic-commerce/catalog.json`.

## Steps

What the script enforces before it will insert a row:

- Prices and stock come from the `stock` table seeded from the catalog. An unknown sku errors.
- A cardamom bun cannot be shipped. A house espresso cannot be bike-delivered. Hot drinks stay at the counter.
- Coffee ships inside the United States only, not to a PO box, and not on Monday. Under $40 the fee is $6.00. At $40 or more the fee is $0.00.
- Local delivery, covered by `--self-check`, is $4.50 under $35, free at $35 or more, Tuesday through Friday, within 3 miles.
- `checkout` is confirm. The token covers the quote, including the total. Stock decrements only inside the same transaction as the insert.
- `charge_card` is never. The test card number is redacted and is not stored.

From the repo root:

1. Reset the database and run the story without approving checkout.

   ```bash
   python labs/ch18-agentic-commerce/checkout.py --reset
   ```

   Expect `orders=0` and `house_coffee_on_hand=20`. Copy the checkout token from the one-bag quote. The three-bag block is a quote only. It must not be the call you confirm.

2. Reset again and approve that one-bag quote. Resetting keeps the receipt to a single row. A second confirm on the same database would place a second order.

   ```bash
   python labs/ch18-agentic-commerce/checkout.py --reset --confirm TOKEN
   ```

   Replace `TOKEN` with the token from step 1. Expect `orders=1`, `house_coffee_on_hand=19`, `payment_status: mock_not_charged`, and `card_charged: no`.

3. Run the checks that use a temporary database, not `var/shop.db`.

   ```bash
   python labs/ch18-agentic-commerce/checkout.py --self-check
   ```

   You want passing lines for the bun, Monday, the $40 boundary, the delivery fee, the missing card number in the database file, and the missing card column.

## What to write up

Answer in a few sentences each:

- The one-bag arithmetic: unit price, shipping fee, total, and the policy sentence that sets the fee. Say where the $18.00 price lives, and that `faq.md` does not list it.
- Why the bun quote and the Monday quote produced no token and no row.
- The receipt fields from step 2. Include `status`, `payment_status`, `confirmed_by`, and the stock count after the insert.
- Which of the four parties (customer, café, agent, payment network) this database row informs, and which party the lab leaves out on purpose.
- What would be wrong with treating the model's sentence "your order has shipped" as the receipt when the summary says `orders=0`.

## Troubleshooting

- `orders=0` after `--confirm`: the token does not match the one-bag quote. Tokens from an edited catalog will not match. Re-run step 1 and use the new token.
- `orders=2` or `on_hand=18`: step 2 ran without `--reset` on a database that already had a confirmed order. Run step 2 again with `--reset`.
- A card number in the trace or in `shop.db`: the run is not the one this lab asks for. `--self-check` reads the database bytes and should report that the number is absent.
- The three-bag total was inserted: that block is `quote_only`. Confirm only the token printed under the one-bag quote.
- `ModuleNotFoundError` for `labs`: run from the repository root.
