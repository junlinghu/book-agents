# Tutorial 1. Using a tool

## Motivation

This series builds one seller for the fictional Harbor Jar, a small-batch shop of preserves, olive oils, spice blends, and gift boxes. The person in the chat is a customer on the store website. The agent answers support questions and helps the customer buy. Each tutorial keeps what the agent can already do and adds one capability, until the last notebook can walk a customer from a recommendation to a checked cart and an order note a person has approved. We are at the start of that path. What we have is a language model that can read a short brief and a question, then write a paragraph. What we do not yet have is any way for that paragraph to depend on a document the store actually keeps. The model can sound ready to help. It cannot open the policy, and it cannot wait until a written rule has been placed in front of it.

The first question a customer might ask makes that limit concrete. They opened a jar of fig jam and want to know if it can come back. The store's answer lives in the returns section, which says that opened jars are final sale. If the model replies from the habits it picked up in training, the customer still hears a finished paragraph, and the policy file never enters the conversation. We add a tool at this first step, before the catalog, the loop, or any later check, because every later lesson uses the same division of work. The model may ask for a fact. The program around the model is what goes and gets it, and the model writes the answer only after that fact has come back.

## What this tutorial is about

This tutorial is tool use in its smallest form. A tool is a named action your program can perform. Here the action is looking up one store rule by topic: returns, shipping, damage, discounts, hours, allergens, or gifts. The model names the topic. It does not name a file. You tell the model the name of the action and a short description of when to use it. The model may then request the action. It does not carry the action out. Your program does that, places the text of the rule back into the conversation, and asks the model once more to write the answer from that text.

By the time you finish the notebook, you should be able to keep three moments separate. The request is the model asking for the returns rule. The result is the returns section your program read from the policy. The answer is the paragraph written afterward, and that paragraph should say that an opened jar is final sale because the policy says so.

## How you will get there

The notebook registers that one tool and asks the return question in the customer's voice. On the first call, the model requests the lookup. The program reads the returns section and sends the text back. On the second call, the model writes the answer from what came back. You run the notebook from top to bottom and read the printed result beside the policy, so the rule and the answer are visibly the same passage.

The hands-on steps are in the notebook and in the series guide. The notebook calls the Chat Completions API, so `OPENAI_API_KEY` has to be set (a repository-root `.env` locally, or a Colab secret of the same name).

## Additional things

The description you attach to a tool is part of the tool. The model chooses among the actions you offered by reading the name and the description. A vague description invites a guess, and a guess is how a confident paragraph gets ahead of the file.

A model may also skip the tool and answer at once. When that happens, the record of the run shows no tool result. Treat the paragraph as an answer that never consulted the store, however sure it sounds.

This tutorial stops after a single round trip. Tutorial 2 adds the catalog beside this lookup and places both inside a loop that can take several steps and that knows when to stop. A prompt with no tool at all would answer from the brief. This notebook refuses that shortcut by reading the policy first.

The store in these files is fictional. The lookup reads one section under `docs/` in this folder. The model names a topic. Leave private files alone.

## Sources and references

- The returns section is read from [docs/policy.md](docs/policy.md). The model passes the topic `returns`. The path jail in [common/read_file.py](common/read_file.py) stays inside the lookup. It is not a Chat Completions tool. The lookup is registered through [common/tools.py](common/tools.py) from [common/facts.py](common/facts.py).
- API settings live in [common/client.py](common/client.py). Live calls use the [OpenAI Chat Completions API](https://platform.openai.com/docs/api-reference/chat).
- The notebook is [1-using-tool.ipynb](1-using-tool.ipynb). The series map and the run commands are in [README.md](README.md).
