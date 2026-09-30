# Labs

Exercises for the Local Shop Concierge. Chapters 1–3 and 16–18 are scripts you can run. The other chapter folders are stubs.

Do this setup once from the repo root. Then open the lab you are on and follow that README.

## Labs

| Lab | Script |
|---|---|
| [Chapter 1. Hello Concierge](ch01-what-an-agent-is/README.md) | `labs/ch01-what-an-agent-is/hello_concierge.py` |
| [Chapter 2. Your first loop](ch02-your-first-loop/README.md) | `labs/ch02-your-first-loop/file_agent.py` |
| [Chapter 3. Swap the model](ch03-models-without-the-pain/README.md) | `labs/ch03-models-without-the-pain/swap_model.py` |
| [Chapter 16. Autonomy policy](ch16-autonomy-policy/README.md) | `labs/ch16-autonomy-policy/policy_gate.py` |
| [Chapter 17. Work-agent blueprint](ch17-work-agent-blueprint/README.md) | `labs/ch17-work-agent-blueprint/draft_mail.py` |
| [Chapter 18. Agentic commerce](ch18-agentic-commerce/README.md) | `labs/ch18-agentic-commerce/checkout.py` |

Each of Labs 1–3 has a `SOLUTION.md` in its folder. Those notes are for instructors and for checking your own write-up after you have finished it. If the lab is homework, finish the write-up before you open that file.

Chapters 16–18 do not have solution files. Their required traces run without a model server. `--self-check` on those three scripts does not contact Ollama or a hosted API.

## Requirements

- Python 3.10 or newer
- Either **Ollama** on your machine, or an API key for **Groq** or **OpenRouter**

Chapters 1–3 share one OpenAI-compatible client. Ollama is the default. Groq and OpenRouter are the same three variables in `.env`.

Chapter 1 is a single chat completion. Tool calling is not required. Chapters 2 and 3 need a model that can emit tool calls. If a Chapter 2 or 3 trace never shows a tool call, use the `llama3.1` fallback under Ollama below.

## Install

From the repo root:

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

`requirements.txt` installs `openai`, `python-dotenv`, and `httpx`.

## Configure `.env`

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

`.env` is gitignored. `.env.example` is the committed template. Do not commit a real hosted key.

| Variable | Meaning | Ollama default |
|---|---|---|
| `BASE_URL` | OpenAI-compatible API origin | `http://localhost:11434/v1` |
| `API_KEY` | Bearer token. Ollama ignores the value and still wants a non-empty string. | `ollama` |
| `MODEL` | Model name that server expects | `llama3.2` |

Process environment variables win over `.env`. Commented Groq and OpenRouter blocks are in `.env.example`. Use one provider at a time. Two active `MODEL=` lines are easy to misread: the last assignment wins. An empty `API_KEY` exits before the request. For Ollama use the literal value `ollama`.

### Ollama

Install from [ollama.com/download](https://ollama.com/download), pull the default tag, and start the server if it is not already running:

```bash
ollama pull llama3.2
ollama serve
```

Default `.env`:

```env
BASE_URL=http://localhost:11434/v1
API_KEY=ollama
MODEL=llama3.2
```

Chapters 2 and 3 need a model that emits `tool_calls`. The default `llama3.2` often can, and sometimes will not. If the trace never shows a `read_file` call, pull a tool-capable fallback and change only `MODEL`:

```bash
ollama pull llama3.1
```

```env
MODEL=llama3.1
```

### Groq or OpenRouter

Comment out the Ollama lines in `.env` and set one hosted provider. These placeholders are not real keys:

```env
# Groq — use a model with local tool-call support, not groq/compound
BASE_URL=https://api.groq.com/openai/v1
API_KEY=gsk_your_key_here
MODEL=llama-3.3-70b-versatile
```

```env
# OpenRouter — confirm the id on the model page and that it lists tools
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-your_key_here
MODEL=meta-llama/llama-3.3-70b-instruct
```

`groq/compound` runs tools on Groq's servers and will not call this lab's `read_file`. A smaller Groq option, same URL and key, is `MODEL=llama-3.1-8b-instant`. If the API says a model id is gone, pick a current local-tool-use id from that provider's docs.

A hosted request includes the prompt and, for Chapters 2 and 3, the text of any file the agent read. The shop docs are fictional. Do not send a private document to a third-party API unless you mean to.

## Run each script

From the repo root, with the virtualenv active:

```bash
python labs/ch01-what-an-agent-is/hello_concierge.py
python labs/ch02-your-first-loop/file_agent.py
python labs/ch03-models-without-the-pain/swap_model.py
```

Each script prints `BASE_URL` and `MODEL` and hides the key. Optional questions are extra arguments. Chapter 3 is the Chapter 2 loop. Switching providers is an edit to `.env`, then the same command. Shop files are `labs/ch02-your-first-loop/docs/policy.md` and `docs/faq.md`.

## Check the harness without a model

```bash
python -m unittest labs.common.test_harness
```

That covers the docs path jail, tool-error handling, max steps, and the repeated-call stop. It does not contact Ollama or a hosted API.

## Troubleshooting

A connection error means `.env` or the server, not the café prompt. The key is not printed. A header line `API_KEY=set (value hidden)` means a non-empty value was loaded. `API_KEY=missing (value hidden)` means it was not.

- **Connection refused, or any connection error.** Check `BASE_URL`. The Ollama default is `http://localhost:11434/v1`, with nothing after `/v1`. Confirm `ollama serve` is running and `ollama pull` has finished, or that your hosted key is set. `MODEL` must be a tag you have pulled or a hosted id that exists.
- **Empty `API_KEY`.** The process exits before the request. For Ollama set `API_KEY=ollama`.
- **`BASE_URL` is empty.** Copy `.env.example` to `.env`.
- **HTTP 401.** The hosted key is wrong or still set to `ollama`.
- **HTTP 404 on the model.** The id is stale or not enabled on your account. Change `MODEL` only.
- **Empty tool log on Chapter 2 or 3, with `final` after 1 model call.** The server answered and the model never called the tool. Change `MODEL` (the `llama3.1` fallback above, or a hosted id that calls tools locally), not the question.
