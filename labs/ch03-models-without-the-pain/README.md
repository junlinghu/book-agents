# Lab — Chapter 3. Swap the model, keep the loop

The Chapter 2 agent, run from this directory, against the Chapter 2 docs. You change models by editing `MODEL` in the repo-root `.env` only.

Chapter: [Chapter 3: Local and Hosted Models](../../chapters/ch03-models-without-the-pain/README.md)

## Goal

Run the same question twice. Once with `MODEL=gpt-4.1-mini`. Once with `MODEL=gpt-4.1`. Leave `swap_model.py` untouched between the runs. Compare tool logs, stop tags, and citations.

Differences you can attribute to the model are the point. The harness, the key, and the shop files stay put. You can smoke-test the script with one model. The comparison this lab asks you to turn in needs both.

## Assignment

Turn in:

1. Two complete runs of the default question: one `gpt-4.1-mini`, one `gpt-4.1`. For each, include the startup header, the tool log, the answer, the stop line, and any `NOTE:` lines.
2. A comparison: `MODEL`, which files were read, stop tag, step count, and which claims cite which file.
3. A note if either run skipped tools or offered to book, refund, or email. Leave `swap_model.py` unchanged. Do not add `tool_choice`.
4. The fixed harness values from both headers, showing they matched. If you used a different tool-capable id because one of these was retired, say which id and why.

## Prerequisites

- The shared setup in [`../README.md`](../README.md). Chapter 1 or 2's virtualenv is enough if you already did it
- One OpenAI API key in `.env`
- Two tool-capable model ids. These notes use `gpt-4.1-mini` and `gpt-4.1`

## Setup

Do the shared setup in [`../README.md`](../README.md) once, then come back here. If you already installed dependencies for Chapter 1 or 2, reuse that virtualenv.

Work from the repository root. `swap_model.py` loads `.env`, prints the header, and calls `run_file_agent` from `labs/common/loop.py` (the same loop as Chapter 2). It reads:

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

The script also prints `MODEL`, and `OPENAI_API_KEY=set (value hidden)` or `OPENAI_API_KEY=missing (value hidden)`. The key itself is not printed. `MODEL` is the line that should differ.

If `TEMPERATURE` or `MAX_TOKENS` differ between your two runs, you edited the harness, and the comparison is no longer the one this chapter asks for.

`read_file` executes on your machine. The file text is then sent to the OpenAI API as the tool result on the next request. The shop docs are fictional.

Edit `MODEL` in `.env` at the repo root to switch models. Leave `OPENAI_API_KEY`, `swap_model.py`, `labs/common/`, and the docs alone. A restart is not required. The next process reads `.env` again. The script prints the two ids again after each run.

Two active `MODEL=` lines are easy to misread: the last assignment wins. Process environment variables win over `.env`.

**`gpt-4.1-mini`** is the default. It supports tool calls. The id is documented at [developers.openai.com/api/docs/models/gpt-4.1-mini](https://developers.openai.com/api/docs/models/gpt-4.1-mini).

**`gpt-4.1`** is the second run. Same key, same client, larger model in the same family. The id is documented at [developers.openai.com/api/docs/models/gpt-4.1](https://developers.openai.com/api/docs/models/gpt-4.1).

If the API says an id is gone, pick another current tool-capable id from [the models page](https://developers.openai.com/api/docs/models) and change only `MODEL`. Say so in your notes. Do not commit the key.

## Steps

From the repo root, with the virtualenv active. Do not edit `swap_model.py` between runs.

1. Set `MODEL=gpt-4.1-mini` in `.env`. Run the default question.

   ```bash
   python labs/ch03-models-without-the-pain/swap_model.py
   ```

   Default question: "How much is local delivery, and which day are you closed?"

2. Set `MODEL=gpt-4.1`. Run the same command again.

3. Optional. Pass another question, and run that same question on both models. Keep the question text identical across the two runs.

   ```bash
   python labs/ch03-models-without-the-pain/swap_model.py "What's the Wi-Fi password?"
   ```

The harness does not send `tool_choice`, so the loop cannot force the read. A run that skips tools is a result from that model. Change `MODEL` and run again. Leave the script alone.

## What to write up

Keep both traces. For each, record:

- `MODEL`
- `TEMPERATURE`, `MAX_TOKENS`, `MAX_STEPS`, and the `DOCS` path
- Whether `policy.md` was read, and whether `faq.md` was read (quote the tool-log lines)
- The stop tag and the step count
- Every `NOTE:` line
- Each shop fact the answer states, and the file path it cites, or that it cites none
- Any offer to book, refund, or email. The tool list cannot do those

Then write a short comparison: what changed between the two models, and which header values stayed the same.

## Troubleshooting

HTTP 401 and HTTP 404 on the model id are the checks in [`../README.md`](../README.md). A request error is not a defect in `swap_model.py`.

- Empty tool log on a model that should call tools: run once more and keep both outputs. If it is stable, note it. That is a Chapter 3 result, not a broken script.
- `max_tokens`, or truncated tool-call JSON: leave `MODEL` in place and look at `MAX_TOKENS` in `labs/common/client.py` (800). Changing the model and the token limit in one edit muddies the comparison. Record it if you change the limit.

Instructor notes are in `SOLUTION.md` in this folder. If this lab is homework, finish the write-up before you open that file.
