# Tutorial 5. Skills

## Motivation

The seller can read the store, loop until it has an answer or a reason to stop, choose which help article to load, and remember a customer after the chat ends. What it still cannot do is follow a procedure that lives in its own document. A standing brief that holds every procedure grows long, and it goes stale the moment a procedure changes. Recommending a jar is one procedure. Pointing a gift question at the catalog is another. Both can share the same tools. What differs is the order of the steps. We add a skill now, a written procedure loaded when the question matches, so the brief stays short and the steps stay editable.

## What this tutorial is about

`load_skill` reads a file from `data/skills`. The file is not the system prompt, and it does not run itself. `recommend` tells the seller to load the customer's preference, the allergens topic, and a catalog row before naming a jar. `gift-box` is a short stub: call `query_catalog` for the Harbor gift box and read the gifts topic. Neither file is a price list. If the skill and the catalog disagree, the catalog wins.

## How you will get there

The notebook prints the gift-box stub and checks that it names `query_catalog` and does not contain skus. A customer named Maya then asks what jar she should buy. The run should load the recommend skill, load her preference, and read the store before it answers. Sesame crunch is not the jar to sell her. Calabrian chili oil fits the favorite on her entry, once the allergen topic has been consulted.

## Additional things

A procedure that remembers a price the catalog no longer charges has become fiction. The skill should point at the tool. It should not become a second catalog. Tutorial 15 asks Maya for a full purchase and starts from this same recommend file. The store and the two customers are practice data.

## Sources and references

- The procedures are [data/skills/recommend.md](data/skills/recommend.md) and [data/skills/gift-box.md](data/skills/gift-box.md). The tool is [common/skills.py](common/skills.py).
- The previous lecture is [4-memory.md](4-memory.md). The notebook is [5-skills.ipynb](5-skills.ipynb). The series map is in [README.md](README.md).
