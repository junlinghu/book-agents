# Lab — Chapter 3. Swap the model, keep the loop

The Chapter 2 agent, run from this directory, against the Chapter 2 docs. You change providers by editing the repo-root `.env` only.

Chapter: [Chapter 3: Local and Hosted Models](../../chapters/ch03-models-without-the-pain/README.md)

## Goal

Run the same question twice. Once on an Ollama-shaped config. Once on Groq or OpenRouter. Leave `swap_model.py` untouched between the runs. Compare tool logs, stop tags, and citations.

Differences you can attribute to the model are the point. The harness and the shop files stay put. You can smoke-test the script with one provider. The comparison this lab asks you to turn in needs both.

## Assignment

Turn in:

1. Two complete runs of the default question: one Ollama, one Groq or OpenRouter. For each, include the startup header, the tool log, the answer, the stop line, and any `NOTE:` lines.
2. A comparison: provider, `BASE_URL`, `MODEL`, which files were read, stop tag, step count, and which claims cite which file.
3. A note if either run skipped tools, browsed or searched instead of calling `read_file`, or offered to book, refund, or email. Leave `swap_model.py` unchanged. Do not add `tool_choice`.
4. The fixed harness values from both headers, showing they matched. If you switched `MODEL` within a provider (for example to `llama3.1`), say so.

## Prerequisites

- Python 3.10 or newer
- Chapter 2's virtualenv, `requirements.txt`, and repo-root `.env`
- Ollama on your machine, plus a Groq or OpenRouter key
- On each provider, a model that can emit tool calls (see Setup)

## Setup

Work from the repository root. This script imports `run_file_agent` from `labs/common/loop.py` and reads:

```text
labs/ch02-your-first-loop/docs/
```

It does not keep a second copy of the policy or the FAQ. The corpus is:

| File | Holds |
|---|---|
| `labs/ch02-your-first-loop/docs/policy.md` | Returns, shipping, transit damage, local delivery fee and window |
| `labs/ch02-your-first-loop/docs/faq.md` | Address, hours, menu prices, allergens, Wi-Fi network name |

Printed at startup, and these should match across your two runs:

- `TEMPERATURE` `0.2` and `MAX_TOKENS` `800`, from `labs/common/client.py`
- `MAX_STEPS` `6`, from `labs/common/loop.py`
- `DOCS` pointing at the Chapter 2 `docs/` directory

The script also prints `BASE_URL`, `MODEL`, and `API_KEY=set (value hidden)` or `API_KEY=missing (value hidden)`. The key itself is not printed.

If `TEMPERATURE` or `MAX_TOKENS` differ between your two runs, you edited the harness, and the comparison is no longer the one this chapter asks for.

`read_file` executes on your machine. On a hosted run, the file text is then sent to that provider as the tool result on the next request. The shop docs are fictional.

Install steps are also in the top-level README under **Running the labs**.

1. From the repo root, if you do not already have the lab environment. If you already installed dependencies for Chapter 1 or 2, reuse that virtualenv.

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   cp .env.example .env
   ```

   Windows PowerShell:

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   Copy-Item .env.example .env
   ```

   `requirements.txt` installs `openai`, `python-dotenv`, and `httpx`. Do not commit `.env`.

2. Edit `.env` at the repo root. Leave `swap_model.py`, `labs/common/`, and the docs alone. Comment out the provider you are not using so a single `BASE_URL` and a single `MODEL` are set. A restart is not required. The next process reads `.env` again.

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

   If this model answers with an empty tool log, pull a model that calls tools and change only `MODEL`. Say so in your notes if you switched.

   ```bash
   ollama pull llama3.1
   ```

   ```env
   MODEL=llama3.1
   ```

   **Groq** (hosted). Create a key in the Groq console. Use a model with local tool-call support. `groq/compound` runs tools on Groq's servers and will not call this lab's `read_file`. Smaller option, same URL and key: `MODEL=llama-3.1-8b-instant`. If the API says the model id is gone, pick a current local-tool-use id from Groq's docs. Do not commit the key.

   ```env
   BASE_URL=https://api.groq.com/openai/v1
   API_KEY=gsk_your_key_here
   MODEL=llama-3.3-70b-versatile
   ```

   **OpenRouter** (hosted). Model ids are `vendor/name`. On the model page, confirm tool support before you run.

   ```env
   BASE_URL=https://openrouter.ai/api/v1
   API_KEY=sk-or-your_key_here
   MODEL=meta-llama/llama-3.3-70b-instruct
   ```

   The same blocks are commented in `.env.example`. The script prints them again after each run.

## Steps

From the repo root, with the virtualenv active. Do not edit `swap_model.py` between runs.

1. Set `.env` to the Ollama block. Run the default question.

   ```bash
   python labs/ch03-models-without-the-pain/swap_model.py
   ```

   Default question: "How much is local delivery, and which day are you closed?"

2. Comment out the Ollama lines. Set Groq or OpenRouter. Run the same command again.

3. Optional. Pass another question, and run that same question on both providers. Keep the question text identical across the two runs.

   ```bash
   python labs/ch03-models-without-the-pain/swap_model.py "What's the Wi-Fi password?"
   ```

The harness does not send `tool_choice`. Ollama's compatible API does not support that field, so the loop cannot force the read. A run that skips tools is a result from that model. Change `.env` and run again. Leave the script alone.

## What to write up

Keep both traces. For each, record:

- Provider, `BASE_URL`, and `MODEL`
- `TEMPERATURE`, `MAX_TOKENS`, `MAX_STEPS`, and the `DOCS` path
- Whether `policy.md` was read, and whether `faq.md` was read (quote the tool-log lines)
- The stop tag and the step count
- Every `NOTE:` line
- Each shop fact the answer states, and the file path it cites, or that it cites none
- Any offer to book, refund, or email. The tool list cannot do those

Then write a short comparison: what changed between the two providers, and which header values stayed the same.

## Troubleshooting

- Connection refused on localhost: Ollama is not serving, or `BASE_URL` still has a trailing path the server does not use. The default is `http://localhost:11434/v1`. `ollama pull` and `ollama serve` are setup. A connection error is not a defect in `swap_model.py`.
- HTTP 401: the hosted key is wrong or still set to `ollama`.
- HTTP 400 mentioning `messages[].name`: Groq rejects that field. The shared client does not send it. If you added it locally, remove it.
- HTTP 404 on the model: the id is stale or not enabled on your account. Change `MODEL` only.
- Empty tool log on a model that should call tools: run once more and keep both outputs. If it is stable, note it. That is a Chapter 3 result, not a broken script.
- A run that browses or searches instead of opening `policy.md` or `faq.md`: the model is running tools on the provider's side. Switch to a model marked for local tool use.
- `max_tokens`, or truncated tool-call JSON: leave the provider in place and look at `MAX_TOKENS` in `labs/common/client.py` (800). Changing the vendor and the token limit in one edit muddies the comparison. Record it if you change the limit.

Instructor notes are in `SOLUTION.md` in this folder. If this lab is homework, finish the write-up before you open that file.
