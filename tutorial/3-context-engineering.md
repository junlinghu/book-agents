# Tutorial 3. Context engineering

## Motivation

The seller can now look up a rule and a catalog row, and it can take more than one step. What it still cannot do is tell a title from a body. A help folder that is pasted in full on every turn spends the context window on articles the customer did not ask about, and one of those files is long on purpose. We add a catalog of titles now, and we load a body only when the question needs it, before memory and procedures, because later lessons should inherit the habit of leaving unused text on disk.

## What this tutorial is about

The prompt holds ids, titles, and sizes. `read_help_article` returns one body. The model passes an article id from that list, not a filesystem path. A body over the cap returns an error. `preserving-mega-guide` is the file that is over the cap. `opened-jars` is short enough to load. Pasting every article at once is larger than the cap for one article, which is the point of the budget: length is not authority.

## How you will get there

The notebook prints the list, refuses the mega-guide, and loads the short article, with no model in that first check. A customer then asks what the short help article says about an opened jar. The answer should come from `opened-jars`, and the mega-guide should stay unread.

## Additional things

A title in the prompt is a promise that the body exists, not a substitute for reading it. Tutorial 5 will make the same split for a procedure: the skill file is loaded when the question matches, and it is not pasted into every brief. The store documents and the catalog from tutorial 2 are still the sources for rules and stock. A help article that disagrees with the policy is the file you correct. It is not a second policy.

The articles in this folder are fictional practice text.

## Sources and references

- The articles are in [data/help](data/help). The tools are in [common/articles.py](common/articles.py).
- The previous lecture is [2-tools-and-loop.md](2-tools-and-loop.md). The notebook is [3-context-engineering.ipynb](3-context-engineering.ipynb). The series map is in [README.md](README.md).
