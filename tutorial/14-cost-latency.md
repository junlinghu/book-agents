# Tutorial 14. Cost, time, and a repeated read

## Motivation

The agent can now leave a trace that names the user, the agent, and the tool. What it still cannot do is say what that turn cost, how long it took, or whether a second read of the same document did any new work. A loop that hides its usage will surprise you in the second week, and a loop that re-reads the same file on every step spends both time and money on a fact it already holds. We add a small ledger and a saved copy of read-only results now, after the trace exists to attach them to, and before the shop manager runs a restock long enough for the totals to matter.

## What this tutorial is about

The ledger sums three kinds of usage and an illustrative cost. The first two are the amount of text sent to the model and the amount of text that came back, counted in the small pieces a model provider bills, usually called tokens. The third is how long the calls took. The dollar figure in the notebook is for teaching. It is an invoice from no one, and you should read current prices before you budget with it. Usage belongs on the trace next to the answer, including a run that fails or stops partway, because a partial run still spent the call.

A cache keeps the result of a read-only tool, keyed by the tool together with its arguments. The first read misses and does the work. The second identical read hits and reuses the saved result. A ticket write is not cached, because a write is not a reading you can safely replay from a saved copy. The notebook also records which class of question it thinks it has, a short lookup or a shop decision, and which model it would have chosen. This lab still calls one model. The log shows the decision so you can see it before you add a second one.

## How you will get there

The notebook is staff looking up the café’s hours for a guest at the counter. The route for that question is recorded as a short lookup on the model named in `common/client.py`. The agent reads the frequently asked questions, and the run reads that file a second time inside the same loop. You should see a miss and then a hit, a ledger with totals and an illustrative cost, and the hours taken from the document, including the day the café is closed. The spans from tutorial 13 are still on the run, so cost and identity share one record.

## Additional things

The second read is also the repeated-call situation from tutorial 3. The cache can serve the file on that second request. A third identical call would stop the loop. Saving a result does not repeal the stop. It only keeps the second read from doing the work again.

Swapping the model is a change to `MODEL` in `common/client.py`. A model change is the wrong repair when the surrounding program is what failed. Report cost and time for the finished task, and prefer an honest total over a number that flatters the run. The café in these files is fictional.

## Sources and references

- The ledger and the read cache are [common/cost.py](common/cost.py).
- The default model id lives in [common/client.py](common/client.py). The model card is the [OpenAI gpt-4.1-mini documentation](https://developers.openai.com/api/docs/models/gpt-4.1-mini).
- The previous lecture is [13-observability.md](13-observability.md). The notebook is [14-cost-latency.ipynb](14-cost-latency.ipynb). The series map is in [README.md](README.md).
