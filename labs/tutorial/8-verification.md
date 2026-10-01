# Tutorial 8. Checking a proposal

## Motivation

The agent can read the shop, follow a procedure, and quote a supplier page as a claim someone else made. It can also sound sure while the quantity is wrong. A note or a page can say to order a thousand units, and a fluent paragraph will repeat the number. What the agent still cannot do is separate the proposal from a check that recomputes the quantity for itself. We add that checker now, before we grade the agent and before we let it write anything down, because a restock that files a ticket should already know which proposals the checker will accept.

## What this tutorial is about

This tutorial splits proposing from checking. The checker is a second step, with the rules written in the program rather than left to the model’s confidence. It loads the shelf row itself. The quantity it accepts is the gap between the target stock and the amount on hand. Dairy and bakery stay in the shop: a proposal that asks to ship them fails, and so does a proposal that cites nothing. You will see a bad proposal rejected and a good one accepted before the model is involved, and you will then see the agent call the same checker as a tool. The plan you trust is the one the checker accepted.

## How you will get there

The notebook first scores two oat-milk proposals with no model in the path. One orders a thousand cartons, asks to ship them, and cites nothing. The checker rejects it, and the findings name both the shipping rule and the missing citation. One uses the shelf gap, does not ask to ship, and cites the inventory. The checker accepts it. The agent then proposes an oat-milk restock and calls the checker. The printed answer is the proposal the checker accepted. The record shows that the shelf was read, and that the checker ran as its own step.

## Additional things

A checker that trusts the proposer’s arithmetic is a second copy of the proposal. The value of this one is that it recomputes the gap from the database you met in tutorial 2, where “low” and “how many to order” were kept apart. Tutorial 12 gives the same split to two roles, a stocker and a checker, and a supplier note that says to order a thousand bags fails there for the same reason. Tutorial 15 uses the checker on the house-blend and oat-milk gaps before any ticket is written.

A separate checker, a failure that stops the work, and a person who joins only when the checker asks are the whole of the check in this lesson. The café in these files is fictional.

## Sources and references

- The checker is [cell_src/verify.py](cell_src/verify.py).
- The previous lecture is [7-web-browse.md](7-web-browse.md). The notebook is [8-verification.ipynb](8-verification.ipynb). The series map is in [README.md](README.md).
