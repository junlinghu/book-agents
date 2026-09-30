# Lab — Chapter 6. Memory

Priya's preferences in a JSON file that survives the process, a seeded belief that contradicts the FAQ, and a quiz on the next run.

Chapter: [Chapter 6: Memory](../../chapters/ch06-memory/README.md)

## Goal

Day 1 stores what the staff said about Priya. The quiz is a new process: a new message list, the same store. You are checking scope, the FAQ, and whether a stale row can be forgotten without being deleted.

`memory_forget` and `rejects_generalization` start as stubs. `--check` does not call a model. It uses a temporary copy of the seed, so it will not wipe a day-1 store you have already built.

## Assignment

Turn in:

1. The `--check` output before you edit the stubs, including both `TASK OPEN` lines.
2. The day-1 trace, then the contents of `memory/cafe_memory.json` after that process exits (active records are enough; you may omit nothing that was stored).
3. The quiz trace from a second process: three questions, tool results, answers, stop lines, and the active-memory JSON the script prints at the end.
4. After you implement `memory_forget` and `rejects_generalization`, the `--check` output with both `TASK DONE` lines.
5. A short note on the seeded bun belief: did the model try to forget it, what `code` came back, and was the row still active afterward?
6. Optional: forget Priya's budget, start another process, and ask the ceiling again. Include both traces and the store.

## Prerequisites

- The shared setup in [`../README.md`](../README.md): Python 3.10 or newer, a virtualenv, and a repo-root `.env`
- Day 1 and `quiz` need a model that can emit tool calls. `--check` and `--reset` do not
- Shop allergens are read from `labs/ch02-your-first-loop/docs/faq.md`. This lab does not copy that file

## Setup

Do the shared setup in [`../README.md`](../README.md) once, then come back here. Reuse the virtualenv from earlier chapters.

The seed is `seed_memory.json`: one active shop belief, "Cardamom buns are nut-free." The script copies it to `memory/cafe_memory.json` the first time, and leaves that file alone on later runs. `--reset` replaces it with the seed again. Say so in your notes if you reset between day 1 and the quiz. A quiz after a reset is not a test of what day 1 stored.

Tools on the model loop: `memory_get`, `memory_set`, `memory_search`, `memory_forget`, and `read_file`. Search returns active rows only. Get returns a forgotten row too, once forget works.

Two stubs in `memory_api.py`:

- `memory_forget` — set `status` to `forgotten` and save. Do not delete the row.
- `rejects_generalization` — return `"refused_generalization"` when `scope` is `shop` and the text claims the café is nut-free, or that every customer shares one guest's allergy or budget. A constraint scoped to `customer:priya` stays allowed.

Day 1's staff note, stored as separate records if the model calls `memory_set`:

> Priya from the mill office is picking up tomorrow. She is allergic to almonds. She takes oat milk in a pour-over, not dairy. Her office order has to stay at or under $40. Please remember that for the morning.

An allergy is a `constraint`. A milk choice is a `preference`. The ceiling is a `constraint`. Scope for those rows is `customer:priya`.

## Steps

From the repo root, with the virtualenv active.

1. Contract check, no model, temporary store.

   ```bash
   python labs/ch06-memory/prefs_agent.py --check
   ```

   Expect `TASK OPEN` for forget and for the generalization guard, then `CHECK OK`. `CHECK FAIL` means a row was lost or an illegal scope was stored. Fix that before you grade a paragraph.

2. Reset the lab store, then run day 1.

   ```bash
   python labs/ch06-memory/prefs_agent.py --reset
   python labs/ch06-memory/prefs_agent.py
   ```

   `--reset` alone does not call the model. The next command starts a fresh message list and may call `memory_set`. Open `memory/cafe_memory.json` after it exits.

3. Quiz, in a new process. Three questions, three fresh message lists, one store.

   ```bash
   python labs/ch06-memory/prefs_agent.py quiz
   ```

   The questions are: what must not be in Priya's order, and can we promise a nut-free bun; is the café nut-free because she is allergic; what is the ceiling on her office order.

   The script prints active memory at the end. Compare it to the file.

4. Implement the two stubs. Run `--check` again. Forget should hide `mem_buns_nutfree` from search and leave it visible to get, with `status` `forgotten`. The shop-wide nut-free sentence should be refused.

5. Optional. Clean store, day 1 again, then drop only the budget and ask in a new process.

   ```bash
   python labs/ch06-memory/prefs_agent.py --reset
   python labs/ch06-memory/prefs_agent.py
   python labs/ch06-memory/prefs_agent.py quiz "Forget the record that stores Priya's office budget."
   python labs/ch06-memory/prefs_agent.py quiz "What is the ceiling on Priya's office order? If memory has no active record, say so."
   ```

   The last command is a new process. `$40` from an active row is a different result from `$40` after a successful forget.

## What to write up

Record:

- `--check` before and after the stubs, including `TASK OPEN` or `TASK DONE`.
- Day 1 header: `MODEL`, `STORE`, `DOCS`, `MAX_STEPS`. The key is not printed.
- Day 1 tool results and the records in the JSON file afterward. Note the seeded belief if it is still active.
- For each quiz question: tool names, `ok` and `code`, the answer, and the stop line.
- Whether the bun answer agrees with `faq.md`, and whether a shop-wide nut-free record was written.
- If forget returned `forget_not_implemented`, quote it and say whether the belief was still active.
- Empty tool logs. The harness does not send `tool_choice`. A polite paragraph with no `memory_set` on day 1 will not be there in the morning.

## Troubleshooting

- Request error: checks are in [`../README.md`](../README.md). `--check` does not need a key.
- Quiz "forgets" Priya because you passed `--reset` in between: that flag copies the seed over the store. Day 1 has to run again.
- `bad_scope` on `everyone` or `shop` for her allergy: the tool is enforcing the scope. The repair is `customer:priya`, not a second copy with a looser scope.
- `forget_not_implemented`: the stub. The file is unchanged. That is the assignment, not a failed request.
- Search still returns a row after forget reports success: `status` was not saved as `forgotten`, or the row was written again later in the same quiz.
- `read_file` returns `ERROR:` for `faq.md`: the Chapter 2 docs directory is missing. The path is printed as `DOCS`.
