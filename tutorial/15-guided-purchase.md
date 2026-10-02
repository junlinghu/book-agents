# Tutorial 15. Guided purchase

## Motivation

By the end of tutorial 14 the seller can plan a multi-step question before it acts, and the earlier lessons have never been asked to serve one customer purchase from start to finish. The seller can look up a rule, read the catalog, choose a help article, remember a constraint, and follow a written procedure. It can treat an origin page as someone else's words, check a quantity against stock, and wait for a person before writing a note. It can leave a trace that names who acted and what the turn roughly cost. What it still cannot do is stay with one customer from a recommendation through the cart, the checker, and a yes, and then file a note, without charging a card along the way. We add that conversation last. A finale that introduced a new framework would hide the lesson the series was built to show: the same tools and the same gates, in one piece of work.

## What this tutorial is about

You are the customer. The seller greets you and then waits on `You:`. You can ask for a jar you can eat, one of those jars in a cart to Ohio, a check of that cart, and an order note. The same message list is the visit. It grows when you answer. Type `bye`, `quit`, or `exit` when you want to leave.

The plan from tutorial 14 is written on the first thing you ask. The seller loads the recommend procedure, your preference, and the catalog. It calls `verify_cart`. `file_order_note` waits. The gate returns `confirm_required` and a token, and nothing is written yet. Your next message approves that call. "Yes, file the note." is enough. Pasting the token is enough. The seller calls `file_order_note` again on this same thread, with the same arguments. The note says the card was not charged. `charge_card` stays denied even if a token is offered for that exact call. A cart of 1000 jars is rejected by the checker before the model is asked, because the origin note still does not set the quantity. The page from tutorial 10 still cannot open the canary or grant a tool.

When the notebook runs with no terminal, as `nbconvert` does, nobody can type. The cell then replays three customer lines so the process can finish: Maya's request, her yes, and bye. In a terminal, in Jupyter, in VS Code, or in Colab, you type the lines yourself. The replay is the fallback. The visit is the same function either way.

## How you will get there

The notebook first scores a 1000-jar cart and walks the order note through the gate with no model in the path. Nothing is written until the token matches. The charge stays denied. It then runs the injection boundary so the canary stays out of the output. The notebook then defines `run_customer_chat`. The seller welcomes you and the chat loops until you leave. You should see the plan, the recommend procedure, the cart check, the held note, and, after you agree, the note file. The ledger and the trace travel with the visit.

## Additional things

When a step in this notebook surprises you, the repair is in the earlier tutorial that introduced that step. Confirmation is per call. A yes approves the note that was waiting. It does not approve a charge, and this seller never makes that charge. A saved recording of the run still has to show a reviewer which tool ran. The origin note's quantity stays separate from the live catalog.

A purchase that looks finished is one customer on one day. Rules written for that day go out of date. A passing score can hide a wrong answer. A long job fails in ways a short script hides. A tidy note does not settle who is responsible. The series stops at a guided purchase. It does not stop the problems.

The store is fictional. Prices, hours, and the catalog live in this folder. Leave private files alone.

## Sources and references

- The purchase workflow is [15-guided-purchase.ipynb](15-guided-purchase.ipynb). `run_customer_chat` is defined in that notebook. It keeps one message list and calls [common/loop.py](common/loop.py) once per customer line. The gate is [common/gate.py](common/gate.py). Documents are in [docs](docs), fixtures in [data](data).
- The previous lectures are [1-using-tool.md](1-using-tool.md) through [14-planning.md](14-planning.md). The series map is in [README.md](README.md).
