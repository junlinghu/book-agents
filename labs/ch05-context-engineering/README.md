# Lab — Chapter 5. Context engineering

A long Tuesday restock huddle, notes under a character cap, and a morning question that should reload a note instead of the transcript.

Chapter: [Chapter 5: Context Engineering](../../chapters/ch05-context-engineering/README.md)

## Goal

File `dialogue.md` into notes the next turn can open. Then ask how many cartons of oat milk were ordered, and how many cardamom buns on Thursday. Compare two ways of building the prompt: pasting every note, and sending only a map so the model calls `read_note`.

The decisions are in the dialogue. Chapter 5 shows the shape of a durable note and of a lossy summary. Your files have to match the huddle, and the morning answer has to match a note the trace actually returned.

## Assignment

Turn in:

1. The `size` output while `CONTEXT_STRATEGY` is still `paste` and the only note is the starter transcript. Include `INITIAL_CONTEXT_CHARS` and `TURN_BUDGET`.
2. The note files you wrote with `file_durable_notes` (names, titles, and whether each is under `PER_NOTE_CAP`).
3. The `size` output after you switch `CONTEXT_STRATEGY` to `map`.
4. Two traces of the morning question, or one trace if the pasted run was too large to be worth a second model call: say which you ran. For each, the header, tool results, answer, and stop line.
5. For each quantity in the answer, the note body it came from, or a note that no tool result contained it.
6. Optional: the `agent` trace, and a morning question about the mill picnic or the bun recipe.

## Prerequisites

- The shared setup in [`../README.md`](../README.md): Python 3.10 or newer, a virtualenv, and a repo-root `.env`
- `file` and `size` do not call a model. `next` and `agent` need a model that can emit tool calls

## Setup

Do the shared setup in [`../README.md`](../README.md) once, then come back here. Reuse the virtualenv from earlier chapters.

The huddle is `dialogue.md` in this folder. Notes are written to `notes/`, which the script creates. `file` and `agent` delete existing `*.md` notes in that folder before they write.

Two knobs in `notes_lib.py`:

- `file_durable_notes` — the starter writes the whole dialogue to `transcript.md`. Replace that body with short notes. Do not write `transcript.md`. A file longer than `PER_NOTE_CAP` (800 characters) cannot be returned by `read_note`.
- `CONTEXT_STRATEGY` — the starter is `paste`. Set it to `map` so the system prompt holds names and titles, and the body arrives only through `read_note`.

`TURN_BUDGET` is 2000 characters. `size` prints the comparison. It does not call a model.

Keep quantities and the bun plan in durable notes. A lossy summary, if you write one, goes in its own file and does not carry the only copy of a number. Leave out the rain, the porridge bowl, a recipe change, a Wi-Fi guess, and any version of the picnic in which the café accepted the job. The picnic was declined.

## Steps

From the repo root, with the virtualenv active.

1. File the starter dump and measure it. No model call.

   ```bash
   python labs/ch05-context-engineering/restock_notes.py file
   python labs/ch05-context-engineering/restock_notes.py size
   ```

   `file` is also the default when you pass no command. `size` should report the transcript over both caps.

2. Optional, before you edit the notes. Ask the morning question against the dump.

   ```bash
   python labs/ch05-context-engineering/restock_notes.py next
   ```

   Default question: how many cartons of oat milk, and how many cardamom buns on Thursday. If a note is refused, the prompt tells the model not to guess. Record what it did.

3. Edit `file_durable_notes` and set `CONTEXT_STRATEGY` to `map`. Run `file` again, then `size`. `read_note` should be able to return the notes that hold the numbers. The initial context should fit in `TURN_BUDGET`.

4. Ask the morning question again.

   ```bash
   python labs/ch05-context-engineering/restock_notes.py next
   ```

   The header prints `CONTEXT_STRATEGY`, both caps, and `INITIAL_CONTEXT_CHARS`. Tool results are JSON. `over_budget` means the body was not returned.

5. Optional. A second morning question, same notes:

   ```bash
   python labs/ch05-context-engineering/restock_notes.py next "Are we catering the mill picnic, and did the bun recipe change?"
   ```

6. Optional. Let the model call `write_note` during the huddle. This deletes `notes/` and does not use `file_durable_notes`.

   ```bash
   python labs/ch05-context-engineering/restock_notes.py agent
   ```

   Then `size` and `next`. Each `write_note` body must already be under the cap.

## What to write up

Record:

- `DIALOGUE_CHARS`, `PER_NOTE_CAP`, `TURN_BUDGET`, and `CONTEXT_STRATEGY` from `size`, before and after your edit.
- The note map: file name, title, character count, and whether `read_note` would refuse it.
- For a model run: `MODEL`, `INITIAL_CONTEXT_CHARS`, the question, every tool result's `ok` and `code`, the answer, and the stop line.
- Whether the oat-milk quantity and the Thursday bun count in the answer appear in a note the trace returned.
- Any claim that the recipe changed, that the café is catering, or that a Wi-Fi password was found. Those are not decisions in the huddle.
- If the tool log is empty under `map`, write that down. The quantities are not in the map's titles unless you put them there.

## Troubleshooting

- `No notes yet` on `next`: run `file` or `agent` first.
- `read_note` returns `over_budget` for every file: the notes are still the transcript, or one file holds the whole huddle. Split them in `file_durable_notes` and run `file` again.
- Initial context over `TURN_BUDGET` after the split: `CONTEXT_STRATEGY` is still `paste`.
- Request error on `next` or `agent`: checks are in [`../README.md`](../README.md). `file` and `size` do not need a key.
- Empty tool log and a confident number, with strategy `map`: the model did not read a note. Change `MODEL` if the skip is stable. Keep the trace.
- `bad_name` on `write_note`: the name has a slash, a space, or a suffix other than `.md`.
