# Tutorial 2. Tools and the agent loop

## Motivation

After the first tutorial, the seller can answer a return question from a section you can point to. A customer question is often longer than one exchange, and a rule is only one kind of fact. "Do you have Calabrian chili oil, and can you ship a jar to Ohio?" needs a stock count and a shipping rule. The count lives in a database. The rule lives in the policy. If you paste both steps into the program ahead of time, you have written a script for one question. We add the catalog and the loop together, before help articles, memory, and checks, because every later tutorial takes its steps inside this same loop and reads this same catalog.

## What this tutorial is about

This tutorial is two tools inside the agent loop. One step is one call to the model. The model looks at the conversation so far, which is the perceiving. It decides whether it can answer or whether it needs a tool, which is the reasoning as this book uses that word: the choice you can see in the reply. If it requests a tool, the program runs that tool, which is the acting. The result goes back into the conversation, which is the observation. Then the loop begins again.

`get_store_fact` still takes a topic. The model never passes a filename. `query_catalog` reads SQLite. Each row has a sku, a name, a stock count, a price, a shippable flag, and a category. The model passes a name or a sku. The SQL stays in `read_db.py`.

You will learn the three ways this loop is allowed to end. It ends when the model answers without requesting a tool. It ends when a step limit is reached, and the program reports the stop and leaves the reply unwritten. It ends when the same tool request, with the same arguments, has already been tried and is repeating. The run becomes a finished reply only when the model actually answered.

## How you will get there

The notebook prints the Calabrian chili oil row so you can see stock 14 and that the jar is shippable. The customer then asks about stock and about shipping to Ohio. The catalog result has to come back before a count is real, and `get_store_fact` with topic `shipping` has to come back before the answer can say the jar ships to Ohio.

You then watch two runs that stop on purpose. One is given a step limit too small to finish. One asks for the shipping topic until the same call repeats. In both runs you can read the reason for the stop. The program does not fill in the rest of the reply.

## Additional things

The step limit is a safety rail. When a run stops at the limit, read the tool results you already have. Widening the limit, on a loop that is not making progress, only postpones the same stop.

The repeated-call stop catches a model that asks for the same reading again and again. The third identical request ends the loop. Tutorial 13 meets that stop again: a cached second lookup of the same topic is still a repeated request if the model asks a third time.

The store in these files is fictional. The catalog is the seed in this folder.

## Sources and references

- `run_agent` in [common/loop.py](common/loop.py) stops on `final`, `max_steps`, or `repeated_call`.
- The catalog is created in [common/get_db.py](common/get_db.py) and read in [common/read_db.py](common/read_db.py). `query_catalog` is registered from [common/catalog.py](common/catalog.py).
- The previous lecture is [1-using-tool.md](1-using-tool.md). The notebook is [2-tools-and-loop.ipynb](2-tools-and-loop.ipynb). The series map is in [README.md](README.md).
