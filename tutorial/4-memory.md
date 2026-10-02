# Tutorial 4. Session and durable memory

## Motivation

The loop can answer from the store's files. The message list that holds those answers is one chat. When the customer closes the tab, that list is gone. Maya is a returning customer. She is allergic to sesame, her favorite is Calabrian chili oil, and her last order was one jar of that oil. A new chat that has never heard her name still has to know those facts, and it has to know them as hers. Jonah's last order is a Harbor gift box. His entry must not leak into Maya's turn, and her allergy must not rewrite the catalog. We add one shared preference file now, before a recommendation procedure tries to use it.

## What this tutorial is about

Session memory is the message list. Durable memory is `data/customer_preference.md`. Both sample customers use the same fields: Name, Allergy, Favorite, Last order, Notes. `get_preference` takes a name, not a filename, and returns that heading only. The policy and the catalog stay where tutorials 1 and 2 put them. A preference file that also stored the return rule would go stale beside `get_store_fact`.

## How you will get there

The notebook prints both entries so you can see the shared fields. It then starts a fresh `run_agent` for Maya. The message list contains only this question. Her allergy and last order still come back from the file. A second `run_agent` starts empty again and asks for Jonah's last order. Nothing Maya said is in that list.

## Additional things

An allergy on file applies to that customer. The store still sells sesame crunch. Tutorial 5 uses Maya's entry as an input to a recommendation procedure, and the allergen topic remains the source for what a jar contains. The customers in this file are fictional.

## Sources and references

- The preference file is [data/customer_preference.md](data/customer_preference.md). The tool is [common/memory.py](common/memory.py).
- The previous lecture is [3-context-engineering.md](3-context-engineering.md). The notebook is [4-memory.ipynb](4-memory.ipynb). The series map is in [README.md](README.md).
