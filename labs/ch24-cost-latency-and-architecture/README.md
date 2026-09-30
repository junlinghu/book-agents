# Lab — Chapter 24. Cost, latency, and architecture

The same weekday restock runs three ways: every step on a small model, every step on a large model, and a router that sends shelf steps to the small model and the note to the large model. You report micro-dollars and wall-clock for the finished tasks. The rows are recorded. No live model.

Chapter: [Chapter 24: Cost, Latency, and Architecture](../../chapters/ch24-cost-latency-and-architecture/README.md)

## Goal

Implement `route` and `summarize_runs`. The router is a function of the tool name. The summary is the Chapter 14 receipt: failed mornings stay in the spend and in the total wait, and they stay out of the clean-success median. You do not train a router, and you do not need an API key.

There is no `SOLUTION.md`.

## Assignment

Turn in:

1. Your `router.py`.
2. The output of `python labs/ch24-cost-latency-and-architecture/router.py`.
3. The output of `python labs/ch24-cost-latency-and-architecture/test_router.py`. `FixtureTests` pass on the starter. `RouteTests` and `SummaryTests` fail until the TODOs are done.
4. The answers in [What to write up](#what-to-write-up).

## Prerequisites

- The shared setup in [`../README.md`](../README.md) for Python. This lab does not read `.env`.

## Setup

Work from the repository root. No model server.

| File | Role |
|---|---|
| `fixtures/restock_runs.jsonl` | Thirty-six recorded steps: three mornings, four steps, three arms. |
| `router.py` | `load_jsonl` and `format_table` are done. `route` and `summarize_runs` are the TODOs. |
| `test_router.py` | The spec. |

The scenario is `weekday_restock`. Each arm runs the same three tasks: `tue_rush`, `wed_dairy`, and `fri_close`. Each task has the same four steps, in order: `read_par`, `read_stock`, `write_qty`, `draft_note`. The arms differ in which model ran, and in whether `draft_note` stayed clean.

| Arm | What ran | What the rows are for |
|---|---|---|
| `all_small` | Small model on every step | The note drops a constraint. The task is not a clean success. |
| `all_large` | Large model on every step | The note holds. Shelf reads are priced like the note. |
| `routed` | Small on the shelf steps, large on `draft_note` | The route in the chapter. The recorded `model` field should match `route`. |

`place_order` is not in the fixture. Chapter 16 still requires a confirm before an order, and this lab does not place one.

## Router

`route(step)` looks at `step["tool"]` and returns a string.

- `read_par`, `read_stock`, and `write_qty` return `small`.
- `draft_note` returns `large`.
- Any other tool raises `ValueError`. Do not send `place_order` or `charge_card` to a model by defaulting unknown tools to `small`.

The direct tests call `route` with a dict that has only `tool`. Do not require `kind`, `arm`, or `model` to be present.

## Receipt

`summarize_runs(rows)` returns a dict keyed by `all_small`, `all_large`, and `routed`.

Group rows by `task_id` inside each arm. A task is a clean success only when every step has `clean_success` true. One failed `draft_note` fails the morning.

For each arm:

- `tasks` is the number of distinct task ids.
- `clean_successes` counts clean tasks.
- `cost_micro_usd` sums `cost_micro_usd` over every step, failures included.
- `cost_per_clean_success_micro_usd` is that sum floor-divided by `clean_successes` (`//`). Use `None` when the arm has no clean success.
- A task's wall-clock is the sum of its steps' `latency_ms`. The runs are sequential.
- `wall_clock_p50_clean_ms` is the lower median of those wall-clocks on clean tasks only: sort ascending, index `(count - 1) // 2`. Use `None` when there is no clean task. Failed tasks do not enter this list.
- `wall_clock_ms` sums `latency_ms` over every step, failures included.

A million micro-dollars is one dollar. The fixture stays in micro-dollars so the division is exact.

## Steps

From the repo root, with the virtualenv active.

1. Skim `fixtures/restock_runs.jsonl`. Notice which arm fails `draft_note`, and which model the `routed` arm used on that step.

2. Run the starter. It loads the rows and stops on the TODO.

   ```bash
   python labs/ch24-cost-latency-and-architecture/router.py
   ```

3. Implement `route` and `summarize_runs`. Run the script again and keep the table.

4. Run the spec.

   ```bash
   python labs/ch24-cost-latency-and-architecture/test_router.py
   ```

   Neither command contacts a hosted API or a local model server.

## What to write up

Paste the table. Then answer, from the rows rather than from memory:

- Which arm has no clean success, and what `cost_per_clean_success_micro_usd` is in that case? Quote the total `cost_micro_usd` you still spent.
- For `all_large` and `routed`, quote micro-dollars per clean success and the clean wall-clock median. Which arm finishes the same mornings for less money and less wait?
- Why the `routed` total is not "the large model's price times three notes." Name the steps that stayed on the small model.
- What `route({"tool": "charge_card"})` does, and why that is not a model choice.
- One harness change the fixture does not measure: replacing `write_qty` with subtraction in code. Say what you would expect to move on the receipt, and what must not move (which line of the note).

## Troubleshooting

- `NotImplementedError` from the script: `summarize_runs` is still the starter. The script returns before the table on purpose.
- Route tests error on `read_par`: `route` is still the starter, or it reads a field the direct tests do not pass.
- `draft_note` routes to `small`: that is the all-small arm. The note is the large-model step.
- Unknown tools return `small`: raise `ValueError` instead. A charge is not a cheap completion.
- `all_small` cost per clean success is `0`: there were no clean successes. Return `None`, and do not divide by zero.
- `routed` micro-dollars per clean success equals one morning's cost: sum every step in the arm, including the other mornings, then floor-divide by the clean-success count.
- Clean wall-clock median equals the failed morning's wait: failed tasks stay out of that list. They stay in `wall_clock_ms` and in `cost_micro_usd`.
- You edited a number in `restock_runs.jsonl`: put it back. The spec matches the recorded file.
