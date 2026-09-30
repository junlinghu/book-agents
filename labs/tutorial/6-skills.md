# Tutorial 6. Skills as procedures

## Motivation

A system prompt that holds every procedure grows long, and it goes stale the moment a procedure changes. Recommending a pastry is one procedure. Restocking the shelf is another. Both can share the same tools. What differs is the order of steps and the promise the agent is allowed to make. This lesson keeps a procedure in its own document and loads it when the question matches, so the brief stays short and the steps stay editable.

## What this tutorial is about

A skill is a written procedure with a name. It tells the agent which tools to use, and in what order, for one kind of question. It is separate from the system prompt, which is the standing brief, and separate from the tools, which are the actions the harness can perform. The skill is instructions. The tools are how those instructions touch the shop.

You will learn to load one skill, the recommendation procedure, and then follow it. The procedure says to search durable memory and to read the FAQ. The guest’s allergy is already on disk from the memory lesson. The FAQ lists what the shop sells and what it contains. The skill only names the steps. If the FAQ offers no safe pastry, the answer says so and withholds a promise the menu does not support.

## How you will get there

The notebook registers a tool that returns the text of a named skill. You ask for a recommendation for the guest whose allergy was saved earlier. The agent loads the procedure, searches memory, and reads the FAQ. The reply follows those steps and cites the FAQ for the food itself.

You will read the skill text and the answer side by side, and notice that the price and the allergen line come from the FAQ. The hands-on steps are in the notebook [6-skills](6-skills.ipynb).

## Additional things

A skill that copies the menu becomes a second menu. The next price change will update one copy and leave the other behind. Keep facts in the documents and the shelf. Keep the procedure as steps.

Loading a skill spends context, the same way loading a note does. Load the procedure the question needs. Leave the others on disk. The catalog of names can sit in the brief; the body arrives through the tool.

The restock procedure appears again in the last tutorial. The same idea is at work: a skill names the steps, and the tools and the checker still decide what is true. Chapter 7 is the book’s treatment of skills as portable procedures.

The café in these files is fictional. The guest constraint and the FAQ are practice data.

## Sources and references

- [Chapter 7: Skills as portable procedures](../../chapters/ch07-skills-as-portable-procedures/README.md), and the lab [labs/ch07-skills-as-portable-procedures](../ch07-skills-as-portable-procedures).
- The previous lecture is [5-memory.md](5-memory.md). The series map is in [README.md](README.md).
