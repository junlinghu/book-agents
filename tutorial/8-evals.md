# Tutorial 8. A graded set

## Motivation

The seller can answer from the store's files, follow a procedure, quote a page as untrusted, and submit a cart to a checker. What it still cannot do is show, on a later day, that the answers you already care about still hold. A conversation you remember is a weak test. The moment you change the brief or the tools, you need a set of cases and a grader that looks at the text and at the record of which tools ran. We add that set now, built from support questions and buying questions, before the seller is allowed to write a note or touch a card.

## What this tutorial is about

An evaluation, in the sense of this lesson, is a graded set kept on purpose. Each case names the customer's question, the tools that must have run, phrases that must appear, and phrases that must not. Passing means the tools ran and the text matches. A confident tone is not part of the grade.

Five cases call the model. One is the opened jar from tutorial 1. One is chili oil shipped to Ohio, which needs the catalog and the shipping topic. One asks whether sesame crunch contains sesame. One asks to ship fresh labneh to Ohio, which the policy says does not ship. One is a cracked jar, which must mention the 48-hour window. A sixth case does not call the model. It is a canned answer that invents a cash refund and a password. That row is supposed to fail. Keeping the failure is the point.

## How you will get there

The notebook runs the live questions through the agent and grades each reply. It then grades the canned answer, which fails, and prints how many rows passed. You should see the live cases pass, and you should see the canned row remain because it fails. The grader's reasons are printed with the failure, so you can tell a missing phrase from a missing tool.

## Additional things

A grader can be wrong, and a seller can learn to satisfy the phrases without satisfying the store. This notebook is a small version of that habit: duties you already teach, and one bad answer you refuse to throw away. The store in these files is fictional.

## Sources and references

- The cases and the grader are in [common/evals.py](common/evals.py).
- The previous lecture is [7-verification.md](7-verification.md). The notebook is [8-evals.ipynb](8-evals.ipynb). The series map is in [README.md](README.md).
