# Ch 2. Your first loop

Part I — Foundations

Chapter 1 sent one completion and let the model talk about a shop it could not see. This chapter puts the model in a loop: perceive the transcript, let it propose a tool call, run that tool in your process, append the result, and repeat until a stop condition fires. The tool is `read_file`, jailed to `labs/ch02-your-first-loop/docs/`. The product claim of the chapter is small enough to implement in an afternoon: **the loop is the product; the prompt is not.**

The lab is `labs/ch02-your-first-loop/file_agent.py`. It uses the shared harness in `labs/common/loop.py` and `labs/common/tools.py`.

## 2.1 Perceive → reason → act → observe

Say the loop as four beats. Then match each beat to a line of code so the words cannot float free of the program.

**Perceive.** The model sees a list of messages: the system prompt, the customer's question, and every tool result so far. It does not see the filesystem. If a fact is not in that list, it is not in the model's world on this turn.

**Reason.** You call the model. The call is opaque. You do not inspect weights. You inspect the object that comes back: either assistant text, or one or more `tool_calls`, or both.

**Act.** If there are tool calls, your code runs them. The model does not open files. `read_file` in `labs/common/tools.py` does. That split is the security boundary you will tighten later. In this chapter the boundary is a directory prefix check.

**Observe.** You append a `role: tool` message whose `tool_call_id` matches the call, then you call the model again. The observation is data, including an `ERROR:` string when the path was illegal or missing. An exception that kills the process is a lost observation. The model cannot correct a crash it never sees.

```
customer question
        |
        v
   +---------+
   |  model  |  <-- messages (perceive / reason)
   +---------+
        |
        |-- no tool_calls --> final text, stop
        |
        v
   harness runs read_file (act)
        |
        v
   tool message appended (observe)
        |
        +--> model again, until a stop condition
```

The implementation is `run_file_agent` in `labs/common/loop.py`. Each iteration does one completion with the same `tools` list, appends the assistant message, and either returns the text or dispatches every tool call:

```python
response = client.chat.completions.create(
    model=model,
    messages=messages,
    tools=[READ_FILE_TOOL],
    temperature=TEMPERATURE,
    max_tokens=MAX_TOKENS,
)
```

There is no `tool_choice` field. Chapter 3 explains why: Ollama's compatible endpoint does not support it. The consequence belongs in this chapter too. A model is allowed to skip the tool and answer immediately. That shows up in the lab as a final answer with an empty trace. Treat that answer the way you treated Chapter 1. The loop existed. The model did not use it.

Hearth Lane question, grounded path:

1. User: opened coffee, and can you ship a cardamom bun out of state?
2. Model calls `read_file` with `policy.md`.
3. Harness returns the file, prefixed with `PATH: docs/policy.md`.
4. Model answers: opened coffee is final sale; pastries are not shipped; both claims carry `(docs/policy.md)`.

A second question in the Chapter 3 lab needs both files (delivery fee in the policy, closed day in the FAQ). The same loop handles that without a new branch. Two tool calls, two observations, then text. That is the reason to pay for a loop instead of hard-coding "always read policy.md."

The system prompt in `SYSTEM_PROMPT` still matters. It names the two files and tells the model to cite a path or say it does not know. The prompt is a brief for the loop. It is not the thing that reads the disk. If you delete `run_file_agent` and keep the prompt, you are back in Chapter 1.

## 2.2 Tool schemas (name, args, returns, errors)

A tool the model can call has four parts you should be able to write down before you implement it.

| Part | `read_file` in this lab |
|---|---|
| Name | `read_file`. The only name the dispatcher accepts. |
| Arguments | One string, `path`, relative to the docs directory. `policy.md` and `faq.md` are the paths that exist. |
| Returns | UTF-8 text starting with `PATH: docs/...`, so the model can cite what it was shown. |
| Errors | A string starting with `ERROR:`. Missing file, escape (`..`), absolute path, hidden name, non-UTF-8. The loop continues. |

The schema sent to the server is `READ_FILE_TOOL` in `labs/common/tools.py`. The description is model-facing documentation. It tells a small model which file holds returns and which file holds hours. That description is part of the harness. It does not enforce anything. The function enforces the jail.

Paths the function refuses, all returned as text rather than raised:

- `../.env`, `docs/../../.env`, and any other `..` segment
- absolute paths such as `/etc/passwd`
- hidden names such as `.env`
- a symlink inside `docs/` whose target resolves outside `docs/`

On a miss, the error names the markdown files that do exist, so the next turn can recover:

```text
ERROR: docs/secret.md not found. Available markdown: faq.md, policy.md.
```

Argument parsing has the same shape. Providers send `function.arguments` as a JSON string. Some local stacks hand you a dict. `parse_arguments` accepts both. Invalid JSON becomes an `ERROR:` tool result that shows the expected shape, `{"path": "policy.md"}`, and the loop continues inside the step budget. An unknown tool name is the same kind of result: `ERROR: unknown tool 'send_email'. Only read_file is available.`

Returns are capped at 12,000 characters (`MAX_FILE_CHARS`). These two shop files are far smaller. The cap is there so a later document cannot silently fill the window. Truncation is marked in the tool result (`[truncated by harness]`), which keeps the observation honest.

The dispatcher is a closed set. `_dispatch` calls `read_file` or returns an unknown-tool error. There is no `eval`, no shell, and no "the model gave me a path so I opened it relative to the repo root." The docs directory is an argument to `run_file_agent`. Chapter 2's script passes `labs/ch02-your-first-loop/docs`. Chapter 3's script passes that same directory. The tool cannot be aimed at the repo root without editing the harness.

You can see the jail without a model, from the repo root:

```bash
python -c "from labs.common.tools import read_file; from pathlib import Path; print(read_file(Path('labs/ch02-your-first-loop/docs'), '../.env'))"
```

You should get an `ERROR:` line and you should not see the contents of any env file.

## 2.3 Stop conditions and max steps

A loop without a stop is a stuck process and a bill. This harness stops for four reasons. `AgentResult.stopped` records which one fired.

**`final`.** The model returned a message with no tool calls. The harness treats the assistant text as the customer-facing answer and returns it. This is the success path, including the success path where the model wrongly skipped the tool. "Final" means "the model stopped calling tools," not "the answer is true."

**`max_steps`.** `DEFAULT_MAX_STEPS` is 6, counted in model calls, not in tool calls. A question about this shop needs at most two reads. Six leaves room for a bad path, an error result, and a retry. When the budget is spent, `run_file_agent` returns a stop message and does **not** write a customer answer from the tool trace. Inventing the closing paragraph inside the harness would hide the overrun. The lab prints the trace so you can see the reads that did happen.

**`repeated_call`.** The same tool name and the same JSON arguments may run twice. The second result includes a nudge: you already read this file, answer now. A third identical call stops the loop. A model that re-reads `policy.md` forever will otherwise burn the whole step budget saying nothing new. The signature includes the arguments, so reading `policy.md` and then `faq.md` is not a repeat.

**`max_tokens`.** If a turn ends with `finish_reason == "length"` and there is no tool call, the harness stops and labels it `max_tokens`. `MAX_TOKENS` lives in `labs/common/client.py` (800). A limit that is too small cuts a reply mid-sentence. On some providers it can also cut a tool-call's argument JSON; that case usually shows up as an `ERROR:` about invalid JSON on the next observation, and the model gets a chance to retry until the step budget ends. If you see truncated arguments, raise `MAX_TOKENS`. That knob is harness. It is not a `.env` provider switch.

The lab script prints the stop tag after the answer:

```text
--- stop: final after 2 model call(s) ---
```

When you compare two models in Chapter 3, compare this line as well as the prose. A pretty paragraph that stopped as `final` with an empty tool log is a different event from a paragraph that stopped as `final` after `policy.md` was read.

## 2.4 Citing sources from tool output

The tool result starts with a path header:

```text
PATH: docs/policy.md
```

The system prompt tells the model to carry that path into the answer, in parentheses: `(docs/policy.md)`. A fee, an hour, or a return window without a path is not yet a grounded answer, even if the sentence happens to match the file. You can check the match only because the path tells you which file to open.

`file_agent.py` prints a soft note when the final text does not contain `docs/`. That note is feedback for you. It is not a checker. It does not retry the model. It looks for a substring, so a model can satisfy it with a path it never read. Chapter 11's job is to separate the checker from the drafter. Your job here is to open the cited file and confirm the sentence is actually in it.

Use these shop facts as an answer key when you grade a run by hand:

| Claim | File | What the file says |
|---|---|---|
| Opened coffee | `docs/policy.md` | Final sale |
| Unopened coffee | `docs/policy.md` | 14 days, receipt, Hearth card credit, no cash |
| Ship a cardamom bun | `docs/policy.md` | Pastries are not shipped |
| Coffee shipping under $40 | `docs/policy.md` | $6.00, US only, packed in 2 business days |
| Local delivery fee | `docs/policy.md` | $4.50, free at $35 and above, Tue–Fri, 3 miles |
| Closed day | `docs/faq.md` | Monday |
| Weekday hours | `docs/faq.md` | Tue–Fri 7:30–15:30 |
| Cardamom bun allergens | `docs/faq.md` | Wheat, butter, and almonds |
| Wi-Fi password | neither | Printed on the paper receipt. An invented password is a failure even if a path is cited |

Ask the Wi-Fi question on purpose (`python labs/ch02-your-first-loop/file_agent.py "What's the Wi-Fi password?"`). A good trace reads `faq.md` and then refuses to invent a password. A bad trace prints a plausible string. The FAQ's silence is the test.

Citations are harness work in two places: the `PATH:` header, which your code adds, and the instruction to copy it into the answer, which the model may ignore. When it ignores the instruction, you have a feedback item. Changing the adjective in the prompt is optional. Recording the miss is not.

## Lab

**Wire `read_file`. Answer a return and a shipping question from the shop docs, with path citations.**

Setup is the top-level **Running the labs** section. From the repo root, with `.env` pointed at a model that can emit tool calls:

```bash
python labs/ch02-your-first-loop/file_agent.py
```

The default question is the Chapter 1 question, so you can compare an ungrounded paragraph with a traced one. Pass another question as arguments if you want the delivery-fee case, the allergen case, or the Wi-Fi case.

What to record from one real run:

- The trace lines: which `path` was requested, and whether the first line of the result was `PATH:` or `ERROR:`.
- The stop tag (`final`, `max_steps`, `repeated_call`, `max_tokens`) and the step count.
- Whether each shop fact in the answer appears in the cited file. Quote the file line next to the model line.
- If the trace is empty, write that down as the observation. The harness did not force a tool call.

The lab README (`labs/ch02-your-first-loop/README.md`) has the extra questions and the no-model jail check. The unit tests in `labs/common/test_harness.py` cover the jail, invalid JSON, unknown tools, max steps, and the repeated-call stop without a server.

## Builder takeaway

The loop is the product; the prompt is not. The prompt tells the model which files exist and how to cite them. The loop is what opens a file, jails the path, returns errors as text, and refuses to run forever. A stronger sentence in the system prompt does not move `read_file` onto the disk. A working `read_file` still needs you, or a later checker, to confirm the citation.
