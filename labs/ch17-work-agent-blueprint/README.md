# Lab — Chapter 17. Work-agent blueprint

A staff work agent reads the café policy, writes a draft email, and copies it to a local outbox only after you pass that draft's confirm token. The From address is `counter@hearthlane.example`. The script does not open SMTP.

Chapter: [Chapter 17: The Work-Agent Blueprint](../../chapters/ch17-work-agent-blueprint/README.md)

## Goal

Separate a draft from a send. The draft may be written immediately, because it is a file. The send waits until the token matches that draft's id, recipient, subject, and body. You should be able to show `sent=0` and then `sent=1`, and to say who the sent record claims to act as.

This is the counter-staff agent from Chapter 17. It is allowed to confirm mail to a customer. The customer-facing concierge from Chapter 16 still never sends to `sam@example.com`. The self-check calls both.

## Assignment

Turn in:

1. The full trace of the default run, including the readable draft body, the `send_draft` decision, and the summary (`drafts=1`, `sent=0`).
2. The full trace of the run that passes that draft's token, including `confirmed_by=operator` and the summary (`sent=1`).
3. The output of `--self-check`, especially the line that says the concierge still denies the external send.
4. The answers in [What to write up](#what-to-write-up).

## Prerequisites

- The shared setup in [`../README.md`](../README.md), if you want the same virtualenv as the earlier labs. The required traces do not call a model server.
- Python 3.10 or newer
- Chapter 16's gate is the function this script calls (`labs/common/autonomy.py`). You do not need to turn Chapter 16 in first.

## Setup

Reuse the shared setup in [`../README.md`](../README.md). Focus on this exercise. No new services and no mailbox credentials.

Work from the repository root. Drafts go to `labs/ch17-work-agent-blueprint/var/drafts/`. Sent copies go to `var/sent/`. Both directories are local output. The policy text is read from `labs/ch02-your-first-loop/docs/policy.md`. The draft quotes sentences from that file. If those sentences are missing, the script will not write the draft.

## Steps

The tools:

- `read_file` on `policy.md` is auto, and it uses the same directory jail as Chapter 2.
- `draft_email` is auto. It writes one JSON file. `status` is `draft`.
- `send_draft` is confirm. The staff agent passes `allow_external_mail`, so Sam's address can be approved. It still does not send until the token matches. A token for a different body does not send.
- `from` is fixed to `counter@hearthlane.example`. The script does not take a From address from the draft arguments you might wish the model had set.
- `smtp=not_used` on every run. "Sent" means a file in the local outbox.

From the repo root:

1. Draft the return letter and stop before send.

   ```bash
   python labs/ch17-work-agent-blueprint/draft_mail.py
   ```

   You should see `PATH: docs/policy.md`, a draft id, the body between `|` lines, `sent=0`, and a `--confirm` hint. Copy that token.

2. Send that exact draft.

   ```bash
   python labs/ch17-work-agent-blueprint/draft_mail.py --confirm TOKEN
   ```

   Replace `TOKEN` with the token from step 1. The summary should report `sent=1`. The sent record includes `acted_as=counter-staff` and `confirmed_by=operator`.

3. Run the no-model checks.

   ```bash
   python labs/ch17-work-agent-blueprint/draft_mail.py --self-check
   ```

   The check that mutates the body must leave `sent=0`. The check that calls `decide` without the staff flag must deny the external address.

## What to write up

Answer in a few sentences each:

- What `read_file` returned, and which policy sentences the draft quotes. Open `docs/policy.md` and point at the lines.
- What existed on disk after step 1, and what appeared only after step 2. Name the From address and the `confirmed_by` value.
- Why this script may confirm mail to `sam@example.com`, and why Chapter 16's concierge may not. Use the self-check line as evidence.
- Who is allowed to act as the café in the sent file, and who is not (the customer, the agent process, the outbox tool).
- A `draft_calendar` tool for a Tuesday bike delivery. Say what would be auto, what would require confirm, and which fields the token would need to cover. You do not have to implement it.

## Troubleshooting

- `sent=1` on the first run: `--confirm` was set. Run again without it.
- The confirm run still says `not sent`: the token was not the one printed for this body. Copy the token from the latest unconfirmed trace.
- `ERROR: draft quotes are not in docs/policy.md`: the draft text and the policy file have diverged. The script refuses to send a return rule the file does not contain.
- A connection error or an API key prompt: this exercise does not call the model client. Check that you ran `draft_mail.py`, not a Chapter 2 or 3 script.
- `ModuleNotFoundError` for `labs`: run from the repository root.
