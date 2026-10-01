# Tutorial 12. Two roles and a handoff

## Motivation

The agent can read an untrusted page without obeying it, and a checker can reject a quantity the shelf did not ask for. Both of those checks still live inside one concierge that plays every part. What it still cannot do is pass a structured handoff between two roles with a contract, so that the role which proposes a quantity is not the role which accepts it. A supplier note in this lesson says to order a thousand bags and to ignore the shelf. We add the two roles now, after the checker and the boundary around untrusted text, because the handoff is where an untrusted sentence would otherwise become an order.

## What this tutorial is about

The two roles are ordinary functions with a contract, not a crowd of agents free to invent one another’s jobs. The stocker reads a shelf row and sets the quantity to the gap between the target stock and the amount on hand. It stores the supplier note as untrusted data attached to the handoff. The handoff itself is a small record: a role, the shelf numbers, the quantity, and a place for that note. The checker compares the record to the shelf row. It accepts the handoff when the quantity is the gap, and it rejects a record that copied a thousand from the note. A failed check stops the handoff. The chat model can load the shelf and the note. It does not get the last word.

## How you will get there

The notebook asks the agent to pull the house-blend shelf row and the supplier note so the two roles can hand off. You then watch a bad handoff, built by copying the note’s quantity, fail the checker. You watch the stocker’s own handoff pass. The note is still attached, and it still asks for a thousand bags, and the checker accepts the handoff because the quantity came from the shelf. The note remains in the record as data the checker was not allowed to treat as an order.

## Additional things

An unconstrained group of agents, each free to improvise the next agent’s job, tends to disappoint. The constraint here is small and strict. The checker reads the shelf again, and a broken handoff stops. Tutorial 15 keeps that rule inside one restock. The supplier note still cannot set the quantity.

One agent is enough for many questions at the counter. The second role earns its place when a proposal would change an order. The fetch tool, the gate, and the loop are still in this notebook, so the handoff sits on top of the earlier lessons rather than replacing them. The café in these files is fictional.

## Sources and references

- The stocker and the checker are [cell_src/roles.py](cell_src/roles.py). The supplier note is [data/supplier-note.txt](data/supplier-note.txt).
- The previous lecture is [11-prompt-injection.md](11-prompt-injection.md). The notebook is [12-multi-agent.ipynb](12-multi-agent.ipynb). The series map is in [README.md](README.md).
