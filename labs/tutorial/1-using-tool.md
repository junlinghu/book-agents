# Tutorial 1. Using a tool

## Motivation

This series builds one shop agent for the fictional Hearth Lane Café. Each tutorial keeps what the agent can already do and adds a single capability, until the last notebook can plan a Tuesday restock and file the tickets a person has approved. We are at the start of that path. What we have is a language model that can read a short brief and a customer question, then write a paragraph. What we do not yet have is any way for that paragraph to depend on a document the café actually keeps. The model can sound like a person at the counter. It cannot open the policy, and it cannot wait until a written rule has been placed in front of it.

The first question a customer might ask makes that limit concrete. Someone wants to know whether an opened bag of house coffee can be returned. The shop’s answer lives in the returns section of the policy, which says that opened coffee is final sale. If the model replies from the habits it picked up in training, the customer still hears a finished paragraph, and the policy file never enters the conversation. We add a tool at this first step, before the shelf, the loop, or any later check, because every later lesson uses the same division of work. The model may ask for a fact. The program around the model is what goes and gets it, and the model writes the customer’s answer only after that fact has come back.

## What this tutorial is about

This tutorial is about tool use in its smallest form. A tool is a named action your program can perform. Here the action is looking up one shop rule: returns, shipping, hours, or allergens. You tell the model the name of the action and a short description of when to use it. The model may then request the action. It does not carry the action out. Your program does that, places the text of the rule back into the conversation, and asks the model once more to write the answer from that text.

By the time you finish the notebook, you should be able to keep three moments separate. The request is the model asking for the returns rule. The result is the returns section your program read from the policy. The answer is the paragraph written afterward, and that paragraph should say that opened coffee is final sale because the policy says so. You will also see why a careful sentence in the brief is a weaker instrument than it first appears. The brief can urge the model to consult the shop. Only the tool result puts the shop’s words where the model can read them.

## How you will get there

The notebook registers that one tool and asks the return question. On the first call, the model requests the lookup. The program reads the returns section of the shop policy and sends the text back. On the second call, the model writes the answer from what came back. You run the notebook from top to bottom and read the printed result beside the policy, so the rule and the answer are visibly the same passage.

The hands-on steps, including how to run the scripted demonstration or a live model, are in the notebook and in the series guide. This note stays with the idea the notebook is there to make visible.

## Additional things

The description you attach to a tool is part of the tool. The model chooses among the actions you offered by reading the name and the description. A vague description invites a guess about which fact you meant, and a guess is how a confident paragraph gets ahead of the file.

A model may also skip the tool and answer at once. When that happens, the record of the run shows no tool result. Treat the paragraph as an answer that never consulted the shop, however sure it sounds. The skip is easier to notice when the program allows it to happen and then shows you an empty record, which is the behavior this lesson keeps.

This tutorial stops after a single round trip. Tutorial 2 gives the agent the shop’s documents and the shelf, because a return rule is only one kind of fact. Tutorial 3 places the same exchange inside a loop that can take several steps and that knows when to stop. Much later, the series puts a gate in front of actions that change the shop, so that reading a rule and charging a card are different kinds of permission. If you want the comparison with a prompt and no tool at all, Chapter 1 asks a question of the same kind and lets the model answer from the brief alone.

The café in these files is fictional. Point the tool at the shop documents in this repository, and leave private files alone.

## Sources and references

- [Chapter 1: What an Agent Is](../../chapters/ch01-what-an-agent-is/README.md) asks the café question with a prompt alone. The lab is [hello_concierge.py](../ch01-what-an-agent-is/hello_concierge.py).
- [Chapter 2: The Agent Loop](../../chapters/ch02-your-first-loop/README.md) develops the program around the model, the tool result, and the reasons a run may stop. The shared loop is [labs/common/loop.py](../common/loop.py). The policy this tutorial reads lives in [labs/ch02-your-first-loop/docs](../ch02-your-first-loop/docs).
- [Chapter 4: Tools and Sensors](../../chapters/ch04-tools-and-sensors/README.md) treats tools as the way an agent touches the shop. The lab folder is [labs/ch04-tools-and-sensors](../ch04-tools-and-sensors).
- The notebook is [1-using-tool.ipynb](1-using-tool.ipynb). The series map and the run commands are in [README.md](README.md).
