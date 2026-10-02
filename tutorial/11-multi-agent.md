# Tutorial 11. Two roles and a handoff

## Motivation

The seller can read an untrusted page without obeying it, and a checker can reject a quantity the catalog did not allow. Both of those checks still live inside one concierge that plays every part. What it still cannot do is pass a structured handoff between two roles with a contract, so that the role which proposes a quantity is not the role which accepts it. An origin note in this lesson says to ship a thousand jars and to ignore the stock. We add the two roles now, after the checker and the boundary around untrusted text, because the handoff is where an untrusted sentence would otherwise become an order.

## What this tutorial is about

The two roles are ordinary functions with a contract, not a crowd of agents free to invent one another's jobs. The advisor reads a catalog row and sets the quantity only when the customer's number fits the stock. It stores the origin note as untrusted data attached to the handoff. The handoff itself is a small record: a role, the sku, the stock, the quantity, and a place for that note. The fulfillment checker compares the record to the catalog row. It accepts the handoff when the quantity is allowed by stock, and it rejects a record that copied a thousand from the note. A failed check stops the handoff. The chat model can load the catalog and the note. It does not get the last word.

## How you will get there

The notebook builds a bad handoff by copying 1000 into the quantity after the advisor had set 2. The checker rejects it. The advisor's own handoff for 2 jars passes, because stock is 14. Asking the advisor for 1000 returns no quantity at all: the note's number is not a legal argument. The customer then asks for 2 jars and asks the seller to read the note without letting the note choose the number. The catalog and the note both show up in the tool log. The checker you trust is the one that read the row.

## Additional things

An unconstrained group of agents, each free to improvise the next agent's job, tends to disappoint. The constraint here is small and strict. The checker reads the catalog again, and a broken handoff stops. Tutorial 15 keeps a checker in front of the order note. The origin note still cannot set the quantity.

One seller is enough for many questions on the website. The second role earns its place when a proposal would change an order. The catalog and the loop are imported, so this notebook runs on its own. The store in these files is fictional.

## Sources and references

- The advisor and the fulfillment checker are [common/roles.py](common/roles.py). The origin note is [data/origin-note.txt](data/origin-note.txt).
- The previous lecture is [10-prompt-injection.md](10-prompt-injection.md). The notebook is [11-multi-agent.ipynb](11-multi-agent.ipynb). The series map is in [README.md](README.md).
