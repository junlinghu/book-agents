# Lab — Chapter 1. Hello Concierge

One chat completion, no tools. The model plays the Hearth Lane Café concierge and answers a question this script cannot look up.

Chapter: [Chapter 1: What an Agent Is](../../chapters/ch01-what-an-agent-is/README.md)

## Goal

Run `hello_concierge.py` and treat the reply as text from a model, not as a shop ruling. The script sends one chat completion. It has no tools, and it cannot open `policy.md` or `faq.md`. Anything specific in the answer — a return window, a fee, an hour, a price — came from the model and the prompt.

Your write-up records what the model claimed, and which of those claims this process had no way to check.

## Assignment

Turn in:

1. The startup header and the full model reply for the default question.
2. Three failure modes from that reply. For each one, quote the sentence and label it: invented shop fact, fake citation, or an offer to take an action this process cannot perform. If one of those labels does not appear, say so and quote what the model did instead.
3. A note on the shape of the reply: the model hedged, or it stated a shop rule with confidence. Those are different outcomes. Record which one you got.
4. Optional: the same three items for a second question you pass on the command line.

## Prerequisites

- Python 3.10 or newer
- A working chat endpoint: Ollama on your machine, or an API key for Groq or OpenRouter
- Tool calling is not required for this lab

## Setup

Work from the repository root (the directory that contains `requirements.txt` and `.env.example`). Chapters 1–3 share one OpenAI-compatible client. Ollama is the default. Groq and OpenRouter use the same three variables in `.env`.

The same shared setup is summarized in the top-level README under **Running the labs**. The commands below are enough to run this lab on its own.

1. Create a virtualenv and install dependencies.

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

2. Copy the env template. `.env` is gitignored. `.env.example` is the committed template. Do not commit a real hosted key.

   ```bash
   cp .env.example .env
   ```

   Windows PowerShell:

   ```powershell
   Copy-Item .env.example .env
   ```

   | Variable | Meaning | Ollama default |
   |---|---|---|
   | `BASE_URL` | OpenAI-compatible API origin | `http://localhost:11434/v1` |
   | `API_KEY` | Bearer token. Ollama ignores the value and still wants a non-empty string. | `ollama` |
   | `MODEL` | Model name that server expects | `llama3.2` |

   Process environment variables win over `.env`. Commented Groq and OpenRouter blocks are in `.env.example`. Use one provider at a time so a single `BASE_URL`, `API_KEY`, and `MODEL` are set.

3. Point `.env` at a chat endpoint.

   **Ollama** (default, local). Install from [ollama.com/download](https://ollama.com/download), pull the tag, and start the server if it is not already running:

   ```bash
   ollama pull llama3.2
   ollama serve
   ```

   ```env
   BASE_URL=http://localhost:11434/v1
   API_KEY=ollama
   MODEL=llama3.2
   ```

   **Groq** (hosted). Create a key in the Groq console. This placeholder is not a real key. Comment out the Ollama lines so only one `BASE_URL` and one `MODEL` are active.

   ```env
   BASE_URL=https://api.groq.com/openai/v1
   API_KEY=gsk_your_key_here
   MODEL=llama-3.3-70b-versatile
   ```

   **OpenRouter** (hosted). Model ids are `vendor/name`. Confirm the id on the model page.

   ```env
   BASE_URL=https://openrouter.ai/api/v1
   API_KEY=sk-or-your_key_here
   MODEL=meta-llama/llama-3.3-70b-instruct
   ```

   Chapter 1 sends the persona and the question. It does not send shop files.

## Steps

From the repo root, with the virtualenv active.

1. Run the default question.

   ```bash
   python labs/ch01-what-an-agent-is/hello_concierge.py
   ```

   The script loads `BASE_URL`, `API_KEY`, and `MODEL` through `labs/common/client.py`. It prints those values with the key hidden, plus `TEMPERATURE`, `MAX_TOKENS`, and `TOOLS=none`. It sends a system prompt and your question to `chat.completions.create`. There is no `tools` argument. It prints the reply, then a checklist of failure modes.

   Default question:

   > I opened a bag of your house coffee and they're not for me. Can I return them? Also, can you ship a cardamom bun to another state?

2. Optional. Pass another question for a second sample:

   ```bash
   python labs/ch01-what-an-agent-is/hello_concierge.py "What time do you open on Monday, and what's the Wi-Fi password?"
   ```

   This script cannot look that up either.

## What to write up

From the run, record:

- The header, including `TOOLS=none`, `BASE_URL`, and `MODEL`. The key is not printed. `TOOLS=none` is there so a later Chapter 2 trace is obviously a different program.
- The full reply.
- Three quoted sentences, each labeled with one of these modes:
  - **Invented shop fact.** A return window, a fee, an hour, or a price this program had no way to look up.
  - **Fake citation.** A file path in the reply. Nothing was read, so a path is invented. If the reply names no path, write that down too.
  - **Action this process cannot take.** An offer to process a refund, print a label, or email the customer. This process cannot do those things.
- Whether the model hedged ("I don't know the shop's policy") or stated a rule with confidence.

The script's closing note is a checklist for your write-up. It is not a grade of your model.

## Troubleshooting

A connection error means `.env` or the server, not the café prompt.

- Check `BASE_URL`. The Ollama default is `http://localhost:11434/v1`.
- For Ollama, confirm `ollama serve` is up and `ollama pull llama3.2` has finished.
- For Groq or OpenRouter, confirm `API_KEY` is a real key and `MODEL` is an id that provider still serves.
- The key is not printed. `API_KEY=set (value hidden)` means a non-empty value was loaded.
- An empty `API_KEY` exits before the request. For Ollama use the literal value `ollama`.

Instructor notes are in `SOLUTION.md` in this folder. If this lab is homework, finish the write-up before you open that file.
