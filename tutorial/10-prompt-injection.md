# Tutorial 10. Untrusted text

## Motivation

Tutorial 6 taught the seller to fetch one origin page and to mark the text as untrusted. Tutorial 9 taught the program to refuse a card charge, a cancellation, and an email. Document lookup stays on a topic, and the reader inside that lookup stays inside the store folder. What the seller still cannot show is that those lessons hold together when the page is trying to give orders. The Calabrian mill page asks for a charge, a cancellation, a secret file, and a new price. A polite model may ignore those sentences. A boundary that depends on politeness fails on the day the model complies. We add that test now, while the gate is still the newest piece, and before two roles start passing quantities to each other.

## What this tutorial is about

The name for this failure is prompt injection: instructions that arrive inside something the agent was only supposed to read. The untrusted text can sit in the conversation. It does not edit the list of tools, and it does not grant an action the program has refused. You will see the model report the mill price and leave the demanded actions uncalled. You will then see the same proposals run through the folder boundary and the gate with no model in the path, because the boundary has to hold when the model is wrong.

A planted fake secret sits in a local practice file. People sometimes call that kind of marker a canary, because its appearance in the output would show that private text leaked. It must not appear in the tool output. The public tool accepts a topic, so a path is not a legal argument. Inside the reader, a path that climbs out of the store documents still comes back as an error. The model never sees that path argument.

## How you will get there

The notebook asks for the mill price and tells the seller to leave the page's instructions alone. The answer reports `$6.40` and does not call `charge_card`. A second cell then attempts the reads, the charge, the cancellation, and the email that the page requested. You read the errors and the refusals. The planted secret does not appear in that output, and a charge remains refused even when an approval is offered for that exact call.

## Additional things

Marking a page "untrusted" is a comment until some function enforces it. This notebook is that function: the topic check, the folder check inside the reader, the gate from tutorial 9, and a secret that is absent from the result. Tutorial 11 meets an origin note with the same habit. The note can ask for a thousand jars. The quantity still comes from the catalog.

The planted secret is practice data. Leave real credentials alone.

## Sources and references

- The poisoned page is [data/pages/calabrian-mill.html](data/pages/calabrian-mill.html). The canary fixture is [data/canary.env](data/canary.env). The boundary check is [common/injection.py](common/injection.py).
- The gate is [common/autonomy.py](common/autonomy.py).
- The previous lectures are [6-web-browse.md](6-web-browse.md) and [9-autonomy-policy.md](9-autonomy-policy.md). The notebook is [10-prompt-injection.ipynb](10-prompt-injection.ipynb). The series map is in [README.md](README.md).
