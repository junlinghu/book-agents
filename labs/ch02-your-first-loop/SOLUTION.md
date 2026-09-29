# Solutions — Lab 2. Your first loop

For instructors, or for a self-check after you have finished the write-up. Do not read this before the lab if you are using it as homework.

The corpus is [`docs/policy.md`](docs/policy.md) and [`docs/faq.md`](docs/faq.md). Score a citation by opening the file, not by the presence of the substring `docs/`. The soft `NOTE:` only checks that substring.

Delivery fees are in `policy.md` only. The FAQ does not restate them. Hours, including the closed day, are in `faq.md`. The Wi-Fi password is in neither file.

## Expected outcomes

### Default question

> I opened a bag of your house coffee and they're not for me. Can I return them? Also, can you ship a cardamom bun to another state?

A grounded answer says both of the following and cites `docs/policy.md` on each:

- Opened coffee is final sale. Returns: "Opened coffee, ground coffee, pastries, drinks, and any food that has left the counter are final sale."
- A cardamom bun cannot be shipped. Shipping: "The café does not ship pastries, drinks, milk, or anything that needs refrigeration."

The trace should include `read_file` of `policy.md` before those claims. Reading `faq.md` as well is fine. The return and shipping rules are in `policy.md`.

Do not accept the unopened-coffee rule applied to an opened bag. Unopened retail coffee (bag valve seal intact) may be returned within 14 days of purchase, with a paper or email receipt, as store credit on a Hearth card only. The café does not give cash refunds. That rule is the same Returns section, and it does not cover an opened bag.

### Optional: local delivery and closed day

> How much is local delivery, and which day are you closed?

- Delivery, from `docs/policy.md` (Local delivery): fee $4.50; orders of $35 or more are delivered free; window Tuesday–Friday, 8:00–14:00; addresses within 3 miles of 12 Hearth Lane, North Mill. No local delivery on Saturday, Sunday, or Monday. A delivery-fee answer has to read `policy.md`. The FAQ tells the reader that the fee lives only in `policy.md`.
- Closed day, from `docs/faq.md` (Where and when): closed Monday, all day, including when a holiday falls on Monday. Hours are Tuesday–Friday 7:30–15:30 and Saturday–Sunday 8:00–16:00. A "which day are you closed?" answer has to read `faq.md`.

`policy.md` also says coffee orders do not ship on Monday because the café is closed. That sentence supports "no Monday shipping." It is not the hours table. Citing only that line for the closed-day question is incomplete. Citing the delivery window's "no local delivery on Monday" is also incomplete for "which day are you closed?"

### Optional: Wi-Fi password

> What's the Wi-Fi password?

A grounded answer reads `docs/faq.md` and reports the guest network name `hearth-guest`. The password is not in the file. The FAQ says it is printed on the paper receipt and says not to invent one. An invented password is a miss even when the path is cited.

### Optional: live crabs

> Do you sell live crabs?

Neither file mentions live crabs or any crab item. The model should say it does not know, or that the documents do not say. A made-up menu item is a miss.

### Empty tool log

`final` after 1 model call with an empty trace means the model never called `read_file`. Shop facts in that answer were not read from `docs/`. That is a model miss, including when the prose happens to match the files. The harness does not send `tool_choice`, because Ollama's compatible API does not support that field. The remedy is a different `MODEL` (`llama3.1` after `ollama pull llama3.1`, or a Groq / OpenRouter id with local tool calls), not a different question, and not an edit to the loop for this lab.

### Checks without a model

Path jail, from the repo root:

```bash
python -c "from labs.common.tools import read_file; from pathlib import Path; print(read_file(Path('labs/ch02-your-first-loop/docs'), '../.env'))"
```

Expect this line, and nothing from `.env`:

```text
ERROR: path must stay inside docs/. Example: policy.md
```

`read_file` in `labs/common/tools.py` returns an `ERROR:` string for `..`, absolute paths, hidden names, and symlinks that resolve outside `docs/`. It does not raise. The same rejection covers `/etc/passwd`, `docs/../../.env`, and `policy.md/../../.env`.

Stop conditions and the jail, without a server:

```bash
python -m unittest labs.common.test_harness
```

Expect a run that finishes `OK` with no failures. The module covers the docs path jail, tool-error handling, the max-steps stop, the repeated-call stop, and `max_tokens`. It does not contact Ollama or a hosted API.

## How to score

| Result | Grade it as |
|---|---|
| Claims match the file quoted, trace shows that file was read, stop tag is `final` | Full credit for that question |
| Prose matches the shop, tool log is empty | Miss. The facts were not read on this run |
| Path cited, file does not support the sentence | Miss. The substring `docs/` is not a citation |
| Delivery fee cited only to `faq.md` | Miss. The fee is not in the FAQ |
| Closed day cited only from the shipping or delivery lines in `policy.md` | Incomplete. Hours are in `faq.md` |
| Wi-Fi answer invents a password | Miss, even with `(docs/faq.md)` |
| Live-crabs answer names a price or a menu item | Miss |
| `max_steps` or `repeated_call` | Grade the trace. The harness did not write a customer answer |
| `max_tokens`, or cut-off tool-call JSON | Grade the trace. `MAX_TOKENS` in `labs/common/client.py` is 800. Raising it is a harness edit; the write-up should say so |
| `ERROR:` on `policy.md` or `faq.md` for a normal question | Model path error, or a missing `docs/` directory in the checkout |
| Unittest or path-jail output missing | Fine when those steps were optional. When they were turned in, the jail line must be the `ERROR:` above and the unittest summary must be `OK` |

`NOTE:` lines are hints for the student. They do not rewrite the answer, and they are not themselves the grade.
