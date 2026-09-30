# Tutorial 1. Tool calling

## Motivation

A shop agent that answers from habit will invent the return rule. The customer hears a finished paragraph, and the policy file stays closed. That is the failure this tutorial exists to repair. Before an agent can help run a shop, it needs a way to ask for a fact the shop actually wrote down, and to wait for that fact before it speaks.

## What this tutorial is about

This lesson is about tool calling. A tool is a named action your program can perform, such as reading one section of the shop policy. The language model may request that action. It does not perform the action itself. The program around the model, called the harness, carries the request out and places the result back where the model can read it.

You will learn to tell those two moments apart. You will see a request for the return rule, the text the harness returns, and an answer written from that text. You will also see why a shop rule in the reply has to come from the tool result. A careful sentence in the prompt still leaves the file closed.

## How you will get there

The notebook registers one tool and asks a question a customer might ask at the counter: whether an opened bag of coffee can be returned. The model requests the tool. The harness reads the returns section of the shop policy and sends that text back. A second call to the model writes the answer from what came back.

You will run that exchange from top to bottom and read the printed result beside the policy text. The hands-on steps are in the notebook [1-using-tool](1-using-tool.ipynb).

## Additional things

The description you give a tool is part of the tool. The model chooses from the name and the description. A vague description invites a guess about which fact you meant.

A model may also skip the tool and answer from habit. When that happens, the record of the run shows no tool result. Treat that as a failed answer, even if the paragraph sounds sure.

This tutorial stops at one round trip. Later lessons add the shelf, a loop that can take several steps, and gates on actions that change the shop. Chapter 1 asks a question of the same kind with only a prompt, so you can compare a bare reply with a reply that had a document behind it.

The café in these files is fictional. Point the tool at the shop documents in this repository. Leave private files alone.

## Sources and references

- [Chapter 1: What an Agent Is](../../chapters/ch01-what-an-agent-is/README.md), and the lab that answers with a prompt alone, [hello_concierge.py](../ch01-what-an-agent-is/hello_concierge.py).
- [Chapter 2: The Agent Loop](../../chapters/ch02-your-first-loop/README.md). The shared loop lives in [labs/common/loop.py](../common/loop.py).
- [Chapter 4: Tools and Sensors](../../chapters/ch04-tools-and-sensors/README.md), where tools become the way an agent touches the shop.
- [OpenAI’s function calling guide](https://developers.openai.com/api/docs/guides/function-calling), the public overview of how a model requests a tool and how your application returns the result.
- The series map is in [README.md](README.md).
