# Tutorial 3. The agent loop

## Motivation

After the first two tutorials, the agent can answer a shop question from a source you can point to. It can look up a return rule, read a shop document, and read the shelf, and a shipping sentence can come from the policy while a count comes from the database. Those tutorials still run the exchange by hand. The model speaks, the tools run, and the model speaks again, in an order the notebook wrote down in advance. A question from staff at the counter is often longer than one exchange. The concierge may need the shelf, then the policy, and then another look, before it is ready to answer staff. What the agent still cannot do is choose the next step from what it just learned, or stop for a reason you can name. If you paste the steps into the program ahead of time, you have written a script for one question. We add the loop now, before notes, memory, and checks, because every later tutorial takes its steps inside this same loop.

## What this tutorial is about

This tutorial is the agent loop. One step is one call to the model. The model looks at the conversation so far, which is the perceiving. It decides whether it can answer or whether it needs a tool, which is the reasoning as this book uses that word: the choice you can see in the reply. If it requests a tool, the program around the model runs that tool, which is the acting. The result goes back into the conversation, which is the observation. Then the loop begins again. The four moments are a teaching order for one turn. They are one program, and the program is what calls the model, opens the file, and keeps the bookkeeping.

You will learn the three ways this loop is allowed to end. It ends when the model answers without requesting a tool. It ends when a step limit is reached, and the program reports the stop and leaves the reply for staff unwritten. It ends when the same tool request, with the same arguments, has already been tried and is repeating. A stop is a reason you can name. The run becomes a finished reply for staff only when the model actually answered.

## How you will get there

The notebook keeps the document tool and the shelf tool, and it wraps the exchange in the loop. Staff ask which items are at or below their reorder point, and whether oat milk may be shipped to a guest. That question now takes more than one model call. The shelf result has to come back before the policy is useful, and the policy has to come back before the answer can say that the café does not ship oat milk.

You then watch two runs that stop on purpose. One is given a step limit too small to finish, and the program reports that it reached the limit. One asks for the low-stock list again until the same call repeats, and the program refuses to continue. In both runs you can read the reason for the stop. The program does not fill in the rest of the reply.

## Additional things

The step limit is a safety rail. A short question should finish well inside it. When a run stops at the limit, read the tool results you already have. Widening the limit, on a loop that is not making progress, only postpones the same stop.

The repeated-call stop catches a model that asks for the same reading again and again. The third identical request ends the loop. When the tool is failing, the repair is the tool or the question. Another identical try will meet the same stop.

Later tutorials add notes, memory, a checker, and a gate inside this same loop. The loop remains the place where a step is taken and where a stop is recorded. This notebook is that pattern with the shop’s shelf included. Tutorial 14 meets the repeated-call stop again: a cached second read of the same document is still a repeated request if the model asks a third time.

The café in these files is fictional. The shelf is the seed in this folder.

## Sources and references

- `run_agent` in [3-agent-loop.ipynb](3-agent-loop.ipynb) stops on `final`, `max_steps`, or `repeated_call`.
- The previous lectures are [1-using-tool.md](1-using-tool.md) and [2-data-and-files.md](2-data-and-files.md). The series map is in [README.md](README.md).
