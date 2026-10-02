# Tutorial 15. Guided purchase

## Motivation

By the end of tutorial 14 the seller can plan a multi-step question before it acts, and the earlier lessons have never been asked to serve one customer purchase from start to finish. The seller can look up a rule, read the catalog, choose a help article, remember a constraint, and follow a written procedure. It can treat an origin page as someone else's words, check a quantity against stock, and wait for a person before writing a note. It can leave a trace that names who acted and what the turn roughly cost. What it still cannot do is carry one customer from a recommendation through the cart, the checker, and the approval to a filed note, without charging a card along the way. We add that workflow last. A finale that introduced a new framework would hide the lesson the series was built to show: the same tools and the same gates, in one piece of work.

## What this tutorial is about

A customer named Maya asks for one path. Recommend a jar she can eat. Put one of those jars in a cart to ship to Ohio. Check the cart. File an order note. Do not charge her card.

The run starts with the plan from tutorial 14. It loads the recommend procedure, her preference, and the catalog. It calls `verify_cart`. `file_order_note` waits for a person. A second run passes that approval and writes the note. The note says the card was not charged. `charge_card` stays denied even if a token is offered for that exact call. A cart of 1000 jars is rejected by the checker before the model is asked, because the origin note still does not set the quantity. The page from tutorial 10 still cannot open the canary or grant a tool.

## How you will get there

The notebook first scores a 1000-jar cart and walks the order note through the gate with no model in the path. Nothing is written until the token matches. The charge stays denied. It then runs the injection boundary so the canary stays out of the output. It runs Maya's question once without approvals. You read the plan, the tools, and the approval code. No order file exists yet. It runs the same question again with that approval. The note file appears, and it still says the card was not charged. The ledger and the trace travel with the run.

## Additional things

When a step in this notebook surprises you, the repair is in the earlier tutorial that introduced that step. Confirmation is per call. A note and a charge are different decisions, and this seller never makes the second one. A saved recording of the run still has to show a reviewer which tool ran. The origin note's quantity stays separate from the live catalog.

A purchase that looks finished is one customer on one day. Rules written for that day go out of date. A passing score can hide a wrong answer. A long job fails in ways a short script hides. A tidy note does not settle who is responsible. The series stops at a guided purchase. It does not stop the problems.

The store is fictional. Prices, hours, and the catalog live in this folder. Leave private files alone.

## Sources and references

- The purchase workflow is [15-guided-purchase.ipynb](15-guided-purchase.ipynb). It composes the helpers in [common](common), the documents in [docs](docs), the fixtures in [data](data), and the gate in [common/gate.py](common/gate.py).
- The previous lectures are [1-using-tool.md](1-using-tool.md) through [14-planning.md](14-planning.md). The series map is in [README.md](README.md).
