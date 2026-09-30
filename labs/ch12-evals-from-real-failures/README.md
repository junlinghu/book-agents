# Lab — Chapter 12. Evals from real failures

Ten logged concierge misses become fixtures. A weak keyword grader passes them. You game that grader, then harden it so the misses fail and the known-good answers still pass.

Chapter: [Chapter 12: Evals from Real Failures](../../chapters/ch12-evals-from-real-failures/README.md)

## Goal

Treat the fixture file as a product requirement. `grade_weak` is the check an agent can satisfy without being right. `grade_hardened` is the check you would be willing to gate on. Build at least two cheat answers that the weak grader passes, and make the hardened grader fail the logged bad answers, the example cheat, and your cheats, without failing the known-good set.

This lab does not call a model. There is no `SOLUTION.md`.

## Assignment

Turn in:

1. Your `grader.py`, with `grade_hardened` implemented. Leave `grade_weak` behaving as it does now so the weak tests still pass.
2. `fixtures/my_cheats.jsonl`: at least two lines you wrote. Each line is `{"id": "<case id>", "answer": "<text>"}`. The weak grader should pass each cheat. The hardened grader should fail it.
3. The output of `python labs/ch12-evals-from-real-failures/run_eval.py`.
4. The output of `python labs/ch12-evals-from-real-failures/test_grader.py`. On the starter, `WeakGraderTests` pass and `HardenedGraderTests` fail. A finished grader passes both.
5. A short note for one cheat: which keywords made the weak grader pass, and which constraint made the hardened grader fail. If a cheat of yours still passes `grade_hardened`, say what constraint you would add, and add it only if you also keep the known-good answer passing. Do not delete a bad answer to make the report green.

## Prerequisites

- The shared setup in [`../README.md`](../README.md) for Python. This lab does not read `.env`.

## Setup

Work from the repository root. No model server.

| File | Role |
|---|---|
| `fixtures/failures.jsonl` | Ten logged misses: the bad answer, why it failed, the weak keywords, and the real constraint. |
| `fixtures/good_answers.jsonl` | An acceptable answer for each id. Hardening must not reject these. |
| `fixtures/example_cheat.jsonl` | One keyword costume: `14 docs/policy.md`. |
| `fixtures/my_cheats.jsonl` | Yours. The starter does not include this file. |
| `grader.py` | `grade_weak` is done. `grade_hardened` is the TODO. |
| `run_eval.py` | Prints weak vs hardened for bad, good, and cheat rows. |
| `test_grader.py` | The gate. |

## Steps

From the repo root, with the virtualenv active.

1. Score the fixtures with the starter. The weak grader passes the bad answers. The hardened grader, still delegated to the weak one, passes them too.

   ```bash
   python labs/ch12-evals-from-real-failures/run_eval.py
   ```

2. Read `opened-coffee-window` in `failures.jsonl` next to its good answer. Both contain `14` and `docs/policy.md`. Only one says the opened bag is final sale.

3. Write two cheats in `fixtures/my_cheats.jsonl`. A cheat is wrong about the shop and still contains every `weak_keywords` entry for its case. Use two different case ids. Re-run `run_eval.py` and confirm the weak column says `pass` for `my_cheat`.

4. Replace the body of `grade_hardened`. Compare case-insensitively.

   - Every phrase in `must_contain` must appear in the answer.
   - No phrase in `must_not_contain` may appear.
   - `citation` must appear.
   - `passed` is false when any of those fire, and `reasons` lists what fired.

   Do not special-case ids. The fields on the case are the requirement.

5. Run the gate.

   ```bash
   python labs/ch12-evals-from-real-failures/test_grader.py
   ```

   The command does not contact Ollama or a hosted API.

## What to write up

Record:

- For `opened-coffee-window`, `invented-wifi-password`, and one more id you choose: whether weak and hardened passed the bad answer, the good answer, and (if you cheated that id) your cheat.
- The two cheat strings, quoted.
- One constraint that would have been too blunt. For example, forbidding the characters `14` would also reject the good opened-coffee answer, which mentions the unopened window. Say what you required instead, or what the fixture already requires.
- The unittest summary line.

## Troubleshooting

- Hardened tests fail and `grade_hardened` still calls `grade_weak`: that is the starter. Replace the body.
- A known-good answer fails: print `grade.reasons`. A forbidden phrase that is also a substring of the good answer is too wide. The fixtures were written so the good answers satisfy the lists. Check case folding, and check that you are testing the answer rather than the question.
- A bad answer still passes hardened: a required phrase is too easy, or a forbidden phrase is not the one in the bad answer. Read that row's fields again.
- Your cheat passes hardened: it accidentally satisfied the constraint. Write a worse answer, or tighten a phrase only if the good answer still passes.
- `my_cheats.jsonl` is missing: `run_eval.py` still scores the example cheat. The assignment wants your file as well.
