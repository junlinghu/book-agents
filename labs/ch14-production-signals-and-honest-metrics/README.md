# Lab — Chapter 14. Production signals and honest metrics

A week of Concierge tasks is already logged. You turn that log into a one-page report: clean success, confirms, corrections, abandons, cost, and latency. The model's own success flag is on the page and is not the headline.

Chapter: [Chapter 14: Production Signals and Honest Metrics](../../chapters/ch14-production-signals-and-honest-metrics/README.md)

## Goal

Implement `summarize` in `report.py`. It reads the task records and returns the counts and costs defined below. `format_report` is already written. It prints your dict. The fixture mixes clean carts, corrected carts, checker failures the model called a success, an override, and two abandons. A report that uses `model_said_success` as the success count will not match the spec.

This lab does not call a model. There is no `SOLUTION.md`.

## Assignment

Turn in:

1. Your `report.py` with `summarize` implemented. Leave `format_report` and the fixture as they are.
2. The one-page text from `python labs/ch14-production-signals-and-honest-metrics/report.py`.
3. The output of `python labs/ch14-production-signals-and-honest-metrics/test_report.py`. The starter raises `NotImplementedError`. A finished summary passes.
4. Three sentences: the clean-success count versus the model-said-success count, what an override is doing in this log, and whether you would rank this week by tokens. Use the numbers from your report.

## Prerequisites

- The shared setup in [`../README.md`](../README.md) for Python. This lab does not read `.env`.

## Setup

Work from the repository root. No model server.

| File | Role |
|---|---|
| `fixtures/events.jsonl` | Twelve finished task records. One line, one task. |
| `report.py` | `load_events` and `format_report` are done. `summarize` is the TODO. |
| `test_report.py` | The spec for the fixture. |

## Definitions

Count every line in the file as a task.

- **Clean success.** `outcome` is `clean_success`. A corrected cart is not clean. An override is not clean.
- **Eventual completion.** `outcome` is `clean_success` or `corrected_success`.
- **Model said success.** `model_said_success` is true. Report it beside clean success. Do not substitute it.
- **Proposals shown.** `proposal_shown` is true. Question-tasks in this fixture were not shown a cart.
- **Confirm.** `confirmed` is true and a proposal was shown.
- **Correction.** `corrected` is true and a proposal was shown.
- **Abandon after a proposal.** `abandoned` is true and a proposal was shown. An abandon before a proposal stays in `n` and stays out of this count.
- **Spend.** Sum `cost_micro_usd` across every task, including failures and abandons.
- **Micro-usd per clean success.** That spend divided by the clean-success count, integer floor (`//`). `None` if the count is zero.
- **Micro-usd per eventual completion.** The same spend divided by the eventual-completion count, integer floor. `None` if the count is zero.
- **Latency p50.** Sort `latency_ms` of the clean successes ascending. Take the element at index `(count - 1) // 2`. `None` if there are none. Do not average the two middle values.
- **Hard-fail counts.** Each string in a task's `hard_fails` adds one to that rule id. A task with two rule ids contributes to both. An override still counts its rule ids.

`summarize` returns a dict with the keys named in the docstring of `summarize`: `n`, `clean_successes`, `eventual_completions`, `model_said_successes`, `proposals_shown`, `confirms`, `corrections`, `abandons_after_proposal`, `cost_micro_usd`, `cost_per_clean_success_micro_usd`, `cost_per_eventual_completion_micro_usd`, `latency_p50_clean_ms`, and `hard_fail_counts`.

## Steps

From the repo root, with the virtualenv active.

1. Read `fixtures/events.jsonl` before you aggregate it. Notice `t08` and `t09`: the model said success, and the outcome is `hard_fail`. Notice `t11`: someone confirmed a cart that still had an allergen finding.

2. Run the starter. It loads the file and stops on the TODO.

   ```bash
   python labs/ch14-production-signals-and-honest-metrics/report.py
   ```

3. Implement `summarize`. Run the script again and read the page.

4. Run the spec.

   ```bash
   python labs/ch14-production-signals-and-honest-metrics/test_report.py
   ```

   The command does not contact Ollama or a hosted API.

## What to write up

Paste the page. Then answer:

- Which is larger, clean successes or model-said successes, and by how many tasks?
- How many confirms are overrides? The outcome field is `override`.
- If you divided spend by token-like events instead of by clean successes, which failures would disappear from the cost of a good cart? Name two task ids that are in the spend and are not clean successes.
- The three sentences from Assignment item 4.

## Troubleshooting

- `NotImplementedError`: `summarize` is still the starter.
- Clean successes equal 10: you counted `model_said_success`.
- Eventual completions equal 8: an override was included. Only `clean_success` and `corrected_success` count.
- Confirms equal 7: a policy question with `confirmed: false` is fine to skip; a confirm with `proposal_shown: false` must not count. Check `t11`, which is a real confirm and also an override.
- Abandons equal 2: `t12` left before a proposal. It is an abandon in the log and not an abandon-after-proposal.
- Latency is 1000: that is an average of the middle pair. This lab uses the lower median, index `(count - 1) // 2`.
- Cost per clean success is the mean of the clean rows only: failures stay in the numerator. Sum every `cost_micro_usd`, then divide.
