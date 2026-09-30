# Lab — Chapter 25. Self-improving agents

An agent proposes a skill patch. You merge it only when the file list stays on the skill surface, the Chapter 12 suite stays green, and a person is the reviewer. One proposal fails the suite. One proposal would edit the grader. Neither merges. No live model, and no `SOLUTION.md`.

Chapter: [Chapter 25: Self-Improving Agents (Honestly)](../../chapters/ch25-self-improving-agents/README.md)

## Goal

Implement `patch_surface_ok` and `decide_merge`. The suite runner is already done: it scores recorded answers with the Chapter 12 constraint check and does not modify Chapter 12. Your function returns the word `merge` or the word `reject`. It does not copy a proposal onto the skill file. A person does that, after reading the diff, and only when you returned `merge`.

## Assignment

Turn in:

1. Your `gate.py`. Leave `suite.py` scoring constraints as it does now.
2. The output of `python labs/ch25-self-improving-agents/run_gate.py`. On the starter the suite table prints and the decision section stops on the TODO. A finished gate prints a decision for reviewers `maya` and `agent` on each proposal.
3. The output of `python labs/ch25-self-improving-agents/test_gate.py`. `SuiteTests` pass on the starter. `SurfaceTests` and `MergeTests` fail until the TODOs are done.
4. The answers in [What to write up](#what-to-write-up).

## Prerequisites

- The shared setup in [`../README.md`](../README.md) for Python. This lab does not read `.env`.
- Chapter 12's fixtures are read in place. You do not need to have finished that lab's `grade_hardened`. Do not edit those fixtures or `labs/ch12-evals-from-real-failures/grader.py` to make this gate green.

## Setup

Work from the repository root. No model server.

| File | Role |
|---|---|
| `skills/counter.md` | The skill that is merged today. The proposals want to replace it. The script does not replace it. |
| `proposals/good_counter.md` | A proposal tied to the known-good answers. Read it. The suite does not read it. |
| `proposals/bad_helpful.md` | A proposal tied to the logged misses. |
| `proposals/grader_note.md` | A proposal that asks to relax the Chapter 12 grader. |
| `patches/*.json` | The file list, which answer set to score, and the path of the proposal text. |
| `suite.py` | Loads Chapter 12 cases and scores them. Done. |
| `gate.py` | `patch_surface_ok` and `decide_merge` are the TODOs. |
| `run_gate.py` | Prints the suite, then the decisions. |
| `test_gate.py` | The spec. |

Answer sets:

| `answers` on the patch | Rows scored |
|---|---|
| `good` | `labs/ch12-evals-from-real-failures/fixtures/good_answers.jsonl` |
| `bad` | The `bad_answer` field on each case in `failures.jsonl` |

The recorded answers are the trace. This lab does not ask a model to follow the skill. Chapter 15's bake-off was recorded the same way.

## Surface

`patch_surface_ok(patch)` looks at `patch["files"]`.

Return true only when `files` is a non-empty list of strings and every string is one skill path.

- Forward slashes only. Reject backslashes.
- Reject absolute paths.
- Reject empty segments, `.`, and `..`. `skills/../grader.py` is a climb, not a skill.
- The only accepted shape is `skills/<name>.md`.
- `<name>` is one or more letters, digits, underscores, or hyphens. `skills/counter.md` and `skills/restock-note.md` are both skills. `skills/counter.txt` is not.
- One bad path fails the whole list. A skill file plus `grader.py` is not ok.

## Merge

`decide_merge(patch, report, reviewer)` returns `merge` or `reject`.

Return `merge` only when all of these are true:

- `reviewer` is a string. After stripping whitespace it is non-empty, and it is not the word `agent` in any capitalization. `maya` and `Ellis` are people. `agent`, `Agent`, and a blank string are not.
- `patch_surface_ok(patch)` is true.
- `report` is a dict, `report["passed"]` is true, and `report["failures"]` is empty. A report that says passed and still lists a failure is not green.

Otherwise return `reject`. Do not write files. Do not import Chapter 12's `grade_hardened` and do not change it.

## Steps

From the repo root, with the virtualenv active.

1. Read `skills/counter.md`, then the three files in `proposals/`. The suite has not seen those files. You should.

2. Run the starter. The suite table is the evidence. The decision section stops on the TODO.

   ```bash
   python labs/ch25-self-improving-agents/run_gate.py
   ```

   `good_counter` should print GREEN. `bad_helpful` should print RED with a reason on each case. `rewrite_grader` should print GREEN, because its recorded answers are the known-good set. The file it wants to edit is still the grader.

3. Implement `patch_surface_ok` and `decide_merge`. Run the script again. Keep both traces if you still have the starter output. The finished trace needs the decisions.

4. Run the spec.

   ```bash
   python labs/ch25-self-improving-agents/test_gate.py
   ```

   Neither command contacts a model server. Neither command should change `skills/counter.md`.

## What to write up

Paste the suite table and the decision lines. Then answer:

- For `bad_helpful`, list the case ids that failed and quote one reason for three of them, including `opened-coffee-window`.
- Why `rewrite_grader` is RED as a decision when its suite line is GREEN. Name the path that failed the surface check.
- What `decide_merge` returned for reviewer `agent` on the green skill, and why a standing "the agent may merge when green" grant is not a reviewer.
- Read `proposals/good_counter.md` against `skills/counter.md`. The suite can be green and the proposal can still be wrong. Quote any sentence you would refuse to merge, and say why these ten cases did not catch it. If you would merge the whole file, name a class of mistake the cases would still allow.
- Confirm you did not edit Chapter 12. The gate reads those fixtures. It does not own them.

## Troubleshooting

- `NotImplementedError` under decisions: `decide_merge` is still the starter. The suite table above it is still evidence. Keep it.
- Surface tests fail on `skills/counter.md`: `patch_surface_ok` is still the starter, or it demands a field other than `files`.
- `skills/../grader.py` is allowed: split the path into segments and reject `..`. A prefix check for `skills/` is not enough.
- `rewrite_grader` returns `merge`: you trusted `passed` and did not look at `files`.
- Reviewer `Agent` returns `merge`: compare the stripped name case-insensitively to `agent`.
- A report with `passed: true` and a non-empty `failures` list returns `merge`: both have to be clean.
- `SuiteTests` fail: `suite.py` or the Chapter 12 fixtures were edited. Put them back. The known-good answers pass the constraint check already.
- `skills/counter.md` changed on disk: the script does not write it. Revert your copy. Merging, in this lab, is the word `merge` plus the write-up.
