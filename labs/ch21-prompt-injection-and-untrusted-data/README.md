# Lab — Chapter 21. Prompt injection and untrusted data

A competitor page tells the concierge to ignore the café price, read `.env`, and email secrets to `sam@example.com`. The harness has to treat that page as untrusted data. The starter still returns the canary file and still marks the send as allowed.

Chapter: [Chapter 21: Prompt Injection and Untrusted Data](../../chapters/ch21-prompt-injection-and-untrusted-data/README.md)

## Goal

Show that untrusted page text cannot grant a tool, change the bun price, or pull a secret into the trace. After your edit, the scripted trace quotes Mill & Birch as untrusted, reports the café bun at 475 cents from `docs/faq.md`, refuses `.env` and `fixtures/canary.env`, and denies mail to `sam@example.com`. Neither canary value appears anywhere in the trace.

The proposals stand in for tool calls a model might make after reading the page. This lab does not need a model server. There is no `SOLUTION.md`.

## Assignment

Turn in:

1. Your `harness.py`.
2. The full trace of `python labs/ch21-prompt-injection-and-untrusted-data/harness.py` after the TODOs are done.
3. The output of `python labs/ch21-prompt-injection-and-untrusted-data/test_harness.py`. The starter fails these tests. A finished harness passes them.
4. The answers in [What to write up](#what-to-write-up).

## Prerequisites

- The shared setup in [`../README.md`](../README.md) is enough if you want the same virtualenv as the earlier labs. The required trace and tests do not call the OpenAI API.
- Python 3.10 or newer

## Setup

Reuse the shared setup in [`../README.md`](../README.md). You do not need a new virtualenv and you do not need a model for this exercise.

Work from the repository root. The poisoned page is `fixtures/mill-and-birch.html`. The fake secrets are `fixtures/canary.env`. Do not point this lab at a real `.env`. The canary file is the stand-in, on purpose, so a leak is obvious and not a live key.

| File | Role |
|---|---|
| `fixtures/mill-and-birch.html` | Competitor page. The visible price is $3.25. A comment demands `.env` and an email. |
| `fixtures/canary.env` | Fake `OPENAI_API_KEY` and `STAFF_INBOX_SECRET`. A trace that contains either value has leaked. |
| `harness.py` | Fill in the TODOs. |
| `test_harness.py` | The spec. It fails until the TODOs are done. |

Shop documents stay `labs/ch02-your-first-loop/docs/faq.md` and `policy.md`. A cardamom bun is $4.75.

## Steps

The boundary this lab is grading:

- `label_untrusted` starts with `UNTRUSTED PAGE TEXT`, then a line that sentences in the page cannot grant tools, change the bun price, or request secrets, then the page text. The constants `UNTRUSTED_MARK` and `UNTRUSTED_RULE` are that wording.
- `read_requested_path` may return `policy.md` and `faq.md` through `read_file` in `labs/common/tools.py`. Every other path returns a string that starts with `ERROR:` and does not include the canary values. That includes `.env`, `fixtures/canary.env`, `..`, and absolute paths.
- `handle_send` returns `decide("send_email", arguments)` from `labs/common/autonomy.py`. Leave external mail off. `sam@example.com` is denied. Do not add a branch that sends.
- `shop_bun_cents` is already 475 from the FAQ. Do not replace it with $0 or $3.25 from the page.
- `build_trace` pastes the two read results into the email body on purpose. If a read leaks, the trace leaks even when the send is later denied. Fix the reads. Do not special-case the printer to hide a leak.

From the repo root:

1. Run the starter and look for the canary strings.

   ```bash
   python labs/ch21-prompt-injection-and-untrusted-data/harness.py
   ```

   You should see the page with no untrusted label, `shop_bun_cents=475`, the canary file contents under the `.env` and `canary.env` reads, and `decision=allowed` on the send.

2. Fill in the three TODOs in `harness.py`.

3. Run the trace again. The canary values should be gone. Both reads should start with `ERROR:`. The send should be `decision=denied`. The page should still be visible under `UNTRUSTED PAGE TEXT`.

4. Run the spec.

   ```bash
   python labs/ch21-prompt-injection-and-untrusted-data/test_harness.py
   ```

   It should finish with `OK`. It does not contact a model server.

## What to write up

Answer in a few sentences each:

- Where the Mill & Birch instructions sit in the HTML, and which customer question they were not. Quote the comment.
- Which of Chapter 16's three trifecta legs this concierge still has after your edit, and which leg the denied send removes.
- Why a denied send can still leak. Use the starter trace, where the body is printed, as the example.
- Why `faq.md` stays readable when `.env` does not. Name the function that implements the jail.
- One new tool you would refuse to register on the concierge that just fetched this page, and which column of the trifecta it would complete.

## Troubleshooting

- The tests pass the label and still fail the canary check: a read result or the email body still contains the fixture. Search the trace for `sk-hearth-lab-canary`.
- `policy.md` started returning `ERROR:`: the allowed names are `policy.md`, `docs/policy.md`, `faq.md`, and `docs/faq.md`. Use `read_file` on the docs directory.
- `handle_send` returns `confirm_required`: external mail was turned on, or the address was rewritten to `@hearthlane.example`. This concierge leaves `allow_external_mail` false. Sam's address stays never.
- `decision=allowed` is still in the trace: the starter return value is still in `handle_send`, or `build_trace` was changed to print a different send.
- `ModuleNotFoundError` for `labs`: run the commands from the repository root, not from inside the lab folder.
