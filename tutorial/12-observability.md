# Tutorial 12. Observability

## Motivation

When a purchase goes wrong, you need the trace, not a guess about which tool ran. The chili-oil question from tutorial 2 is the same work as before. What it still cannot show is who acted. We add spans now, after the handoff has given you two roles worth naming, and before a ledger tries to attach a cost to a turn you cannot identify.

## What this tutorial is about

Each span has a trace id, a status, and three identities. The user is the customer on the website. The agent is the Harbor Jar seller. The actor on a tool span is the tool. The root span is the turn. Secret-shaped values are not copied into the JSON.

## How you will get there

The notebook defines `span_status`, then `make_span`, then `root_span`, and registers the two hooks before the run. The Ohio question runs again with a trace id. You read the spans. Every span names the customer and the seller. At least one span has a tool actor. The answer is still grounded in the catalog and the shipping topic. The canary string is absent.

## Additional things

A span is a record of what the harness did, not a new permission. Tutorial 13 hangs a token ledger on the same loop, so cost and identity share one run. Tutorials 13 and 15 register these same hooks so a standalone run still records who acted. The store in these files is fictional. Do not put a real address or a real card into a span.

## Sources and references

- `span_status`, `make_span`, and `root_span` are defined in [12-observability.ipynb](12-observability.ipynb). `make_span` and `root_span` are registered on `HOOKS` there. The loop that records them is [common/loop.py](common/loop.py). Tutorials 13 and 15 register the same hooks in their notebooks.
- The previous lecture is [11-multi-agent.md](11-multi-agent.md). The notebook is [12-observability.ipynb](12-observability.ipynb). The series map is in [README.md](README.md).
