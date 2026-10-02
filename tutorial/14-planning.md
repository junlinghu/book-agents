# Tutorial 14. Planning

## Motivation

The seller can look up a rule, read the catalog, remember Maya, follow a skill, and stop when a step repeats. A question that needs several of those tools still starts by guessing the next call. For a short lookup that is enough. For "recommend a jar I can eat, and tell me if it ships to Ohio" the order matters: her allergy before the jar, the catalog before the price, the shipping topic before a promise about Ohio. We add an explicit plan now, immediately before the guided purchase, so the last notebook can follow a list you can read instead of hoping the first tool call was the right one.

## What this tutorial is about

Planning, in this lesson, is one model call that happens before any tool runs. The call is offered an empty tool list, so it cannot act while it is planning. It returns a short numbered list. Each step names a tool that is already registered and the argument it would pass. `run_agent` prints that plan, attaches it to the system message, and only then starts the perceive–reason–act–observe loop. The plan is not a second agent. It cannot add a tool, change a price, or name a card charge, a cancellation, or an email. The loop still executes only the tools the harness registered, and the gate from tutorial 9 still applies if that module is imported. This notebook does not import the gate. It shows the plan and then the tools.

## How you will get there

The customer is Maya. She asks for a jar she can eat and whether it can ship to Ohio. You read the numbered plan first, then the tool log. The plan should have more than one step. The log should show store data being read after the plan was printed. Preference is part of the work, either as a step in the plan or as a `get_preference` call. The plan text should not name `charge_card`.

## Additional things

A plan the model writes can be wrong. The loop is allowed to skip a step that does not apply, and it is not allowed to obey a step that invents a tool. If the plan and the catalog disagree, the catalog wins, just as it did for skills. Tutorial 15 turns this hook on for the full purchase, so the recommend–cart–verify–note path starts from a list.

The store and Maya's entry are practice data.

## Sources and references

- The plan step is [common/plan.py](common/plan.py). The loop that runs it is [common/loop.py](common/loop.py).
- The previous lecture is [13-cost-latency.md](13-cost-latency.md). The notebook is [14-planning.ipynb](14-planning.ipynb). The series map is in [README.md](README.md).
