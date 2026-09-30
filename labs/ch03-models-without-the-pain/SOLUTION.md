# Solutions — Lab 3. Swap the model, keep the loop

For instructors, or for a self-check after you have finished the write-up. Do not read this before the lab if you are using it as homework.

`swap_model.py` must be unchanged between the two runs. The only model switch is `MODEL` in the repo-root `.env`. Docs stay [`labs/ch02-your-first-loop/docs/policy.md`](../ch02-your-first-loop/docs/policy.md) and [`labs/ch02-your-first-loop/docs/faq.md`](../ch02-your-first-loop/docs/faq.md). There is no second copy.

Fixed harness values, printed at startup, should match on both runs:

- `TEMPERATURE` `0.2` and `MAX_TOKENS` `800` (`labs/common/client.py`)
- `MAX_STEPS` `6` (`labs/common/loop.py`)
- `DOCS` pointing at `labs/ch02-your-first-loop/docs`

`OPENAI_API_KEY` stays the same key. It is printed as set or missing, never as the value.

## Expected outcomes

### Default question (both models)

> How much is local delivery, and which day are you closed?

When the model actually reads the files, a grounded answer says:

- Delivery fee $4.50, free at $35 and above, Tuesday–Friday 8:00–14:00, within 3 miles of 12 Hearth Lane, North Mill — `docs/policy.md` (Local delivery). No local delivery on Saturday, Sunday, or Monday is part of that same section.
- Closed Monday, all day, including a holiday that falls on Monday — `docs/faq.md` (Where and when). Weekday hours there are Tuesday–Friday 7:30–15:30. Weekend hours are Saturday–Sunday 8:00–16:00.

Both `policy.md` and `faq.md` should appear in the tool log. The fee is not in the FAQ. The hours table is not in `policy.md`. `policy.md` does say coffee does not ship on Monday and that there is no local delivery that day. Those lines are not a substitute for the FAQ's closed-day rule.

Stop tag `final` is the success path. The step count should be greater than 1 when a file was read. The exact count can differ by model. Wording can differ. The shop facts and the files they cite should not.

These notes use `gpt-4.1-mini` and `gpt-4.1`. Both support tool calls. A student who substituted another current tool-capable id, and said so, still meets the assignment.

What may differ across models, and should be written down rather than "fixed":

- Whether any tool ran
- Which files were read
- Stop tag and step count
- Whether each claim names the file that contains it

A run that skips tools is a model result. The harness does not send `tool_choice`. An empty tool log on one model and a traced answer on the other is a valid Chapter 3 comparison. Grade the empty run as a miss on grounding, and grade the write-up on whether the student recorded it and left `swap_model.py` alone.

`read_file` executes locally. The file text is then sent to the OpenAI API as the tool result.

### Optional question

Any extra question uses the Chapter 2 key in [`labs/ch02-your-first-loop/SOLUTION.md`](../ch02-your-first-loop/SOLUTION.md). The required comparison is the default delivery-and-closed-day question, run on two models. The Wi-Fi case, if a student ran it on both: network name `hearth-guest` from `docs/faq.md`, and no invented password.

## How to score

Credit a submission that has two traces, two model ids, the same default question, and an unedited `swap_model.py`.

| Check | Full credit | Common miss |
|---|---|---|
| Models | Headers show two different `MODEL` values, by default `gpt-4.1-mini` and `gpt-4.1` | One model only, or both runs still on the same id |
| Harness held still | `TEMPERATURE` 0.2, `MAX_TOKENS` 800, `MAX_STEPS` 6, and the Chapter 2 `DOCS` path match | Editing `swap_model.py`, `labs/common/`, or copying the docs |
| Delivery claim | $4.50, free at $35+, Tue–Fri, 3 miles, cited to `docs/policy.md`, and the trace read that file | A fee with no read, or the fee cited to `faq.md`. $6.00 is the coffee shipping fee, not delivery |
| Closed day | Monday, cited to `docs/faq.md`, and the trace read that file | "Closed Monday" taken only from `policy.md`'s shipping or delivery lines |
| Empty tool log | Recorded, with the stop tag (often `final` after 1 call) and a `NOTE:` about no tool | Grading the prose and ignoring the empty log, or patching the script to force a call |
| Action boundary | The reply only reads and answers | An offer to book, refund, or email. The tool list cannot do those |
| Key handling | `OPENAI_API_KEY` printed as set or missing, value hidden | A real key committed in `.env` or pasted into the write-up |
| Token limit | Both runs keep `MAX_TOKENS` 800, or the write-up says the limit was changed and `MODEL` was held still | Changing the model and `MAX_TOKENS` in the same edit, then attributing the difference to the model |

`NOTE:` lines are soft checks. They do not rewrite the answer. An empty-log note means the model missed the tool. A missing-`docs/` note means the answer text has no `docs/` substring. Neither note confirms that a cited sentence is in the file. Open the file.
