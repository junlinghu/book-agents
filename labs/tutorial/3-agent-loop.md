# Tutorial 3. The agent loop

## Motivation

The first two tutorials ran one exchange by hand: the model spoke, the tools ran, the model spoke again. A question at the counter is often longer than that. The concierge may need the shelf, then the policy, then another look, before it is ready to answer. If you paste those steps into the program in advance, you have written a workflow for one question. This lesson puts the exchange inside a loop, so the model can take the next step from what it just learned, and so the program still knows when to stop.

## What this tutorial is about

This lesson is the agent loop. One step is one call to the model. The model looks at the conversation so far, which is the perceiving. It decides whether it can answer or whether it needs a tool, which is the reasoning. If it requests a tool, the harness runs that tool, which is the acting. The result goes back into the conversation, which is the observation. Then the loop begins again.

You will learn the three ways this loop is allowed to end. It ends when the model answers without requesting a tool. It ends when a step limit is reached, and the harness leaves the answer unwritten. It ends when the same tool request, with the same arguments, has already been tried and is repeating. A stop is a reason you can name. It is a finished customer paragraph only when the model actually answered.

## How you will get there

The notebook keeps the document tool and the shelf tool, and wraps the exchange in the loop. You ask which items are low. That question now takes more than one model call, because the shelf result has to come back before the answer.

You then watch two runs that stop on purpose. One hits the step limit. One repeats the same call until the harness refuses to continue. In both, the program reports the stop and does not invent the rest of the reply. The hands-on steps are in the notebook [3-agent-loop](3-agent-loop.ipynb).

## Additional things

The step limit is a safety rail, not a target. A short question should finish well inside it. When a run stops at the limit, read the tool results you already have. Widening the limit hides a loop that is not making progress.

The repeated-call stop catches a model that asks for the same reading again and again. The third identical request ends the loop. If the tool is failing, the repair is the tool or the question, not another identical try.

Later tutorials add notes, memory, and checks inside this same loop. The loop stays the place where a step is taken and where a stop is recorded. Chapter 2 builds the same pattern for a single file tool. This notebook is that pattern with the shop’s shelf included.

The café in these files is fictional. The shelf matches the other labs in this book.

## Sources and references

- [Chapter 2: The Agent Loop](../../chapters/ch02-your-first-loop/README.md), and the lab [file_agent.py](../ch02-your-first-loop/file_agent.py).
- The shared stop reasons live in [labs/common/loop.py](../common/loop.py).
- The previous lectures are [1-using-tool.md](1-using-tool.md) and [2-data-and-files.md](2-data-and-files.md). The series map is in [README.md](README.md).
