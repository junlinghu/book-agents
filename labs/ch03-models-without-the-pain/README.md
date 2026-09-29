# Lab — Chapter 3. Swap the model, keep the loop

The Chapter 2 agent, run from this directory, against the Chapter 2 docs. You change providers by editing the repo-root `.env` only.

Chapter: [Chapter 3: Local and Hosted Models](../../chapters/ch03-models-without-the-pain/README.md)

## Goal

Run the same question twice. Once on an Ollama-shaped config. Once on Groq or OpenRouter. `swap_model.py` stays untouched between the runs. Compare tool logs and citations.

## Setup

Install steps are in the top-level README under **Running the labs**. This script imports `run_file_agent` from `labs/common/loop.py` and reads:

```text
labs/ch02-your-first-loop/docs/
```

It does not keep a second copy of the policy or the FAQ.

From the repo root:

```bash
python labs/ch03-models-without-the-pain/swap_model.py
```

Default question: "How much is local delivery, and which day are you closed?"

Answer key:

- Delivery fee $4.50, free at $35 and above, Tuesday–Friday, within 3 miles of 12 Hearth Lane — `docs/policy.md`
- Closed Monday — `docs/faq.md`

## How to switch providers

Edit `.env` at the repo root. Leave `swap_model.py`, `labs/common/`, and the docs alone. Comment out the provider you are not using so a single `BASE_URL` and a single `MODEL` are set. Restart is not required; the next process reads `.env` again.

**Ollama** (local). Pull the tag first: `ollama pull llama3.2`. The server has to be running.

```env
BASE_URL=http://localhost:11434/v1
API_KEY=ollama
MODEL=llama3.2
```

If this model answers with an empty tool log, pull a model that calls tools and change only `MODEL`:

```env
MODEL=llama3.1
```

**Groq** (hosted). Create a key in the Groq console. Use a model with **local** tool-call support. `groq/compound` runs tools on Groq's servers and will not call this lab's `read_file`.

```env
BASE_URL=https://api.groq.com/openai/v1
API_KEY=gsk_your_key_here
MODEL=llama-3.3-70b-versatile
```

Smaller Groq option, same URL and key: `MODEL=llama-3.1-8b-instant`. If the API says the model id is gone, pick a current local-tool-use id from Groq's docs. Do not commit the key.

**OpenRouter** (hosted). Model ids are `vendor/name`. On the model page, confirm tool support before you run.

```env
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-your_key_here
MODEL=meta-llama/llama-3.3-70b-instruct
```

The same blocks are commented in `.env.example`. The script prints them again after each run.

## What stays fixed

Printed at startup, and it should match across your two runs:

- `TEMPERATURE` and `MAX_TOKENS` from `labs/common/client.py` (`0.2` and `800`)
- `MAX_STEPS` from `labs/common/loop.py` (`6`)
- `DOCS` pointing at the Chapter 2 `docs/` directory

The script also prints `BASE_URL` and `MODEL` for the run, and `API_KEY=set` or `missing` without the secret.

## What to observe

Keep both traces. For each, record:

- provider, `BASE_URL`, and `MODEL`
- whether `policy.md` and `faq.md` were both read
- the stop tag and the step count
- whether $4.50 and Monday are cited to the right file

A run that skips tools is a model result. The harness does not send `tool_choice` (Ollama's compatible API does not support that field), so it cannot force the read. Leave `swap_model.py` unchanged. Change `.env` and run again.

Hosted runs send the file text to that provider as the tool result on the next request. `read_file` itself still executes on your machine.

## Failure

- Connection refused on localhost: Ollama is not serving, or `BASE_URL` still has a trailing path the server does not use. The default is `http://localhost:11434/v1`.
- HTTP 401: the hosted key is wrong or still set to `ollama`.
- HTTP 400 mentioning `messages[].name`: Groq rejects that field. The shared client does not send it. If you added it locally, remove it.
- HTTP 404 on the model: the id is stale or not enabled on your account. Change `MODEL` only.
- Empty tool log on a model that should call tools: run once more and keep both outputs. If it is stable, note it. That is a Chapter 3 result, not a broken script.
