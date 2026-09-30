# Lab — Chapter 13. Simulated users and environments

A CI-style job runs three personas against a fake clock and a fake shelf. It asserts cart constraints and asserts that the agent never charges a card, sends mail, or deletes stock.

Chapter: [Chapter 13: Simulated Users and Environments](../../chapters/ch13-simulated-users-and-environments/README.md)

## Goal

Replace the starter in `policy.py`. `choose_actions` reads one persona and that persona's world, and returns a short list of actions. `world.py` is the simulation. It resets nothing for you to edit: each episode already gets its own clock and stock. The job goes green only when Jules, Rafi, and Sam are all satisfied and no forbidden action appears.

This lab does not call a model. There is no `SOLUTION.md`.

## Assignment

Turn in:

1. Your `policy.py`. Leave `world.py`, `personas.json`, and `catalog.json` unchanged. Editing the oracle so a bad policy passes is a failed assignment.
2. The output of `python labs/ch13-simulated-users-and-environments/run_personas.py`. The starter exits 1. Your policy should exit 0.
3. The output of `python labs/ch13-simulated-users-and-environments/test_personas.py`.
4. A short trace note for each persona: the action types you returned, the clock you were given, and which constraint would have failed if you had returned the starter cart.
5. One sentence on a fact the simulation does not model. Say whether that omission could hide a harmful cart.

## Prerequisites

- The shared setup in [`../README.md`](../README.md) for Python. This lab does not read `.env`.

## Setup

Work from the repository root. No model server.

| File | Role |
|---|---|
| `personas.json` | Jules, Rafi, and Sam: clock, stock, budget, avoid list, and what the episode expects. |
| `catalog.json` | Prices and allergens the assertions use. |
| `world.py` | Applies actions and records problems. The CI oracle. |
| `policy.py` | Your agent. The TODO. |
| `run_personas.py` | Runs all three and exits 1 if any fail. |
| `test_personas.py` | The same assertions under unittest. |

## What each persona requires

**Jules (`skeptical_owner`).** Wednesday 09:10. Budget 5000 cents. Action `propose_cart`, fulfillment `pickup`, items exactly one line: `house-coffee-12oz` with `qty` 2. That line cites `docs/faq.md` or `docs/policy.md`. `stated_total_cents` is 3600. At most one `ask`.

**Rafi (`rushed_barista`).** Thursday 07:40. Oat milk and cardamom buns are at 0. Coffee is not. Action `propose_restock` whose items include `oat-milk` and `cardamom-bun` and do not include a SKU that is still in stock. Items may be SKU strings or `{"sku": "..."}` objects. At most one `ask`. Do not lecture, and do not place a customer cart.

**Sam (`allergic_saturday`).** Saturday 09:00. Avoids nuts. Budget 1500 cents. The bun is in stock; the refusal is the allergen, not a stockout. Action `propose_cart`, fulfillment `pickup`, at least one `house-espresso`, no `cardamom-bun`, citations on every line, `stated_total_cents` equal to the catalog sum, total within budget. Espresso is 350 cents. At most one `ask`.

Forbidden for every persona: `charge_card`, `send_email`, `delete_inventory`. Returning one of these fails the episode even if a later action would have been fine. The starter returns `charge_card` on purpose.

## Steps

From the repo root, with the virtualenv active.

1. Run the starter and read which problems fire.

   ```bash
   python labs/ch13-simulated-users-and-environments/run_personas.py
   ```

2. Read the three objects in `personas.json` and the checks in `world.py`. Then replace the body of `choose_actions`. Branch on `persona["id"]`. Read `world["clock"]` and `world["stock"]` even if you also trust the persona fields. They are the same values, injected the way a later tool would return them.

3. Re-run the script. Then run the tests.

   ```bash
   python labs/ch13-simulated-users-and-environments/test_personas.py
   ```

   Neither command contacts Ollama or a hosted API.

## What to write up

Record:

- The problem lines the starter printed for each persona.
- The actions you return for each id, including `stated_total_cents` where you propose a cart.
- Whether Sam's cart includes a bun. It should not, even though `stock["cardamom-bun"]` is 12.
- Whether Rafi's restock includes `house-coffee-12oz`. It should not. Six bags are still on the shelf.
- The sentence from Assignment item 5.

## Troubleshooting

- `forbidden:charge_card`: the starter's second action is still in the list you return.
- `items` on Jules: the cart must be exactly two bags of `house-coffee-12oz`, not one bag and not a bun beside them.
- `total` on Jules: 2 × 1800 = 3600. A stated total of 1 fails.
- `restock_in_stock`: you named a SKU whose stock count is above zero.
- `allergen:cardamom-bun` or `forbid_sku:cardamom-bun`: Sam's opening asked for a bun. The policy still refuses it. Pickup espresso is the cart.
- `fulfillment:delivery` on Sam: Saturday is outside the delivery window. The expectation is pickup.
- The script exits 1: that is a failed persona, not a broken Python install. Read the problem lines.
