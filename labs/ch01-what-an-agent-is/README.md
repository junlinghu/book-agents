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

- The shared setup in [`../README.md`](../README.md): Python 3.10 or newer, and an OpenAI API key in `.env`
- Tool calling is not required for this lab

## Setup

Do the shared setup in [`../README.md`](../README.md) once, then come back here. Work from the repository root. Chapter 1 sends the persona and the question. It does not send shop files.

## Steps

From the repo root, with the virtualenv active.

1. Run the default question.

   ```bash
   python labs/ch01-what-an-agent-is/hello_concierge.py
   ```

   The script loads `OPENAI_API_KEY` and `MODEL` through `labs/common/client.py`. It prints the model with the key hidden, plus `TEMPERATURE`, `MAX_TOKENS`, and `TOOLS=none`. It sends a system prompt and your question to `chat.completions.create`. There is no `tools` argument. It prints the reply, then a checklist of failure modes.

   Default question:

   > I opened a bag of your house coffee and they're not for me. Can I return them? Also, can you ship a cardamom bun to another state?

2. Optional. Pass another question for a second sample:

   ```bash
   python labs/ch01-what-an-agent-is/hello_concierge.py "What time do you open on Monday, and what's the Wi-Fi password?"
   ```

   This script cannot look that up either.

## What to write up

From the run, record:

- The header, including `TOOLS=none` and `MODEL`. The key is not printed. `TOOLS=none` is there so a later Chapter 2 trace is obviously a different program.
- The full reply.
- Three quoted sentences, each labeled with one of these modes:
  - **Invented shop fact.** A return window, a fee, an hour, or a price this program had no way to look up.
  - **Fake citation.** A file path in the reply. Nothing was read, so a path is invented. If the reply names no path, write that down too.
  - **Action this process cannot take.** An offer to process a refund, print a label, or email the customer. This process cannot do those things.
- Whether the model hedged ("I don't know the shop's policy") or stated a rule with confidence.

The script's closing note is a checklist for your write-up. It is not a grade of your model.

## Troubleshooting

A request error means `.env` or the key, not the café prompt. The checks are in [`../README.md`](../README.md). The key is not printed.

Instructor notes are in `SOLUTION.md` in this folder. If this lab is homework, finish the write-up before you open that file.
