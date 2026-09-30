# Tutorial 13. A record of the run

## Motivation

The agent can hand work from a stocker to a checker, refuse a charge, and keep untrusted text from granting tools. When a restock goes wrong, none of that helps if the only account of the run is a paragraph and a guess about which tool ran. What the agent still cannot do is leave a record that names who asked, which agent acted, and which tool ran, in a form you can read without opening the model provider’s private logs. We add that record now, after the roles and the gate exist to be named, and before we attach cost and time to the same trace.

## What this tutorial is about

A trace is the record of one turn. A span is one step inside it. Identity is a field on that span, and the three actors are different people or programs: the user, the agent, and the tool. In this lesson the user is the counter lead and the agent is the shop concierge. A tool has its own actor, so a shelf reading is not silently attributed to the concierge. A confirmation, a refusal, or an error is a status you can see on the span. Secrets, the body of a supplier page, and raw credentials do not belong there. The customer’s answer is still grounded in the shelf and the policy. The trace explains the run. It does not replace the documents.

## How you will get there

The notebook asks the same low-stock question as tutorial 3: which products are at or below their reorder point, and whether oat milk may be shipped. The loop runs as before, and it now prints the spans. You read them and check that every span names the counter lead and the shop concierge, that a tool has its own actor, and that the answer still comes from the shelf and the policy. You also check that the trace does not carry an API key or the supplier’s planted secret from tutorial 11. The handoff roles and the gate are still in the notebook, so the new record sits on top of work you have already seen.

## Additional things

A trace that copies a tool’s full result will eventually copy a secret, because someone will point a tool at a file that contains one. Record the name, the status, and the identity. Leave the body in the tool result the model needed for that turn, and keep it out of the long-term record.

Tutorial 14 hangs token counts, an illustrative cost, and elapsed time on this same trace, including runs that stop early. Chapter 22 is the book’s treatment of actor identity, spans, and the ability to replay a run for debugging and for an audit. The café in these files is fictional.

## Sources and references

- [Chapter 22: Identity and Observability](../../chapters/ch22-identity-and-observability/README.md), and the lab [labs/ch22-identity-and-observability](../ch22-identity-and-observability).
- The previous lecture is [12-multi-agent.md](12-multi-agent.md). The notebook is [13-observability.ipynb](13-observability.ipynb). The series map is in [README.md](README.md).
