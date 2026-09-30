# Tutorial 5. Session and durable memory

## Motivation

The message list feels like memory, because the model can quote what was just said. Close that list and the sentences are gone. A guest who cannot eat almonds will be back next week, and the concierge has to remember the constraint after the chat has ended. Copying the whole shop policy into that same store would mix a personal constraint with rules that already live in the documents. This lesson separates the conversation you are in from the facts that must outlive it.

## What this tutorial is about

Session memory is the message list for one conversation. It holds what has been said in this sitting. It ends when you start a fresh list.

Durable memory is a file the program keeps after the conversation ends. The agent can save a short fact there, and a later conversation can search for it. In this lesson the fact is a guest constraint: one regular guest has an almond allergy. That constraint applies to recommendations for that guest. The shop’s policy and menu remain in the documents, where the earlier tools can still read them.

You will learn to save a fact, to open a new conversation on purpose, and to find the fact again by search. You will see that the earlier tools and the loop are still present. Memory is an addition, not a replacement for the shelf or the policy.

## How you will get there

The notebook adds two actions: one that writes a memory, and one that searches the file. In the first turn, the agent stores the guest’s allergy. In the second turn, the notebook builds a new message list, so nothing from the first chat is still on the screen, and the agent searches the file.

You will read the saved row and the answer that uses it. The hands-on steps are in the notebook [5-memory](5-memory.ipynb).

## Additional things

Write the smallest fact that changes a later answer. A guest constraint is that kind of fact. A copy of the policy is not, because the policy tool already returns it, and a second copy will go stale.

Search should return a short match, not the whole file pasted into the prompt. The budget from the previous tutorial still applies. A memory tool that dumps every row on every question recreates the rot you just learned to avoid.

Forgetting belongs in the design even when this notebook only shows saving and finding. A constraint that is no longer true should be removable. Chapter 6 is the book’s treatment of session memory, durable memory, and stale beliefs.

The café in these files is fictional. The guest constraint is practice data.

## Sources and references

- [Chapter 6: Memory](../../chapters/ch06-memory/README.md), and the lab [labs/ch06-memory](../ch06-memory).
- The previous lecture is [4-context-engineering.md](4-context-engineering.md). The series map is in [README.md](README.md).
