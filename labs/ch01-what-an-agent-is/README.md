# Lab — Chapter 1. Hello Concierge

One chat completion. No tools. The model plays the Hearth Lane Café concierge and answers a return-and-shipping question it cannot look up.

Chapter: [Ch 1. What an agent is](../../chapters/ch01-what-an-agent-is/README.md)

## Goal

Run `hello_concierge.py` and write down three failure modes you saw in the reply. The script cannot open `policy.md` or `faq.md`. Specific shop facts in the answer come from the model.

## Prerequisites

- Python 3.10 or newer
- Either **Ollama** on your machine, or an API key for **Groq** or **OpenRouter**

This lab is a single chat completion. Tool calling is not required.

## Environment

Work from the repository root (the directory that contains `requirements.txt` and `.env.example`). Chapters 1–3 share one OpenAI-compatible client. Ollama is the default. Groq and OpenRouter use the same three variables in `.env`.

The same shared setup is summarized in the top-level README under **Running the labs**. The commands below match that section.

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

`requirements.txt` installs `openai`, `python-dotenv`, and `httpx`.

## `.env`

```bash
cp .env.example .env
```

`.env` is gitignored. `.env.example` is the committed template. Do not commit a real hosted key.

| Variable | Meaning | Ollama default |
|---|---|---|
| `BASE_URL` | OpenAI-compatible API origin | `http://localhost:11434/v1` |
| `API_KEY` | Bearer token. Ollama ignores the value and still wants a non-empty string. | `ollama` |
| `MODEL` | Model name that server expects | `llama3.2` |

Process environment variables win over `.env`. Commented Groq and OpenRouter blocks are in `.env.example`. Use one provider at a time.

Ollama, from [ollama.com/download](https://ollama.com/download):

```bash
ollama pull llama3.2
ollama serve
```

```env
BASE_URL=http://localhost:11434/v1
API_KEY=ollama
MODEL=llama3.2
```

Hosted placeholders (not real keys). Comment out the Ollama lines so only one `BASE_URL` and one `MODEL` are active:

```env
# Groq
BASE_URL=https://api.groq.com/openai/v1
API_KEY=gsk_your_key_here
MODEL=llama-3.3-70b-versatile
```

```env
# OpenRouter — confirm the id on the model page
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-your_key_here
MODEL=meta-llama/llama-3.3-70b-instruct
```

Chapter 1 sends the persona and the question. It does not send shop files.

## Run

From the repo root, with the virtualenv active:

```bash
python labs/ch01-what-an-agent-is/hello_concierge.py
```

Pass another question as arguments if you want a second sample:

```bash
python labs/ch01-what-an-agent-is/hello_concierge.py "What time do you open on Monday, and what's the Wi-Fi password?"
```

Monday hours and the Wi-Fi password are also unknowable to this script. Monday is a real shop fact in Chapter 2's FAQ (the café is closed). The password is not in the FAQ at all.

## What the script does

- Loads `BASE_URL`, `API_KEY`, and `MODEL` through `labs/common/client.py`.
- Prints those values with the key hidden, plus `TOOLS=none`, `TEMPERATURE`, and `MAX_TOKENS`.
- Sends a system prompt and your question to `chat.completions.create`. There is no `tools` argument.
- Prints the reply, then a checklist of failure modes to look for.

The default question:

> I opened a bag of your house coffee and they're not for me. Can I return them? Also, can you ship a cardamom bun to another state?

The shop's own answer, which this script is not allowed to read, is in `labs/ch02-your-first-loop/docs/policy.md`: opened coffee is final sale, and pastries are not shipped. You will use that file in Chapter 2. You can open it yourself after the run to score the reply. Opening it before the run is fine too — the program still does not see it.

## What to observe

1. **Invented shop facts.** A return window, a fee, an hour, or a price. Quote the sentence.
2. **No source.** The reply should not cite `docs/policy.md` or `docs/faq.md`, because nothing was read. If it cites a path anyway, that citation is also invented.
3. **No action boundary.** Offers to process a refund, print a label, or email the customer. This process cannot do those things.

Also note the hedge case. If the model says it does not know the shop's policy, write that down as a different outcome from a confident wrong window. Both are valid Chapter 1 results. The script's closing note is a checklist, not a pre-written grade of your model.

The header line `TOOLS=none` is there so a later Chapter 2 trace is obviously a different program.

## Troubleshooting

A connection error means `.env` or the server, not the café prompt.

- Check `BASE_URL`. The Ollama default is `http://localhost:11434/v1`.
- For Ollama, confirm `ollama serve` is up and `ollama pull llama3.2` has finished.
- For Groq or OpenRouter, confirm `API_KEY` is a real key and `MODEL` is an id that provider still serves.
- The key is not printed. `API_KEY=set (value hidden)` means a non-empty value was loaded.
- An empty `API_KEY` exits before the request. For Ollama use the literal value `ollama`.
