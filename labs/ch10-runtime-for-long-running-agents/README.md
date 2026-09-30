# Lab — Chapter 10. Runtime for long-running agents

A house-coffee restock with a mock ledger. The starter places an order on every run. You add a checkpoint, a human confirmation, and an idempotent place step so a killed job can resume without ordering twice.

Chapter: [Chapter 10: Runtime for Long-Running Agents](../../chapters/ch10-runtime-for-long-running-agents/README.md)

## Goal

Run session `restock-1842` until a draft is saved, stop the process before placement, then resume. The ledger for that session id contains one row. A third start does not add another. The draft quantity stays the quantity that was confirmed.

A model note is optional. The runtime, not the prompt, decides whether `append_order` runs.

## Assignment

Turn in:

1. The checkpoint JSON after the paused draft, before any ledger row for this session.
2. The command you used to stop at the draft, and the command you used to resume after confirmation.
3. The ledger file after resume, and again after one more start of the same session id. One row for `restock-1842`, same `order_id` both times.
4. A short note on where the order id lives. A screenshot of a chat transcript is not the record this lab accepts.
5. Optional: a one-line manager note produced from the checkpoint fields, with `draft_qty` unchanged from the file.

## Prerequisites

- The shared setup in [`../README.md`](../README.md): Python 3.10 or newer and a virtualenv
- A model is optional, and only for the manager note. The ledger check does not need one

## Setup

Do the shared setup in [`../README.md`](../README.md) once if you have not. This lab uses the standard library for SQLite and JSON.

Generated files stay local: `shop.db`, `ledger.jsonl`, and JSON files under `sessions/`. Do not commit them.

## Files

| Path | Role |
|---|---|
| `data/seed.sql` | `house-coffee` on hand 4, par 16 |
| `init_db.py` | Writes `shop.db` |
| `restock.py` | Reads stock and, as shipped, appends a ledger row every run |
| `sessions/` | Where your checkpoints go |

As shipped, `save_checkpoint` and `load_checkpoint` raise `NotImplementedError` and `run_session` does not call them. `append_order` always appends. `confirmation_status` returns `pending` and the runner ignores it. That combination is the bug.

Your finished runner should:

- Compute the draft as par minus on hand, then store that draft on the checkpoint. A later start uses the stored draft.
- Write the checkpoint after the draft. If `RESTOCK_PAUSE` is `1`, exit after that write and do not call `append_order`.
- Place only when confirmation is `confirmed` for that draft. Bind the yes to the draft (a file under the session directory is enough). A sentence in a prompt does not count.
- Use the session id as the idempotency key. A second place for the same key returns the original row and does not append.
- Keep checkpoints and the ledger inside this lab directory.

There is no charge tool and no email tool. Do not add them.

## Steps

From the repo root, with the virtualenv active.

1. Build the inventory database.

   ```bash
   python labs/ch10-runtime-for-long-running-agents/init_db.py
   ```

2. Run the starter twice and look at `LEDGER_ROWS_FOR_SESSION`. You should see the double order. Delete `ledger.jsonl` before you test the fixed runner so old rows are not the evidence.

   ```bash
   python labs/ch10-runtime-for-long-running-agents/restock.py restock-1842
   python labs/ch10-runtime-for-long-running-agents/restock.py restock-1842
   ```

3. Implement checkpoints, the pause, confirmation, and idempotent placement in `restock.py`.

4. Pause after the draft.

   ```bash
   RESTOCK_PAUSE=1 python labs/ch10-runtime-for-long-running-agents/restock.py restock-1842
   ```

   Confirm the process exited without a ledger row for this session, and that the checkpoint lists the draft quantity 12 (par 16 minus on hand 4).

5. Record a confirmation for that draft, then resume with the same session id and without `RESTOCK_PAUSE`. Then start the same session once more. Print the ledger count each time.

6. Optional kill. With a pause you can stop in the middle without a race. If you also want a hard stop, kill the process after the checkpoint write and show that resume still places at most once. Say which one you did.

## What to write up

Record:

- Checkpoint contents at pause, including session id, draft quantity, confirm status, and order id.
- How you recorded the human yes, and what happens if the draft quantity in the file changes after that yes. Placement should wait for a new yes.
- Ledger rows for `restock-1842` after resume and after the extra start.
- What a second session id does (it may place its own order). One sentence is enough.
- If you called a model, the exact fields you put in the prompt, and that the order id in the ledger did not come from the model's reply.

## Troubleshooting

- `Missing shop.db`: run `init_db.py` from the repo root, as above.
- `NotImplementedError` from `save_checkpoint`: the pause path calls the stub. Finish the write, or you are still on the starter's `run_session`, which does not checkpoint and will keep appending.
- Two ledger rows after you thought placement was idempotent: the key changed between runs, the lookup does not see the first row, or resume started a fresh session and called `append_order` anyway. The checkpoint file is the thing to read.
- The order placed while confirm status was still `pending`: the runner is not consulting `confirmation_status`.
- Draft quantity changed across the pause with no new confirmation: resume recomputed the order. Read the stored draft.
- `RESTOCK_PAUSE` has no effect: the environment variable is set on the command, and the process that evaluates it is the one you started. A checkpoint written after `append_order` is too late.
