# Tutorial 14. Cost, time, and a repeated read

## Motivation

The agent can now leave a trace that names the user, the agent, and the tool. What it still cannot do is say what that turn cost, how long it took, or whether a second read of the same document did any new work. A loop that hides its usage will surprise you in the second week, and a loop that re-reads the same file on every step spends both time and money on a fact it already holds. We add a small ledger and a saved copy of read-only results now, after the trace exists to attach them to, and before the shop manager runs a restock long enough for the totals to matter.

## What this tutorial is about

The ledger sums three kinds of usage and an illustrative cost. The first two are the amount of text sent to the model and the amount of text that came back, counted in the small pieces a model provider bills, usually called tokens. The third is how long the calls took. The dollar figure in the notebook is for teaching. It is an invoice from no one, and you should read current prices before you budget with it. Usage belongs on the trace next to the answer, including a run that fails or stops partway, because a partial run still spent the call.

A cache keeps the result of a read-only tool, keyed by the tool together with its arguments. The first read misses and does the work. The second identical read hits and reuses the saved result. A ticket write is not cached, because a write is not a reading you can safely replay from a saved copy. The notebook also records which class of question it thinks it has, a short lookup or a shop decision, and which model it would have chosen. This lab still calls one model. The log shows the decision so you can see it before you add a second one.

## How you will get there

The notebook asks for the café’s hours. The route for that question is recorded as a short lookup on the same model the other labs use. The agent reads the frequently asked questions, and the scripted run reads that file a second time inside the same loop. You should see a miss and then a hit, a ledger with totals and an illustrative cost, and the hours taken from the document, including the day the café is closed. The spans from tutorial 13 are still on the run, so cost and identity share one record.

## Additional things

The second read is also the repeated-call situation from tutorial 3. The cache can serve the file on that second request. A third identical call would stop the loop. Saving a result does not repeal the stop. It only keeps the second read from doing the work again.

Choosing a different model is the change Chapter 3 isolates, and Chapter 15 discusses when a model change is the wrong repair for a problem in the surrounding program. Chapter 14 asks you to report cost and time for a finished task, and to prefer an honest total over a number that flatters the run. Chapter 24 is the book’s wider discussion of cost, delay, and the shape of the system. The café in these files is fictional.

## Sources and references

- [Chapter 14: Production Signals and Honest Metrics](../../chapters/ch14-production-signals-and-honest-metrics/README.md), and the lab [labs/ch14-production-signals-and-honest-metrics](../ch14-production-signals-and-honest-metrics).
- [Chapter 24: Cost, latency, and architecture](../../chapters/ch24-cost-latency-and-architecture/README.md), and the lab [labs/ch24-cost-latency-and-architecture](../ch24-cost-latency-and-architecture).
- [Chapter 3: Local and Hosted Models](../../chapters/ch03-models-without-the-pain/README.md) is the place where swapping the model is the only change.
- The previous lecture is [13-observability.md](13-observability.md). The notebook is [14-cost-latency.ipynb](14-cost-latency.ipynb). The series map is in [README.md](README.md).
