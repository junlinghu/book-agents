# Tutorial 13. Cost and latency

## Motivation

The seller can now leave a trace that names the customer, the agent, and the tool. What it still cannot do is say what that turn cost, how long it took, or whether a second lookup of the same topic did any new work. A loop that hides its usage will surprise you in the second week, and a loop that looks up the same topic on every step spends both time and money on a fact it already holds. We add a small ledger and a saved copy of read-only results now, after the trace exists to attach them to, and before a multi-step purchase runs long enough for the totals to matter.

## What this tutorial is about

Every model call appends prompt tokens, completion tokens, and latency. A short function turns those rows into an illustrative dollar figure. The rates live in code so you can see the arithmetic. They are not an invoice. Read-only tools are cached by name and arguments. The first lookup of a topic is a miss. The second identical lookup is a hit. The tool still returns the same text. A third identical call would trip the repeated-call stop from tutorial 2.

`route_task` prints whether the question looks like a short customer question or a guided purchase. Both routes name the same model in this lab. Swapping the id is a change to `MODEL`, not a second client.

## How you will get there

The notebook registers the tutorial 12 span hooks so the hours run still records who acted. The customer asks for pickup hours and asks for the hours topic twice. You should see a miss and then a hit, a ledger with totals and an illustrative cost, and the spans from tutorial 12 still on the run.

## Additional things

A cache is a copy of a read. It is not a new source of truth. If the policy file changes, the cached string is stale until you clear it. This notebook clears the cache at the start of the run. Tutorial 14 adds a plan step in front of the loop. That plan call is another model call, and tutorial 15's ledger can include it.

The store in these files is fictional.

## Sources and references

- The ledger and the cache are in [common/cost.py](common/cost.py). The span hooks registered in this notebook are the ones defined in [12-observability.ipynb](12-observability.ipynb).
- The previous lecture is [12-observability.md](12-observability.md). The notebook is [13-cost-latency.ipynb](13-cost-latency.ipynb). The series map is in [README.md](README.md).
