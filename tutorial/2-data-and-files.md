# Tutorial 2. Shop data and files

## Motivation

Tutorial 1 gave the agent one capability. It can request a single shop rule and answer from the text that comes back, so staff can tell a guest that opened coffee is final sale and that sentence has a source. What the agent still cannot do is answer the questions that actually run a counter. Staff ask which items are running low. Staff ask whether a guest’s carton of milk can be shipped. The policy lookup from the first tutorial does not hold a shelf count, and a count does not hold the shipping rule. We add the shop’s documents and the shelf now, while the agent still takes one exchange at a time, so that later lessons have real shop facts to loop over, check, and record.

## What this tutorial is about

This tutorial places two further readings beside the policy lookup you already have. One reads a shop document, either the policy or the frequently asked questions, and only from the folder those documents live in. The other reads the shelf, a small database of what is on hand. Both report the shop and leave it unchanged. The model still only requests them. The program around the model still carries the request out and returns the text.

Three habits in this notebook stay with the series. The document tool remains inside the shop folder, and a request that tries to climb out comes back as an error the model can read. The shelf tool accepts a plain question, such as which items are low, while the program chooses the database statement. The model names the question and never supplies the statement itself. One reply may need both tools, and that is a normal turn. You will also learn the shop’s meaning of low stock. An item is low when the amount on hand has fallen to the reorder point or below it. How many units would fill the shelf back up to its target is a different number. This lesson keeps the two apart, so that a later restock does not treat “we are low” as if it were already “order this many.”

## How you will get there

The notebook keeps the return-rule tool and registers the document tool and the shelf tool. Staff ask which items are low, and whether oat milk can ship to a guest. The model requests the tools. The program reads the allowed file and the shelf, and the model writes an answer from those results. Oat milk is on the shelf. The policy says the café does not ship milk, or anything that needs refrigeration, so the shipping sentence has a document behind it and the count has a shelf row behind it.

You compare the printed answer with the document and the shelf, so a number or a shipping rule has a source you can point to. The return question from tutorial 1 still runs at the end of the notebook, which lets you see the first tool survive the addition.

## Additional things

A file tool with a wide path is an open door. The path has to stay inside `docs/`. That boundary becomes urgent again in tutorial 11, when a supplier page asks the agent to read a file outside the folder.

Tutorial 3 puts these calls inside a loop, because a question at the counter often needs the shelf and then the policy before it is ready to answer. Tutorial 8 uses the gap between the target stock and the amount on hand as the quantity a restock may propose. The distinction you meet here, between “low” and “how many to order,” is what that later checker recomputes for itself.

The café in these files is fictional. The documents and the shelf live in this folder. Leave private files alone.

## Sources and references

- The path check is [common/tools.py](common/tools.py). The shop documents are [docs/policy.md](docs/policy.md) and [docs/faq.md](docs/faq.md).
- The shelf rows live in [common/shelf.py](common/shelf.py).
- The previous lecture is [1-using-tool.md](1-using-tool.md). The notebook is [2-data-and-files.ipynb](2-data-and-files.ipynb). The series map is in [README.md](README.md).
