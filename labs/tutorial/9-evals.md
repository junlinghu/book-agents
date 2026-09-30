# Tutorial 9. A small set of graded cases

## Motivation

The agent can answer from the shop’s files, follow a procedure, quote a page as untrusted, and submit a restock proposal to a checker. What it still cannot do is show, on a later day, that the answers you already care about still hold. A conversation you remember is a weak test. The moment you change the brief or the tools, you need a small set of cases and a grader that looks at the text and at the record of which tools ran. We add that set now, built from duties and failures you have already met, before the agent is allowed to write a ticket or touch a card.

## What this tutorial is about

An evaluation, in the sense of this lesson, is a small graded set kept on purpose. Each case names the question, the tool that must have run, phrases that must appear, and phrases that must not. Passing means the tool ran and the text matches. A confident tone is not part of the grade.

You will grade two live answers from the same loop as the earlier tutorials. One is the opened-coffee return from tutorial 1. The reply must consult the returns rule, and it must say that opened coffee is final sale. One is a request to ship milk, which must consult the policy and must say the café does not ship it. You will also keep a third case that does not call the model at all. It is a canned answer that invents a network password, the sort of invention the menu explicitly warns against, because the password is printed on the paper receipt and is absent from the shop documents. That row is supposed to fail. Keeping the failure is the point. Removing it would make the set look healthier than the product is.

## How you will get there

The notebook runs the two live questions through the agent and grades each reply against the required phrases, the forbidden phrases, and the tool record. It then grades the canned password answer, which fails, and prints how many of the three rows passed. You should see the two tool-using cases pass, and you should see the canned row remain in the set because it fails. The grader’s reasons are printed with the failure, so you can tell a missing phrase from a missing tool.

## Additional things

A grader can be wrong, and an agent can learn to satisfy the phrases without satisfying the shop. Chapter 12 is where the book takes up graders that fail, the difference between a saved set and a live sample of real use, and the habit of turning a real miss into a new case. This notebook is the smallest version of that habit: two duties you already teach, and one bad answer you refuse to throw away.

Tutorial 13 will make the tool record easier to read, which is the same record this grader already consults. The café in these files is fictional.

## Sources and references

- [Chapter 12: Evals from Real Failures](../../chapters/ch12-evals-from-real-failures/README.md), and the lab [labs/ch12-evals-from-real-failures](../ch12-evals-from-real-failures).
- The previous lecture is [8-verification.md](8-verification.md). The notebook is [9-evals.ipynb](9-evals.ipynb). The series map is in [README.md](README.md).
