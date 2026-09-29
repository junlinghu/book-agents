# book-agents

Introduction to AI Agents. The running example is a desktop **Local Shop Concierge** for a fictional café, Hearth Lane Café. You build a small harness around an OpenAI-compatible model. The same code talks to local Ollama or to a hosted Groq or OpenRouter endpoint. The switch is `.env`.

Chapters 1–3 (Part I — Foundations) are in `chapters/`. Their labs are in `labs/`.

| Chapter | Text | Lab |
|---|---|---|
| 1. What an agent is | `chapters/ch01-what-an-agent-is/` | `labs/ch01-what-an-agent-is/` |
| 2. Your first loop | `chapters/ch02-your-first-loop/` | `labs/ch02-your-first-loop/` |
| 3. Models without the pain | `chapters/ch03-models-without-the-pain/` | `labs/ch03-models-without-the-pain/` |

The shop documents the agent reads live in `labs/ch02-your-first-loop/docs/` (`policy.md`, `faq.md`). Later chapters are not in this tree yet.

## Running the labs

### Requirements

- Python 3.10 or newer
- A way to complete a chat request:
  - **Ollama** on your machine (default), or
  - an API key for **Groq** or **OpenRouter**

Chapters 2 and 3 need a model that can emit tool calls. Chapter 1 is a single completion and will run on any chat model.

### Install

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

### Configure `.env`

```bash
cp .env.example .env
```

`.env` is gitignored. `.env.example` is the committed template. Do not put a real hosted key in git.

The labs read three variables from the repo-root `.env` (process environment variables win if they are already set):

| Variable | Meaning | Ollama default |
|---|---|---|
| `BASE_URL` | OpenAI-compatible API origin | `http://localhost:11434/v1` |
| `API_KEY` | Bearer token. Ollama ignores the value and still wants a non-empty string. | `ollama` |
| `MODEL` | Model name that server expects | `llama3.2` |

Commented Groq and OpenRouter blocks are in `.env.example`. Use one provider at a time.

### Ollama

Install from [ollama.com/download](https://ollama.com/download), then pull the default tag and start the server if it is not already running:

```bash
ollama pull llama3.2
ollama serve
```

Leave that server running and use the default `.env` values:

```env
BASE_URL=http://localhost:11434/v1
API_KEY=ollama
MODEL=llama3.2
```

If Chapter 2's trace never shows a `read_file` call, pull a tool-capable fallback and change only `MODEL`:

```bash
ollama pull llama3.1
```

```env
MODEL=llama3.1
```

### Groq or OpenRouter

Comment out the Ollama lines in `.env` and set one hosted provider. Example shapes (placeholders are not real keys):

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

Hosted requests include the prompt and, for Chapters 2 and 3, the text of any file the agent read. The shop docs are fictional. Do not point the client at a private document and a third-party API in the same run unless you mean to send that document.

### Run the three scripts

From the repo root, with the virtualenv active:

```bash
python labs/ch01-what-an-agent-is/hello_concierge.py
python labs/ch02-your-first-loop/file_agent.py
python labs/ch03-models-without-the-pain/swap_model.py
```

Each script prints `BASE_URL` and `MODEL` and hides the key. Optional questions are extra arguments:

```bash
python labs/ch02-your-first-loop/file_agent.py "What's the Wi-Fi password?"
python labs/ch03-models-without-the-pain/swap_model.py "How much is local delivery, and which day are you closed?"
```

Chapter 3's script is the Chapter 2 loop. Switching providers is an edit to `.env`, then the same command. Per-lab notes:

- `labs/ch01-what-an-agent-is/README.md` — what failure modes to write down
- `labs/ch02-your-first-loop/README.md` — docs, stop conditions, citation check
- `labs/ch03-models-without-the-pain/README.md` — Ollama vs Groq vs OpenRouter

### Check the harness without a model

From the repo root, after `pip install`:

```bash
python -m unittest labs.common.test_harness
```

That covers the docs path jail, tool-error handling, max steps, and the repeated-call stop. It does not contact Ollama or a hosted API.

## Secrets

- Commit `.env.example`. Do not commit `.env`.
- The default key `ollama` is a placeholder, not an account credential.
- Lab scripts print `API_KEY=set` or `API_KEY=missing` and strip the key from error text they catch.
- Shop files under `labs/ch02-your-first-loop/docs/` are sample policy text, safe to commit.
