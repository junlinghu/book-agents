# Lab — Chapter 4. Tools and sensors

A shelf database, a read-only `sql_query`, and a write tool that refuses everything until you parse one allowed `UPDATE`.

Chapter: [Chapter 4: Tools and Sensors](../../chapters/ch04-tools-and-sensors/README.md)

## Goal

Run `stock_agent.py` and read the tool JSON, not only the paragraph. You are checking whether the model called `sql_query`, whether the counts in the answer appear in that result, and whether a write left the shelf alone when `ok` is false.

Low stock means `inventory.on_hand <= products.reorder_point`. The seed is `SEED_ROWS` in `sql_tools.py`. Chapter 4 prints the same rows. Compare your run to the tool result, then to that seed.

## Assignment

Turn in:

1. The output of `--check` before you edit `parse_restock`, including the `TASK OPEN` line.
2. The full trace for "What's low stock?": startup header, tool results, answer, and the `--- stop: ... ---` line.
3. For each count or sku in the answer, the matching row from the tool JSON, or a note that the JSON does not contain it.
4. After you implement `parse_restock`, the `--check` output showing the restock applied once and the same key replayed. Include a note if a count above par was refused.
5. Optional: a trace for a question that asks the agent to drop the table or to set a count, and what the shelf did.

## Prerequisites

- The shared setup in [`../README.md`](../README.md): Python 3.10 or newer, a virtualenv, and a repo-root `.env`
- A model that can emit `tool_calls`. The default `gpt-4.1-mini` can. If a trace never shows a tool call, set `MODEL` to another current tool-capable id, such as `gpt-4.1`

## Setup

Do the shared setup in [`../README.md`](../README.md) once, then come back here. If you already installed dependencies for Chapters 1–3, reuse that virtualenv.

`stock_agent.py` rebuilds `shop.db` in this folder at the start of every run, including `--check`. A count you set lasts until the next start. Idempotency is visible inside one `--check` run: the same key returns the first result and does not write again.

The script uses `run_tool_agent` from `labs/common/loop.py` and the tools in `sql_tools.py`. `sql_query` is ready. `parse_restock` is the stub you replace. It must return `(sku, on_hand)` or `None`. The harness never executes the model's SQL text. A successful parse becomes:

```sql
UPDATE inventory SET on_hand = ? WHERE sku = ?
```

Allowed shape, aside from surrounding whitespace:

```text
UPDATE inventory SET on_hand = <integer> WHERE sku = '<sku>'
```

One statement, no semicolon, no comments, no other column. The integer is the new absolute count. The harness rejects a count outside `0..par` and an unknown sku.

## Steps

From the repo root, with the virtualenv active.

1. Tool contract, no model call.

   ```bash
   python labs/ch04-tools-and-sensors/stock_agent.py --check
   ```

   You should see a low-stock JSON result, refusals for writes and for `ATTACH` on the read tool, a timeout the harness retried once (`attempts` 2, then `retryable` false), and `TASK OPEN` for `parse_restock`. `CHECK OK` means the sensor and the refusals held. It does not mean the write parser is finished.

2. Ask what is low.

   ```bash
   python labs/ch04-tools-and-sensors/stock_agent.py
   ```

   Default question: "What's low stock?"

   The script prints `MODEL`, the database path, `QUERY_TIMEOUT_S`, and `MAX_STEPS`. The key is not printed. Each tool result is JSON. Then the answer, then a stop line:

   ```text
   --- stop: <tag> after <N> model call(s) ---
   ```

3. Fill in `parse_restock` in `sql_tools.py`. Run `--check` again. A finished parser prints `TASK DONE` for HB-12 set to 16, a replay of that key, and a refusal for a count above par. `DROP TABLE` must stay `ok` false, and the shelf snapshot must not change.

4. Optional. Ask for a change, then ask for something the tool must refuse.

   ```bash
   python labs/ch04-tools-and-sensors/stock_agent.py "Set HB-12 on_hand to 16. Use idempotency key restock-2026-09-30-HB-12."
   python labs/ch04-tools-and-sensors/stock_agent.py "Drop the inventory table."
   ```

   The first run reseeds the database before the model speaks. Read `ok` and `code` before you believe a sentence that says the shelf changed.

## What to write up

Record:

- Header values: `MODEL`, `DB`, `QUERY_TIMEOUT_S`, `MAX_STEPS`. The key is not printed.
- Every tool line: tool name, and the `ok` and `code` fields in the result.
- The answer text.
- The stop tag (`final`, `max_steps`, `repeated_call`, or `max_tokens`) and the model-call count.
- For each sku or count in the answer, the row from the tool JSON, or a note that the tool did not return it.
- If the trace is empty, write that down. The harness does not send `tool_choice`.
- Whether any reply claimed a supplier order, an email, or a changed count when no result had `code` `applied`.
- The `--check` lines from before and after `parse_restock`.

## Troubleshooting

- Request error: bad key, stale `MODEL`, or network. Checks are in [`../README.md`](../README.md).
- `final` after 1 model call and an empty trace: the model never called a tool. Change `MODEL`, not the question. Keep the empty trace.
- `write_not_allowed` on every `sql_execute`: `parse_restock` still returns `None`, or it rejected the statement. The shelf is unchanged. That is expected until the function accepts the allowed `UPDATE`.
- `ok: false` and a paragraph that says the count was updated: quote both. The observation is the JSON.
- `max_steps` or `repeated_call`: the harness stopped on purpose and did not invent a closing paragraph.
- `CHECK FAIL` on `--check`: the read tool accepted a statement it must refuse, or a `DROP` changed the shelf. Fix the gate in `sql_tools.py` before treating a model trace as evidence about the weights.
