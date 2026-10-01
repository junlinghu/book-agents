# Tutorial 4. Context engineering

## Motivation

The loop from tutorial 3 can read a document or the shelf when the question needs them, and it can stop when the work is finished or when a limit says to stop. It will also read whatever you place in front of it at the start of the turn. A Tuesday huddle produces notes: a carton count, a baking plan, and a long write-up of a picnic. Paste every note into the prompt and the question drowns. The model still answers, and the answer drifts, because the useful sentence is buried among leftovers. What the agent still cannot do is tell a title from a body, or refuse a note that is too long for the turn. We add that choice now, before memory and procedures, because those later stores will use the same habit. A short handle sits in the brief, and the full text is loaded only when the question asks for it.

## What this tutorial is about

Context, in this lesson, is the text the model sees on one call. Deciding which text that is, and which text stays on disk, is the work this tutorial calls context engineering. When the text fills with leftovers until the original question is hard to find, the book calls the result context rot. You will see a small version of it. Three staff notes, pasted together, overflow a modest budget for one turn, while a catalog of titles still fits.

You will learn to keep that catalog in the prompt and to load a note body only when the question needs it. You will learn a budget, which is a limit on how much text you deliberately add to one turn, and a second limit on a single note. A note over that second limit is refused even when the model asks for it, and the body stays out of the conversation. You will also see why a number that appears in a note is checked again on the shelf. The note is a memory of a conversation. The shelf is the count.

## How you will get there

The notebook adds a small catalog of staff notes. Titles sit in the brief. Bodies come back through a tool that reads one note. The picnic note is long on purpose. Asking for it returns a refusal, and the run that answers the morning question leaves it unread. Staff ask how many oat-milk cartons were on hand and how many cardamom buns were baked on Thursday, and they ask the agent to check the shelf for oat milk. The agent reads the short oat-milk note and the Thursday bun note, and it reads the shelf. The answer uses those readings. The picnic stays on disk, where a question about the picnic could still find it later.

## Additional things

A bigger prompt is a poor repair for a missing fact. When the fact lives in a file, a tool can fetch it on the turn that needs it. Loading every file on every question spends the budget on text the question never uses.

The refusal of an oversized note is useful information. It tells you the note should be split, or that the question should name a smaller piece. Tutorial 5 treats durable memory the same way. A search should return a short match, because dumping every saved row recreates the crowding you just watched. Tutorial 6 loads one procedure by name, when the question matches, and leaves the other procedures on disk.

A map of titles, a cap on each body, and a refusal of the oversized picnic note are the whole of the budget in this lesson. The café’s notes are practice documents, not a record of a real shop.

## Sources and references

- Note titles, caps, and bodies live in [common/notes.py](common/notes.py) and [data/notes](data/notes).
- The previous lecture is [3-agent-loop.md](3-agent-loop.md). The notebook is [4-context-engineering.ipynb](4-context-engineering.ipynb). The series map is in [README.md](README.md).
