# Tutorial 15. The shop manager

## Motivation

By the end of tutorial 14 the concierge can do the work of a careful counter and the work of a careful buyer, and those abilities have never been asked to serve one morning. It can look up a rule, read the shelf, choose a note, remember a constraint, and follow a written procedure. It can treat a supplier page as someone else’s words, check a quantity against the shelf, and wait for a person before writing a ticket. It can leave a trace that names who acted and what the turn roughly cost. What it still cannot do is carry a Tuesday restock from the procedure through the check and the approval to the filed tickets. We add that workflow last. A capstone that introduced a new framework would hide the lesson the series was built to show: the same tools and the same gates, in one piece of work.

## What this tutorial is about

A manager asks for the low-stock restock. The run loads the restock procedure, reads which items are low, reads the policy, reads the oat-milk note, and searches shop memory. It fetches the supplier page as untrusted text. It checks the house-blend and oat-milk gaps with the checker from tutorial 8. On this shelf the gap is fourteen bags of house blend, because the target is eighteen and four are on hand, and thirteen cartons of oat milk, because the target is sixteen and three are on hand. Tickets for those two items wait for a person. A second run passes the two approvals and writes the two files. No card is charged.

You should be able to say, after the notebook, that the supplier note still cannot set the quantity and that the page still cannot grant a charge. Confirmation is per call. Two tickets need two approvals. The picnic note stays unread, because it is not about the restock. The ledger and the trace from the previous tutorials travel with the run, so the morning has a record as well as an outcome.

## How you will get there

The notebook runs the restock once without approvals. You read the answer, the tools that ran, and the two approval codes. No ticket file exists yet. The notebook then shows that a handoff which copied a thousand bags from the supplier note still fails the checker, and that the page’s demands still fail the folder boundary and the gate. It runs the same restock again with the two approvals. The ticket files appear, the quantities in them are the shelf gaps, and the answer still says that no card was charged.

## Additional things

When a step in this notebook surprises you, the repair is in the earlier tutorial that introduced that step. Wrapping the capstone in another layer would only move the surprise. A saved recording of the run still has to show a reviewer which tool ran, and a huddle note’s quantities stay separate from the live shelf. This notebook is specific about the tickets it files: they use the gap on the shelf it was given, fourteen bags of house blend and thirteen cartons of oat milk.

A morning that looks finished is one shop on one day. Rules written for that day go out of date. A passing score can hide a wrong answer. A long job fails in ways a short script hides. A tidy receipt does not settle who is responsible. The series stops at a working restock. It does not stop the problems.

The café is fictional. Prices, hours, and the shelf live in this folder. Leave private files alone.

## Sources and references

- The restock workflow is [15-shop-manager.ipynb](15-shop-manager.ipynb). It composes the helpers in [common](common), the documents in [docs](docs), the fixtures in [data](data), and the gate in [common/autonomy.py](common/autonomy.py).
- The previous lectures are [1-using-tool.md](1-using-tool.md) through [14-cost-latency.md](14-cost-latency.md). The series map is in [README.md](README.md).
