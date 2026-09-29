# Lab — Chapter 2. Your first loop

A tool-calling loop with one tool, `read_file`, jailed to this directory's `docs/`. The agent answers return and shipping questions from `policy.md` and `faq.md` and is instructed to cite the path.

Chapter: [Chapter 2: The Agent Loop](../../chapters/ch02-your-first-loop/README.md)

## Goal

Run `file_agent.py`. Confirm the trace shows a read of `policy.md` (and `faq.md` when the question needs it), and that the answer's shop facts match those files and name them, for example `(docs/policy.md)`.

## Prerequisites

- Python 3.10 or newer
- Either **Ollama** on your machine, or an API key for **Groq** or **OpenRouter**
- A model that can emit OpenAI-style `tool_calls`

The default `llama3.2` often can, and sometimes will not. If the trace is empty, switch `MODEL` to `llama3.1` (after `ollama pull llama3.1`) or to a Groq / OpenRouter tool-capable id. Chapter 3 is the full provider switch. You can borrow those `.env` lines early if you want a cleaner trace while you learn the loop.

## Environment

Work from the repository root. The script uses the shared harness in `labs/common/loop.py` and `labs/common/tools.py`, and reads only `labs/ch02-your-first-loop/docs/`.

Shared setup is also in the top-level README under **Running the labs**. The commands below match that section.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

`requirements.txt` installs `openai`, `python-dotenv`, and `httpx`. If you already installed them for Chapter 1, reuse that virtualenv.

## `.env`

```bash
cp .env.example .env
```

`.env` is gitignored. Do not commit a real hosted key.

| Variable | Meaning | Ollama default |
|---|---|---|
| `BASE_URL` | OpenAI-compatible API origin | `http://localhost:11434/v1` |
| `API_KEY` | Bearer token. Ollama ignores the value and still wants a non-empty string. | `ollama` |
| `MODEL` | Model name that server expects | `llama3.2` |

Ollama:

```bash
ollama pull llama3.2
ollama serve
```

```env
BASE_URL=http://localhost:11434/v1
API_KEY=ollama
MODEL=llama3.2
```

If the tool log stays empty, pull a tool-capable fallback and change only `MODEL`:

```bash
ollama pull llama3.1
```

```env
MODEL=llama3.1
```

Hosted placeholders (not real keys). Comment out the Ollama lines so only one `BASE_URL` and one `MODEL` are active. Use a model with local tool-call support. `groq/compound` runs tools on Groq's servers and will not call this lab's `read_file`.

```env
# Groq
BASE_URL=https://api.groq.com/openai/v1
API_KEY=gsk_your_key_here
MODEL=llama-3.3-70b-versatile
```

```env
# OpenRouter — confirm the id lists tools
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-your_key_here
MODEL=meta-llama/llama-3.3-70b-instruct
```

A hosted request includes the prompt and the text of any file the agent read. The shop docs are fictional.

## Run

From the repo root, with the virtualenv active:

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

On the delivery question, a grounded answer cites `docs/policy.md` for $4.50 (free at $35, Tuesday–Friday, within 3 miles) and `docs/faq.md` for closed Monday.

On the Wi-Fi question, a grounded answer gives the network name `hearth-guest` from `docs/faq.md` and does not invent a password.

On "live crabs," the files have nothing. The model should say it does not know. A made-up menu item is a miss.

Score citations by opening the file, not by the presence of the substring `docs/`. The soft note only checks the substring.

Record from one real run:

- The trace lines: which `path` was requested, and whether the first line of the result was `PATH:` or `ERROR:`.
- The stop tag (`final`, `max_steps`, `repeated_call`, `max_tokens`) and the step count.
- Whether each shop fact in the answer appears in the cited file. Quote the file line next to the model line.
- If the trace is empty, write that down. The harness does not send `tool_choice`, so it cannot force a tool call.

## Checks without a model

Path jail, from the repo root:

```bash
python -c "from labs.common.tools import read_file; from pathlib import Path; print(read_file(Path('labs/ch02-your-first-loop/docs'), '../.env'))"
```

Expect an `ERROR:` line, and no contents of an env file.

Stop conditions and the jail, without a server:

```bash
python -m unittest labs.common.test_harness
```

That covers the docs path jail, tool-error handling, max steps, and the repeated-call stop. It does not contact Ollama or a hosted API.

## Troubleshooting

- Connection error: server down, bad `BASE_URL`, or bad key. Same checks as Chapter 1. Ollama default is `http://localhost:11434/v1`.
- `final` after 1 model call and an empty trace: the model never called the tool. Change `MODEL`, not the question, and run again.
- `ERROR:` in the trace for a normal question: read the error. A bad path is the model; a missing `docs/` directory is the checkout.
- `max_steps` or `repeated_call`: the harness stopped on purpose and did not invent a closing paragraph. The trace is the result.
- `max_tokens`, or a tool result that says the arguments were not valid JSON and the trace looks cut off: `MAX_TOKENS` in `labs/common/client.py` is 800. Raising it is a harness edit. Record that you changed it.
