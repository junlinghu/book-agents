# Solutions — Lab 1. Hello Concierge

For instructors, or for a self-check after you have finished the write-up. Do not read this before the lab if you are using it as homework.

## Expected outcomes

`labs/ch01-what-an-agent-is/hello_concierge.py` sends one chat completion. There is no `tools` argument. The header includes `TOOLS=none`. The process cannot open shop files. Specific shop facts in the reply came from the model.

### Default question

> I opened a bag of your house coffee and they're not for me. Can I return them? Also, can you ship a cardamom bun to another state?

The shop text this script is not allowed to read is in [`labs/ch02-your-first-loop/docs/policy.md`](../ch02-your-first-loop/docs/policy.md):

- Opened coffee is final sale. Returns: "Opened coffee, ground coffee, pastries, drinks, and any food that has left the counter are final sale."
- Pastries are not shipped. Shipping: "The café does not ship pastries, drinks, milk, or anything that needs refrigeration." A cardamom bun is a pastry, so it is not shipped.

A reply that happens to say those two rules is still not a grounded Chapter 1 answer. The program never read the file. Grade the failure modes, not whether the prose matched the shop.

The unopened-coffee rule in the same Returns section is a different case: unopened retail coffee (bag valve seal intact) may be returned within 14 days with a receipt, as Hearth card credit only, no cash. Applying that window to an opened bag disagrees with the file.

### Optional question

> What time do you open on Monday, and what's the Wi-Fi password?

This script cannot read these either. The shop text, for scoring after the run:

- Monday: the café is closed all day, including when a holiday falls on Monday. Hours are Tuesday–Friday 7:30–15:30 and Saturday–Sunday 8:00–16:00. [`labs/ch02-your-first-loop/docs/faq.md`](../ch02-your-first-loop/docs/faq.md), "Where and when."
- Wi-Fi: the guest network name is `hearth-guest`. The password is printed on the paper receipt and is not written in the FAQ. The FAQ says not to invent one. Same file, "Wi-Fi and payment." `policy.md` does not contain the password either.

## How to score

Credit a write-up that quotes the reply and labels three failure modes that are actually in it, or that says a mode did not appear and quotes what appeared instead.

| Mode | What counts | Common miss |
|---|---|---|
| Invented shop fact | A return window, fee, hour, or price the script could not look up. Quote it. | Treating a confident "30-day refund," a shipping fee for a bun, a Monday open time, or a made-up Wi-Fi password as if the program had checked it. The 14-day rule is for unopened coffee only. |
| Fake citation | The reply names `docs/policy.md`, `docs/faq.md`, or any other path. Nothing was read, so the citation is invented. | Penalizing a reply that names no path. No path is the expected shape. A path is the failure mode. |
| Action the process cannot take | An offer to refund, print a label, ship, or email. This process has no such function. | Grading the offer as a feature the lab forgot to wire up. |

**Hedge vs confident wrong.** Both are valid Chapter 1 results. A hedge ("I don't know your policy") is a different outcome from a confident wrong window. Do not mark a hedge as a fake policy. Do not mark a confident wrong answer as a refusal. The script's closing note is a checklist, not a pre-written grade of the model.

A connection error is a setup failure. Do not grade a stack trace as a concierge reply.
