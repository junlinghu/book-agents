# Tutorial 4. Context engineering

## Motivation

The loop from the previous tutorial will read whatever you place in front of it. A Tuesday huddle produces notes: a carton count, a baking plan, a long write-up of a picnic. Paste every note into the prompt and the question drowns. The model still answers, and the answer drifts, because the useful sentence is buried. This lesson is about choosing what enters the prompt, and leaving the rest on disk until a question asks for it.

## What this tutorial is about

Context is the text the model sees on one call. Context engineering is the work of deciding which text that is. Context rot is what happens when that text fills with leftovers until the original question is hard to find.

You will learn to keep a catalog of note titles in the prompt and to load a note body only when the question needs it. You will learn a budget: a limit on how much text you deliberately add to one turn. You will see a note that is too long for that budget refused, even when the model asks for it. You will also see why a number that appears in a note is checked again on the shelf. The note is a memory of a conversation. The shelf is the count.

## How you will get there

The notebook adds a small catalog of staff notes. Titles sit in the brief. Bodies come back through a tool that reads one note. One note is over the size limit, so you can see the refusal. A long picnic note is the wrong document for a question about how many cartons are on hand, and the run leaves it unread.

The question that matters asks about oat milk. The agent reads the short note that discusses it, and it reads the shelf. The answer uses the shelf count. The hands-on steps are in the notebook [4-context-engineering](4-context-engineering.ipynb).

## Additional things

A bigger prompt is not a repair for a missing fact. If the fact lives in a file, a tool can fetch it on the turn that needs it. Loading every file “just in case” spends the budget on text the question never uses.

The size limit on a single note is a second rail. A model that asks for an oversized body receives a refusal, and the body stays out of the conversation. That refusal is useful. It tells you the note should be split, or that the question should name a smaller piece.

Later lessons treat memory and skills the same way: a short handle in the prompt, and the full text loaded when the question matches. Chapter 5 is the book’s treatment of budgets, rot, and a map of notes instead of a paste.

The café in these files is fictional. The notes are practice documents, not a record of a real shop.

## Sources and references

- [Chapter 5: Context engineering](../../chapters/ch05-context-engineering/README.md), and the lab [labs/ch05-context-engineering](../ch05-context-engineering).
- The previous lecture is [3-agent-loop.md](3-agent-loop.md). The series map is in [README.md](README.md).
