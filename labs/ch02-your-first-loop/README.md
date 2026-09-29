# Lab — Chapter 2. Your first loop

A tool-calling loop with one tool, `read_file`, jailed to this directory's `docs/`. The agent answers return and shipping questions from `policy.md` and `faq.md` and is instructed to cite the path.

Chapter: `chapters/ch02-your-first-loop/README.md`

## Goal

Run `file_agent.py`. Confirm the trace shows a read of `policy.md` (and `faq.md` when the question needs it), and that the answer's shop facts match those files and name them, for example `(docs/policy.md)`.

## Setup

Install and `.env` are in the top-level README under **Running the labs**. This lab needs a model that can emit OpenAI-style `tool_calls`. The default `llama3.2` often can, and sometimes will not. If the trace is empty, switch `MODEL` to `llama3.1` (after `ollama pull llama3.1`) or to a Groq / OpenRouter tool-capable id. Chapter 3 is the full provider switch. You can borrow those `.env` lines early if you want a cleaner trace while you learn the loop.

From the repo root:

```bash
python labs/ch02-your-first-loop/file_agent.py
```

Other questions:

```bash
python labs/ch02-your-first-loop/file_agent.py "How much is local delivery, and which day are you closed?"
python labs/ch02-your-first-loop/file_agent.py "What's the Wi-Fi password?"
python labs/ch02-your-first-loop/file_agent.py "Do you sell live crabs?"
```

## Documents

| File | Holds |
|---|---|
| `docs/policy.md` | Returns, shipping, transit damage, local delivery fee and window |
| `docs/faq.md` | Address, hours, menu prices, allergens, Wi-Fi network name |

The Wi-Fi password is intentionally absent. Delivery fees are intentionally not copied into the FAQ. A correct delivery answer has to read `policy.md`. A correct "closed Monday" answer has to read `faq.md`.

## What the harness does

- `labs/common/loop.py` — up to `DEFAULT_MAX_STEPS` (6) model calls. Stops on a final message with no tool call, on a third identical tool call, or when `max_tokens` cuts off a text reply.
- `labs/common/tools.py` — `read_file` only. Paths must stay inside `docs/`. `..`, absolute paths, hidden names, and symlinks that resolve outside the directory return an `ERROR:` string. The process keeps going.
- The system prompt tells the model to cite `docs/policy.md` or `docs/faq.md` and to abstain when the files do not say.

The script prints each tool result, then the answer, then a stop line:

```text
--- stop: final after 2 model call(s) ---
```

A `NOTE:` after that line means the soft checks saw an empty tool log, a missing `docs/` citation, or a harness stop. Notes do not rewrite the answer.

## What to observe

On the default question, a grounded answer says opened coffee is final sale and a cardamom bun cannot be shipped, with `docs/policy.md` on both claims. Unopened coffee would be 14 days, receipt required, Hearth card credit, no cash — the model should not apply that rule to an opened bag.

On the Wi-Fi question, a grounded answer gives the network name `hearth-guest` from `docs/faq.md` and does not invent a password.

On "live crabs," the files have nothing. The model should say it does not know. A made-up menu item is a miss.

Score citations by opening the file, not by the presence of the substring `docs/`. The soft note only checks the substring.

## No-model checks

Path jail, from the repo root:

```bash
python -c "from labs.common.tools import read_file; from pathlib import Path; print(read_file(Path('labs/ch02-your-first-loop/docs'), '../.env'))"
```

Expect an `ERROR:` line.

Stop conditions and the jail, without a server:

```bash
python -m unittest labs.common.test_harness
```

## Failure

- Connection error: server down, bad `BASE_URL`, or bad key. Same checks as Chapter 1.
- `final` after 1 model call and an empty trace: the model never called the tool. Change `MODEL`, not the question, and run again.
- `ERROR:` in the trace for a normal question: read the error. A bad path is the model; a missing `docs/` directory is the checkout.
- `max_steps` or `repeated_call`: the harness stopped on purpose and did not invent a closing paragraph. The trace is the result.
