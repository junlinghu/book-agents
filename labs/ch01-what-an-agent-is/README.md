# Lab — Chapter 1. Hello Concierge

One chat completion. No tools. The model plays the Hearth Lane Café concierge and answers a return-and-shipping question it cannot look up.

Chapter: `chapters/ch01-what-an-agent-is/README.md`

## Goal

Run `hello_concierge.py` and write down three failure modes you saw in the reply. The script cannot open `policy.md` or `faq.md`. Specific shop facts in the answer are coming from the model.

## Setup

Shared install, `.env`, and Ollama-or-hosted key steps are in the top-level README under **Running the labs**. You need a working chat endpoint. Tool calling is not required for this lab.

From the repo root, with the virtualenv active:

```bash
python labs/ch01-what-an-agent-is/hello_concierge.py
```

Pass another question if you want a second sample:

```bash
python labs/ch01-what-an-agent-is/hello_concierge.py "What time do you open on Monday, and what's the Wi-Fi password?"
```

Monday hours and the Wi-Fi password are also unknowable to this script. Monday is a real shop fact in Chapter 2's FAQ (the café is closed). The password is not in the FAQ at all.

## What the script does

- Loads `BASE_URL`, `API_KEY`, and `MODEL` through `labs/common/client.py`.
- Prints those values with the key hidden, plus `TOOLS=none`.
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

## Failure

A connection error means `.env` or the server, not the café prompt. Check `BASE_URL` (Ollama default `http://localhost:11434/v1`), that `ollama serve` is up or your hosted key is set, and that `MODEL` is a tag you have pulled or a hosted id that exists. The key is not printed.
