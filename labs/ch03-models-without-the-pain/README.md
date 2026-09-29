# Lab — Chapter 3. Swap the model, keep the loop

The Chapter 2 agent, run from this directory, against the Chapter 2 docs. You change providers by editing the repo-root `.env` only. `swap_model.py` stays untouched between runs.

Chapter: [Chapter 3: Local and Hosted Models](../../chapters/ch03-models-without-the-pain/README.md)

## Goal

Run the same question twice. Once on an Ollama-shaped config. Once on Groq or OpenRouter. Compare tool logs, stop tags, and citations. Attribute the difference to the model, because the harness did not move.

## Prerequisites

- Python 3.10 or newer
- **Ollama** for the local run, and an API key for **Groq** or **OpenRouter** for the hosted run
- A model that can emit OpenAI-style `tool_calls` on each side you compare

You can complete a single run with only one provider. The comparison the chapter describes needs both.

## Environment

Work from the repository root. This script imports `run_file_agent` from `labs/common/loop.py` and reads:

```text
labs/ch02-your-first-loop/docs/
```

It does not keep a second copy of the policy or the FAQ.

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

`requirements.txt` installs `openai`, `python-dotenv`, and `httpx`. If you already installed them for Chapter 1 or 2, reuse that virtualenv.

## `.env`

```bash
cp .env.example .env
```

`.env` is gitignored. Do not commit a real hosted key. Edit `.env` at the repo root. Leave `swap_model.py`, `labs/common/`, and the docs alone. Comment out the provider you are not using so a single `BASE_URL` and a single `MODEL` are set. A restart is not required; the next process reads `.env` again.

Process environment variables win over `.env`. Two active `MODEL=` lines are easy to misread: the last assignment wins.

**Ollama** (local). Pull the tag first. The server has to be running.

```bash
ollama pull llama3.2
ollama serve
```

```env
BASE_URL=http://localhost:11434/v1
API_KEY=ollama
MODEL=llama3.2
```

If this model answers with an empty tool log, pull a model that calls tools and change only `MODEL`:

```bash
ollama pull llama3.1
```

```env
MODEL=llama3.1
```

Say so in your notes if you switched.

**Groq** (hosted). Create a key in the Groq console. Use a model with **local** tool-call support. `groq/compound` runs tools on Groq's servers and will not call this lab's `read_file`.

```env
BASE_URL=https://api.groq.com/openai/v1
API_KEY=gsk_your_key_here
MODEL=llama-3.3-70b-versatile
```

Smaller Groq option, same URL and key: `MODEL=llama-3.1-8b-instant`. If the API says the model id is gone, pick a current local-tool-use id from Groq's docs.

**OpenRouter** (hosted). Model ids are `vendor/name`. On the model page, confirm tool support before you run.

```env
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-your_key_here
MODEL=meta-llama/llama-3.3-70b-instruct
```

The same blocks are commented in `.env.example`. The script prints them again after each run.

A hosted request includes the prompt and the text of any file the agent read. `read_file` itself still executes on your machine. The shop docs are fictional.

## Run

From the repo root, with the virtualenv active. Do this twice, once per provider, without editing `swap_model.py`:

```bash
python labs/ch03-models-without-the-pain/swap_model.py
```

Default question: "How much is local delivery, and which day are you closed?"

Answer key:

- Delivery fee $4.50, free at $35 and above, Tuesday–Friday, within 3 miles of 12 Hearth Lane — `docs/policy.md`
- Closed Monday — `docs/faq.md`

Optional: pass another question as arguments. Keep that question identical across the two provider runs.

## What stays fixed

Printed at startup, and it should match across your two runs:

- `TEMPERATURE` and `MAX_TOKENS` from `labs/common/client.py` (`0.2` and `800`)
- `MAX_STEPS` from `labs/common/loop.py` (`6`)
- `DOCS` pointing at the Chapter 2 `docs/` directory

The script also prints `BASE_URL` and `MODEL` for the run, and `API_KEY=set` or `missing` without the secret.

If `TEMPERATURE` or `MAX_TOKENS` differ between your two runs, you edited the harness, and the comparison is no longer the one this chapter asks for.

## What to observe

Keep both traces. For each, record:

- provider, `BASE_URL`, and `MODEL`
- whether `policy.md` and `faq.md` were both read
- the stop tag and the step count
- whether $4.50 and Monday are cited to the right file
- any offer to book, refund, or email — the tool list cannot do those

A run that skips tools is a model result. The harness does not send `tool_choice` (Ollama's compatible API does not support that field), so it cannot force the read. Leave `swap_model.py` unchanged. Change `.env` and run again.

## Troubleshooting

- Connection refused on localhost: Ollama is not serving, or `BASE_URL` still has a trailing path the server does not use. The default is `http://localhost:11434/v1`. `ollama pull` and `ollama serve` are setup; a connection error is not a defect in `swap_model.py`.
- HTTP 401: the hosted key is wrong or still set to `ollama`.
- HTTP 400 mentioning `messages[].name`: Groq rejects that field. The shared client does not send it. If you added it locally, remove it.
- HTTP 404 on the model: the id is stale or not enabled on your account. Change `MODEL` only.
- Empty tool log on a model that should call tools: run once more and keep both outputs. If it is stable, note it. That is a Chapter 3 result, not a broken script.
- A run that browses or searches instead of opening `policy.md`: the model runs tools on the provider's side. Switch to a model marked for local tool use.
- `max_tokens`, or truncated tool-call JSON: leave the provider in place and look at `MAX_TOKENS` in `labs/common/client.py`. Changing vendor and the token limit in one edit muddies the comparison.
