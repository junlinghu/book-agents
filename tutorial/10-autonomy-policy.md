# Tutorial 10. Who may act without asking

## Motivation

The agent can read the shop, check a proposal, and show that a few important answers still pass a grader. Every action so far has been a reading, or a check that changes nothing on disk. What the agent still cannot do is tell a reading from an action that writes a file or moves money. A restock ticket writes a file. A card charge would take payment. If the sentence “please write the ticket” is enough to write it, the program has handed the decision to the wording of the request. We add a gate now, after the checker and before we trust the agent with pages that will try to demand a charge. The gate is the program’s decision, in three grades: run the action, wait for a person, or refuse.

## What this tutorial is about

Readings of the shop, the notes, the memory, the supplier page, and the checker may run on their own. Writing a restock ticket waits for a person. Charging a card is refused, and an approval that matches that exact charge does not promote it into an allowed action. You will learn that the program decides. The wording of the staff message does not. An approval matches one action and one set of arguments, so a different quantity is a different approval. The same grades cover mail. A message to the counter can wait for a person. A message to any other address is refused. This lesson uses the approval rules in `common/autonomy.py` for cards and mail.

## How you will get there

The notebook asks for an oat-milk restock ticket, as shop staff, and asks that no card be charged. The first run prints a short approval code and writes nothing. You can see the ticket waiting, and you can see that the model is still allowed to finish its answer while the file stays unwritten. A separate check then offers an approval for a card charge of that exact call, and the gate still refuses. A second run of the same ticket request passes the approval from the first run. One ticket file appears, and the record shows that the write happened after the approval matched.

## Additional things

A gate that treats a polite request as permission will confirm whatever the model was persuaded to ask. Tutorial 11 is the case that makes this concrete. The supplier page demands a charge and a look at a secret file. The gate refuses the charge. The document tool accepts a topic, and the folder boundary inside the reader refuses the path. Tutorial 15 writes two tickets, and each ticket needs its own approval, because confirmation is per call.

The three grades, the mapping of actions to risk, and an approval a person can match to one call are the whole of the gate in this lesson. The café in these files is fictional. Leave private files alone.

## Sources and references

- Cards and mail use [common/autonomy.py](common/autonomy.py). The ticket gate is [common/gate.py](common/gate.py).
- The previous lecture is [9-evals.md](9-evals.md). The notebook is [10-autonomy-policy.ipynb](10-autonomy-policy.ipynb). The series map is in [README.md](README.md).
