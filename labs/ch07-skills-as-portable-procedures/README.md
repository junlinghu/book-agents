# Lab — Chapter 7. Skills as portable procedures

Two markdown procedures, `skills/recommend.md` and `skills/cite-sources.md`. The concierge loads a catalog of headers, then the body of at most two skills. You change a later answer by editing the markdown and leaving the model settings alone.

Chapter: [Chapter 7: Skills as Portable Procedures](../../chapters/ch07-skills-as-portable-procedures/README.md)

## Goal

Finish the loader in `concierge.py` and the two skill files. Show a trace that names the skills you loaded and the shop file the tool read. Then edit only the markdown, run the same question again, and show that the answer changed because the procedure changed.

## Assignment

Turn in:

1. The finished `skills/recommend.md` and `skills/cite-sources.md`.
2. A trace of the default recommendation question: startup header, `CATALOG`, `LOADED`, tool results, answer, and the stop line.
3. For each shop fact in that answer, the path cited and a quote from `faq.md` or `policy.md`. If the answer names the cardamom bun for a customer who cannot eat nuts, say so.
4. A second trace of the same question after you changed the markdown only. Include the diff of the skill file. `MODEL` must match the first trace.
5. One question that should load `cite-sources` and should not load `recommend`, with the `LOADED` line visible.

## Prerequisites

- The shared setup in [`../README.md`](../README.md): Python 3.10 or newer, a virtualenv, and a repo-root `.env`
- A model that can emit tool calls. The note in the shared setup applies here, because this lab uses `read_file`

## Setup

Do the shared setup in [`../README.md`](../README.md) once, then come back here. If you already installed dependencies for Chapters 1–3, reuse that virtualenv.

Work from the repository root. Shop documents are the Chapter 2 files, not a second copy:

| File | Holds |
|---|---|
| `labs/ch02-your-first-loop/docs/policy.md` | Returns, shipping, local delivery |
| `labs/ch02-your-first-loop/docs/faq.md` | Hours, menu prices, allergens |

Skill stubs:

| File | You write |
|---|---|
| `skills/recommend.md` | When to recommend, which file to read, how to use an allergy and a budget, what to refuse |
| `skills/cite-sources.md` | When a shop fact needs a path, what to do when the files are silent, what is not a citation |

`concierge.py` calls three functions you must finish: `catalog`, `select_skills`, and `load_bodies`. As shipped, they raise `NotImplementedError` and the script does not call the model. The chat loop below those functions is the harness. You do not need a new tool.

## Steps

From the repo root, with the virtualenv active.

1. Write the skill headers and bodies. `catalog` must be able to read `name`, `description`, and `version` from the `---` header without treating the body as the description. Keep the menu prices and allergen list in `faq.md`. The recommendation skill should point at that file.

2. Implement the three functions. `select_skills` returns at most two names. A question that matches nothing returns an empty list. `load_bodies` returns procedure text, or an `ERROR:` line if a name does not exist.

3. Run the default question.

   ```bash
   python labs/ch07-skills-as-portable-procedures/concierge.py
   ```

   Default question:

   > What can you recommend for someone who cannot eat nuts, under six dollars?

   A sound trace loads the recommendation skill (and the citation skill if your catalog says prices must be cited), reads `faq.md`, and does not promise a nut-free cardamom bun. The bun contains almonds. There is no nut-free preparation area.

4. Optional control questions:

   ```bash
   python labs/ch07-skills-as-portable-procedures/concierge.py "I opened a bag of your house coffee and they're not for me. Can I return them?"
   python labs/ch07-skills-as-portable-procedures/concierge.py "What's the Wi-Fi password?"
   ```

   The return question should cite `policy.md`. Opened coffee is final sale. The password is not in either document.

5. Edit one rule in a skill file. Do not edit `concierge.py` or `.env` between this run and the run you are comparing. Examples of the kind of edit, not text you must use: prefer the cheapest item that fits the budget; require a short quote from the file as well as the path; tell the recommender to mention that rye porridge is cooked in a pot that also holds milk. Run the same question again. Save both traces and the diff.

## What to write up

Record:

- `MODEL` and the skill versions you printed. The key is not printed.
- The `CATALOG` lines and the `LOADED` line for each run.
- Tool lines and whether each result started with `PATH:` or `ERROR:`.
- The answer, and a quote from the shop file next to each shop fact.
- The markdown diff for the second run, and which sentence in the answer moved with it.
- If a run loaded no skills, or loaded every skill for every question, say what in the catalog caused that.

## Troubleshooting

- `NotImplementedError` and exit code 2: `catalog`, `select_skills`, or `load_bodies` is still the stub.
- Connection error, HTTP 401, or HTTP 404: key or `MODEL`. Checks are in [`../README.md`](../README.md).
- `LOADED: (none)` on the recommendation question: the description is empty or the matcher does not see the question. Fix the header or `select_skills`, then run again.
- A nut-free bun, or a price with no `docs/` path, after the skill body contains the rule: quote the step and the sentence. The procedure was loaded and was not followed, or the step does not say what you think it says.
- Empty tool log: the model never called `read_file`. The harness does not send `tool_choice`. Change `MODEL` using the shared setup, and keep the empty trace in the write-up.
