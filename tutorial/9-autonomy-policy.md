# Tutorial 9. Who may act without asking

## Motivation

The seller can read the store, check a cart, and show that a few important answers still pass a grader. Every action so far has been a reading, or a check that changes nothing on disk. What it still cannot do is tell a reading from an action that writes a file, applies a discount, or moves money. If the sentence "please apply my code" is enough to change the price, the program has handed the decision to the wording of the request. We add a gate now, after the checker and before we trust the seller with pages that will try to demand a charge. The gate is the program's decision, in three grades: run the action, wait for a person, or refuse.

## What this tutorial is about

An FAQ lookup may run on its own. Applying a discount code waits for a person. Charging a card, canceling an order, and emailing a customer never run, even when an approval token matches that exact call. You will learn that the program decides. The wording of the customer's message does not. An approval matches one action and one set of arguments, so a different code is a different approval. Emailing a customer would send personal details, so that tool stays on the never tier. The seller does not get to promote it by asking nicely.

## How you will get there

The notebook prints the five decisions with no model in the path: hours are auto, `JAR10` waits, and charge, cancel, and email stay denied. The customer then asks to apply `JAR10` and not to charge a card. The first run prints a short approval code and does not apply the code. A second run passes that code. The discount is recorded as held. No card is charged. The catalog price is unchanged.

## Additional things

A gate that treats a polite request as permission will confirm whatever the model was persuaded to ask. Tutorial 10 is the case that makes this concrete. The origin page demands a charge and a look at a secret file. The gate refuses the charge. Tutorial 15 files an order note during the customer's visit. The note needs its own approval, because confirmation is per call. The customer's next message grants it.

The store in these files is fictional. Leave private files alone.

## Sources and references

- Cards, cancellations, and customer email use [common/autonomy.py](common/autonomy.py). The tutorial gate is [common/gate.py](common/gate.py).
- The previous lecture is [8-evals.md](8-evals.md). The notebook is [9-autonomy-policy.ipynb](9-autonomy-policy.ipynb). The series map is in [README.md](README.md).
