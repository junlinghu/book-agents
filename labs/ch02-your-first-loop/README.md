# Lab — Chapter 2. Your first loop

A tool-calling loop with one tool, `read_file`, jailed to this lab's `docs/`. The agent answers from `policy.md` and `faq.md` and is instructed to cite the path.

Chapter: [Chapter 2: The Agent Loop](../../chapters/ch02-your-first-loop/README.md)

## Goal

Run `file_agent.py` and read the trace, not only the final paragraph. You are checking whether the model called `read_file`, which file it opened, how the harness stopped, and whether each shop claim in the answer names a path under `docs/`.

A claim counts as looked up when the trace shows the read. Check a citation by opening the file the model named and comparing the sentence to the text.

## Assignment

Turn in:

1. The full trace for the default question: startup header, tool results, answer, the `--- stop: ... ---` line, and any `NOTE:` lines.
2. For each shop claim in the answer, the path the model cited, and a quote from that file next to the model sentence. If the file does not contain the claim, say so.
3. A short note when the tool log is empty, or when the stop tag is something other than a finished answer. If you changed `MAX_TOKENS` to get a complete trace, say that you changed it.
4. Optional: the same write-up for one or more of the extra questions in Steps.
5. Optional: the printed output of the path-jail command and of `python -m unittest labs.common.test_harness`.

## Prerequisites

- The shared setup in [`../README.md`](../README.md): Python 3.10 or newer, a virtualenv, and a repo-root `.env`
- A model that can emit `tool_calls`. The default `gpt-4.1-mini` can. If a trace never shows `read_file`, set `MODEL` to another current tool-capable id, such as `gpt-4.1`

## Setup

Do the shared setup in [`../README.md`](../README.md) once, then come back here. If you already installed dependencies for Chapter 1, reuse that virtualenv.

The script uses the shared harness in `labs/common/loop.py` and `labs/common/tools.py`, and reads only `labs/ch02-your-first-loop/docs/`. This lab needs tool calls. If the trace never shows `read_file`, change `MODEL` as the shared setup describes. Chapter 3 runs this same loop and changes only `MODEL`.

## Documents

`read_file` may only read these files. They are the corpus for this lab.

| File | Holds |
|---|---|
| `docs/policy.md` | Returns, shipping, transit damage, local delivery fee and window |
| `docs/faq.md` | Address, hours, menu prices, allergens, Wi-Fi network name |

## Steps

The harness this script uses:

- `labs/common/loop.py` runs up to `DEFAULT_MAX_STEPS` (6) model calls. It stops on a final message with no tool call (`final`), on a third identical tool call (`repeated_call`), when the step cap is hit (`max_steps`), or when `max_tokens` cuts off a text reply (`max_tokens`).
- `labs/common/tools.py` exposes `read_file` only. Paths must stay inside `docs/`. `..`, absolute paths, hidden names, and symlinks that resolve outside the directory return an `ERROR:` string. The process keeps going.
- The system prompt tells the model to cite `docs/policy.md` or `docs/faq.md`, and to say it does not know when the files do not say.

The script prints each tool result, then the answer, then a stop line of this shape:

```text
--- stop: <tag> after <N> model call(s) ---
```

A `NOTE:` after that line means the soft checks saw an empty tool log, a missing `docs/` substring, or a harness stop. Notes do not rewrite the answer. The citation note only checks that the substring `docs/` appears. It does not check that the cited file supports the claim. Open the file.

From the repo root, with the virtualenv active:

1. Run the default question.

   ```bash
   python labs/ch02-your-first-loop/file_agent.py
   ```

   > I opened a bag of your house coffee and they're not for me. Can I return them? Also, can you ship a cardamom bun to another state?

2. Optional. Other questions:

   ```bash
   python labs/ch02-your-first-loop/file_agent.py "How much is local delivery, and which day are you closed?"
   python labs/ch02-your-first-loop/file_agent.py "What's the Wi-Fi password?"
   python labs/ch02-your-first-loop/file_agent.py "Do you sell live crabs?"
   ```

3. Optional. Path jail, no model call. From the repo root:

   ```bash
   python -c "from labs.common.tools import read_file; from pathlib import Path; print(read_file(Path('labs/ch02-your-first-loop/docs'), '../.env'))"
   ```

4. Optional. Stop conditions and the jail, without calling the API:

   ```bash
   python -m unittest labs.common.test_harness
   ```

   That run does not call the OpenAI API.

## What to write up

Record:

- Header values: `MODEL`, `DOCS`, `MAX_STEPS`. The key is not printed.
- Every tool line: tool name, path argument, and whether the result started with `PATH:` or `ERROR:`.
- The answer text.
- The stop tag (`final`, `max_steps`, `repeated_call`, or `max_tokens`) and the model-call count.
- Every `NOTE:` line, copied as printed.
- For each factual claim, the path cited and a quote from that file, or a note that the file does not contain the claim.
- If the trace is empty, write that down. The harness does not send `tool_choice`, so it cannot force a tool call.
- For the optional no-model commands, the printed line and the unittest summary.

## Troubleshooting

- Request error: bad key, stale `MODEL`, or network. Checks are in [`../README.md`](../README.md).
- `final` after 1 model call and an empty trace: the model never called the tool. Change `MODEL`, not the question, and run again. Keep the empty trace in the write-up.
- `ERROR:` in the trace for a normal question: read the error. A bad path is the model. A missing `docs/` directory is the checkout.
- `max_steps` or `repeated_call`: the harness stopped on purpose and did not invent a closing paragraph. The trace is the result.
- `max_tokens`, or a tool result that says the arguments were not valid JSON and the trace looks cut off: `MAX_TOKENS` in `labs/common/client.py` is 800. Raising it is a harness edit. Record that you changed it.

Instructor notes are in `SOLUTION.md` in this folder. If this lab is homework, finish the write-up before you open that file.
