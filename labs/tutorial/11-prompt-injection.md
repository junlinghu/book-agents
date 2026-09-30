# Tutorial 11. Untrusted text

## Motivation

Tutorial 7 taught the agent to fetch one supplier page and to mark the text as untrusted. Tutorial 10 taught the program to refuse a card charge and to keep document reads inside the shop folder. What the agent still cannot show is that those two lessons hold together when the page is trying to give orders. The Mill and Birch page asks the concierge to charge a card, to read a secret file, and to change the price of a bun. A polite model may ignore those sentences. A boundary that depends on politeness fails on the day the model complies. We add that test now, while the gate is still the newest piece, and before two roles start passing quantities to each other.

## What this tutorial is about

The name for this failure is prompt injection: instructions that arrive inside something the agent was only supposed to read. The untrusted text can sit in the conversation. It does not edit the list of tools, and it does not grant an action the program has refused. You will see the scripted model report the wholesale price and leave the demanded actions uncalled. You will then see the same proposals run through the folder boundary and the gate with no model in the path, because the boundary has to hold when the model is wrong.

A planted fake secret sits in a local practice file. People sometimes call that kind of marker a canary, because its appearance in the output would show that private text leaked. It must not appear in the tool output. Mail to the counter waits for a person. Mail to any other address is refused. A path that climbs out of the shop documents, or that names a file other than the policy and the frequently asked questions, comes back as an error the model can read.

## How you will get there

The notebook asks for the oat-milk case price on the supplier page, and it asks the agent to leave the page’s instructions alone. The answer reports the price and says those instructions were not carried out. A second part of the notebook then attempts the reads, the charge, and the outside mail that the page requested. You read the errors and the refusals. The planted secret does not appear in that output, and a charge remains refused even when an approval is offered for that exact call.

## Additional things

Marking a page “untrusted” is a comment until some function enforces it. This notebook is that function: the folder check from tutorial 2, the gate from tutorial 10, and a secret that is absent from the result. Tutorial 12 meets a supplier note with the same habit. The note can ask for a thousand bags. The quantity still comes from the shelf.

Chapter 21 is the book’s treatment of instructions hidden in pages, files, and database text, and of keeping secrets out of the prompt. Chapter 16 remains the source of the gate. The café is fictional, and the planted secret is practice data. Leave real credentials alone.

## Sources and references

- [Chapter 21: Prompt Injection and Untrusted Data](../../chapters/ch21-prompt-injection-and-untrusted-data/README.md), and the lab [labs/ch21-prompt-injection-and-untrusted-data](../ch21-prompt-injection-and-untrusted-data).
- The gate is [Chapter 16: Autonomy Policy](../../chapters/ch16-autonomy-policy/README.md), implemented in [labs/common/autonomy.py](../common/autonomy.py).
- The previous lectures are [7-web-browse.md](7-web-browse.md) and [10-autonomy-policy.md](10-autonomy-policy.md). The notebook is [11-prompt-injection.ipynb](11-prompt-injection.ipynb). The series map is in [README.md](README.md).
