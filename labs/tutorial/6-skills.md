# Tutorial 6. Skills as procedures

## Motivation

The agent can now read the shop, loop until it has an answer or a reason to stop, choose which notes to load, and remember a guest constraint after the chat ends. What it still cannot do is follow a procedure that lives in its own document. A standing brief that holds every procedure grows long, and it goes stale the moment a procedure changes. Recommending a pastry is one procedure. Restocking the shelf is another. Both can share the same tools. What differs is the order of the steps, and the promise the agent is allowed to make. We add a skill now, a written procedure loaded when the question matches, so the brief stays short and the steps stay editable. The recommendation is the procedure this tutorial practices. The restock procedure waits for the shop manager, after the checks a restock requires are in place.

## What this tutorial is about

A skill is a written procedure with a name. It tells the agent which tools to use, and in what order, for one kind of question. It stands apart from the system prompt, which is the standing brief, and apart from the tools, which are the actions the program can perform. The skill is instructions. The tools are how those instructions touch the shop.

You will load one skill, the recommendation procedure, and then follow it. The procedure says to search durable memory and to read the menu and the allergen list. Priya’s allergy is already on disk from the memory lesson. The menu lists what the shop sells and what it contains. The cardamom bun contains almonds, so it is the wrong pastry for this guest, and the shop has no nut-free preparation area. The skill names the steps and the refusals. Prices and ingredients stay in the menu. When the menu offers no safe pastry, the answer says so and withholds a promise the menu does not support.

## How you will get there

The notebook registers a tool that returns the text of a named skill. You ask for a pastry recommendation for Priya. The agent loads the procedure, searches memory, and reads the menu. The reply follows those steps. You read the skill text and the answer side by side. The food itself is described from the menu, and the allergy comes from the memory file. The procedure told the agent where to look. It did not become a second copy of the menu.

## Additional things

A skill that copies the menu becomes a second menu. The next price change updates one copy and leaves the other behind. Keep facts in the documents and on the shelf. Keep the procedure as steps.

Loading a skill spends the same kind of room in the prompt that loading a note does. Load the procedure the question needs, and leave the others on disk. A catalog of names can sit in the brief. The body arrives through the tool, which is the same habit tutorial 4 taught for staff notes.

The restock procedure appears again in tutorial 15. The same idea is at work there. A skill names the steps, and the tools, the checker, and the gate still decide what is true and what may be written down. Chapter 7 is the book’s treatment of skills as portable procedures. The guest constraint and the menu are practice data.

## Sources and references

- [Chapter 7: Skills as Portable Procedures](../../chapters/ch07-skills-as-portable-procedures/README.md), and the lab [labs/ch07-skills-as-portable-procedures](../ch07-skills-as-portable-procedures).
- The previous lecture is [5-memory.md](5-memory.md). The notebook is [6-skills.ipynb](6-skills.ipynb). The series map is in [README.md](README.md).
