# Lab — Chapter 16. Autonomy policy

A gate in front of five scripted tool calls. `price_check` runs on its own. `place_order` waits for a token. `charge_card` and email outside `hearthlane.example` never run. Mail to the counter waits on a different token.

Chapter: [Chapter 16: Autonomy Policy](../../chapters/ch16-autonomy-policy/README.md)

## Goal

Show that the harness, not the wording of a request, decides which actions run. The script proposes a price check, a two-bun pickup, a card charge, an external email, and an email to `counter@hearthlane.example`. You keep the traces from the unconfirmed run and from the run that approves only the pickup.

The proposals stand in for tool calls a model might make. This lab does not need a model server. The gate is `decide` in `labs/common/autonomy.py`.

## Assignment

Turn in:

1. The full trace of the default run: every `[n]` block, the summary line, and the printed `--confirm` hint.
2. The full trace of the run that passes only the `place_order` token. Include the intent line the script prints.
3. A short note on what stayed denied or unconfirmed after that token: `charge_card`, mail to `sam@example.com`, and mail to `counter@hearthlane.example`.
4. The output of `--self-check`.
5. The answers in [What to write up](#what-to-write-up).

## Prerequisites

- The shared setup in [`../README.md`](../README.md) is enough if you want the same virtualenv as Chapters 1–3. The required traces do not call Ollama, Groq, or OpenRouter.
- Python 3.10 or newer

## Setup

Reuse the shared setup in [`../README.md`](../README.md). You do not need a new virtualenv and you do not need a model for this exercise.

Work from the repository root. The script writes `labs/ch16-autonomy-policy/var/intents.jsonl` only after a matching confirm. That `var/` directory is local output. Menu prices are the counter prices in `labs/ch02-your-first-loop/docs/faq.md`. A cardamom bun is $4.75.

## Steps

The gate this script uses:

- `price_check` is auto. Unknown skus return an error. The bun price is 475 cents.
- `place_order` for pickup is confirm. The arguments include the menu price and `payment_status=not_charged`. Shipping a bun is rejected before a token exists.
- `charge_card` is never. A token computed for the charge itself still does not run it. Card-like numbers are redacted in the trace.
- `send_email` to a domain other than `hearthlane.example` is never. Mail to `counter@hearthlane.example` is confirm, and it has its own token.
- `--confirm TOKEN` approves only the call whose `approval_token` equals `TOKEN`.

From the repo root:

1. Run the proposals with no approval.

   ```bash
   python labs/ch16-autonomy-policy/policy_gate.py
   ```

   The summary should report `intents_written=0`. Copy the `place_order` token from the trace. Do not reuse a token from someone else's run if you have changed the script.

2. Approve only that pickup. `--reset` clears a previous intent file so the confirm run starts clean.

   ```bash
   python labs/ch16-autonomy-policy/policy_gate.py --reset --confirm TOKEN
   ```

   Replace `TOKEN` with the token from step 1. The summary should report `intents_written=1`. The intent's `charged` field is false.

3. Run the checks that do not write `var/`.

   ```bash
   python labs/ch16-autonomy-policy/policy_gate.py --self-check
   python -m unittest labs.common.test_autonomy
   ```

   Both should finish without a failure line. They do not contact a model server.

## What to write up

Answer in a few sentences each:

- For each of the five proposals, the tier and the decision on the unconfirmed run.
- Which arguments the `place_order` token covers, and why a qty of 20 would not be approved by the token for qty 2.
- What the confirmed run wrote, and what it still refused.
- Where a system-prompt sentence such as "do not charge cards" would sit relative to `decide`. The self-check denies `charge_card` with no model in the process.
- One café action you would mark auto, one you would mark confirm, and one you would mark never, using a tool this script does not already list. Say which of Chapter 16's four risk questions pushed it into that tier.

## Troubleshooting

- `intents_written=1` on the first run: the command included `--confirm`. Run again without it.
- The confirm run still says `confirm_required` for `place_order`: the token does not match this script's arguments. Use the token the latest unconfirmed run printed.
- `charge_card` became `allowed`: the tier map was edited. `decide` denies that tool even when `confirmed_token` is the charge's own token. Restore that behavior before you turn the lab in.
- A card number appears in the trace or in `var/intents.jsonl`: the redact path missed it. The number used by the script is a test value and must not be stored. The self-check looks for this.
- `ModuleNotFoundError` for `labs`: run the commands from the repository root, not from inside the lab folder.
