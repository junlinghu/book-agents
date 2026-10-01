# Tutorial 5. Session and durable memory

## Motivation

By the end of tutorial 4 the agent can read the shop’s documents and the shelf, take several steps inside a loop, and load a staff note only when the question needs it. The message list can feel like memory, because the model can quote what was just said. Close that list and the sentences are gone. A guest who cannot eat almonds will be back next week, and the concierge has to remember the constraint after the chat has ended. What the agent still cannot do is save a fact that outlives the conversation, or find it again from a fresh list of messages. Copying the whole shop policy into that same store would mix a personal constraint with rules that already live in the documents. We add a small memory file now, after you have a budget for what enters a turn, and before the written procedures that will depend on this guest’s constraint.

## What this tutorial is about

Session memory is the message list for one conversation. It holds what has been said in this sitting, and it ends when you start a fresh list. Durable memory is a file the program keeps after the conversation ends. The agent can save a short fact there, and a later conversation can search for it.

In this lesson the fact is a guest constraint. Priya, a regular guest, has an almond allergy, and that constraint applies to recommendations for her. The shop’s policy and menu remain in the documents, where the earlier tools can still read them. You will learn to save a fact, to open a new conversation on purpose, and to find the fact again by search. The earlier tools and the loop are still present. Memory is an addition, and the shelf and the policy remain the sources for counts and rules.

## How you will get there

The notebook adds two actions. One writes a memory, and one searches the file. In the first turn the agent stores Priya’s allergy while the conversation is still open, and you can read the saved row in the file afterward. In the second turn the notebook builds a new message list, so nothing from the first chat is still in front of the model. The agent searches the file, and the answer in that second turn comes from the row that survived the fresh start.

## Additional things

Write the smallest fact that changes a later answer. A guest constraint is that kind of fact. A second copy of the policy will go stale beside the policy tool, which already returns the current document, so the policy stays where tutorial 2 put it.

Search should return a short match. The budget from tutorial 4 still applies, and a memory tool that dumps every row on every question recreates the crowding you just learned to avoid. Forgetting belongs in the design even when this notebook only shows saving and finding. A constraint that is no longer true should be removable, or the file becomes a record of guests the shop no longer knows.

Session messages die with the list. The JSON file does not. Tutorial 6 uses Priya’s saved allergy as an input to a recommendation procedure. The café and the guest constraint are practice data.

## Sources and references

- Durable memory is [cell_src/memory.py](cell_src/memory.py). The file it writes is `tutorial/var/memory.json`.
- The previous lecture is [4-context-engineering.md](4-context-engineering.md). The notebook is [5-memory.ipynb](5-memory.ipynb). The series map is in [README.md](README.md).
