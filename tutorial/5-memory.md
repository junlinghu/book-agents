# Tutorial 5. Session and durable memory

## Motivation

By the end of tutorial 4 the agent can read the shop’s documents and the shelf, take several steps inside a loop, and load a staff note only when the question needs it. The message list can feel like memory, because the model can quote what was just said. Close that list and the sentences are gone. Priya, a guest, cannot eat almonds and will be back next week. Staff need the agent to look that constraint up after the chat has ended. What the agent still cannot do is open a fact that outlives the conversation. Copying every guest into the prompt would mix one person’s allergy with everyone else’s order. We add one shared preference file now, after you have a budget for what enters a turn, and before the written procedures that will depend on this guest’s constraint.

## What this tutorial is about

Session memory is the message list for one conversation. It holds what has been said in this sitting, and it ends when you start a fresh list. Durable memory, in this lesson, is one markdown file the program keeps after the conversation ends. The file is `data/customer_preference.md`. Every guest uses the same fields. A heading names the guest.

In this lesson the person chatting is shop staff. Staff ask what is on file for a guest: an allergy, a usual drink or pastry, a last order. Priya’s entry records an almond allergy. Marcus’s entry records no allergy and a cardamom bun. The shop’s policy and menu remain in the documents. `get_shop_fact` still takes a topic, not a filename. The preference tool takes a name, not a filename. You will learn to start a conversation with an empty message list and to retrieve the one entry the question names. The earlier tools and the loop are still present. The preference file is an addition, and the shelf and the policy remain the sources for counts and rules.

## How you will get there

The notebook adds one action, `get_preference`. Staff ask about Priya. The tool returns Priya’s section and leaves Marcus on disk. A second turn builds a new message list and asks about Marcus. That answer comes from Marcus’s section. Nothing from the first chat had to stay in the prompt for the second lookup to work, because the file was already there.

## Additional things

Ask for the guest the question names. A tool that dumps every customer on every question recreates the crowding you just learned to avoid. The file is the durable copy. The message list is not.

Shop rules stay in the documents. A preference file that also stored the return policy would go stale beside `get_shop_fact`, which already returns the current section, so the policy stays where tutorial 2 put it. Tutorial 6 uses Priya’s allergy, already in this file, as an input to a recommendation procedure. The café and the guest entries are practice data.

## Sources and references

- The lookup is [common/memory.py](common/memory.py). The file it reads is [data/customer_preference.md](data/customer_preference.md).
- The previous lecture is [4-context-engineering.md](4-context-engineering.md). The notebook is [5-memory.ipynb](5-memory.ipynb). The series map is in [README.md](README.md).
