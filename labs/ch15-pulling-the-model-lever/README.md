# Lab — Chapter 15. Pulling the model lever

Checker rejects become preference pairs. A recorded bake-off compares a skill patch with a larger model on the same six cases. You compute which lever moved clean success, and what each finished success cost. No cluster.

Chapter: [Chapter 15: Pulling the Model Lever (Lightly)](../../chapters/ch15-pulling-the-model-lever/README.md)

## Goal

Implement `build_pairs` and `summarize_bakeoff`. The raw reject log includes rows you must drop: no repair yet, two identical sides, or a repair with no rule id. The bake-off rows are already scored. Your job is the aggregation Chapter 14 defined, per arm, plus a written reading of the table. You do not train a model, and you do not need a second API key.

There is no `SOLUTION.md`.

## Assignment

Turn in:

1. Your `pairs.py` and `bakeoff.py`.
2. The output of `python labs/ch15-pulling-the-model-lever/bakeoff.py`.
3. The output of `python labs/ch15-pulling-the-model-lever/test_bakeoff.py`. Both pair tests and bake-off tests fail on the starter. A finished lab passes them.
4. A paragraph that answers: which arm has the highest clean-success count, which case `small_v2` still misses, which cases `large_v1` still misses, and which lever you would ship first. Quote the cost per clean success for the arm you would ship.
5. The list of `case_id`s your pair builder kept, and the `case_id`s it dropped, with the reason for each drop.

## Prerequisites

- The shared setup in [`../README.md`](../README.md) for Python. This lab does not read `.env`.

## Setup

Work from the repository root. No model server and no training job.

| File | Role |
|---|---|
| `fixtures/rejects.jsonl` | Raw checker rejects. Some have a preferred repair. Some do not. |
| `fixtures/bakeoff_rows.jsonl` | Eighteen recorded rows: six cases, three arms. |
| `skills/recommend_v1.md` | The baseline brief. |
| `skills/recommend_v2.md` | The patch the small model was given in `small_v2`. |
| `pairs.py` | `load_jsonl` is done. `build_pairs` is the TODO. |
| `bakeoff.py` | `summarize_bakeoff` is the TODO. The script prints the table. |
| `test_bakeoff.py` | The spec. |

The three arms:

| Arm | Model | Skill | What changed |
|---|---|---|---|
| `small_v1` | small | `recommend_v1.md` | Baseline |
| `small_v2` | small | `recommend_v2.md` | Skill text only |
| `large_v1` | large | `recommend_v1.md` | Model only |

Read the two skill files before you interpret the table. The patch states citations, allergens, pastries, and fees. It does not tell the model to read stock.

## Pair rules

Keep a row, in file order, only when:

- `preferred` is an object, not null.
- `rejected` is an object.
- The two sides are not equal.
- `rule_ids` is non-empty.

Each kept object includes `case_id`, `rule_ids`, `rejected`, `preferred`, and `source`. Leave out rows that fail a condition. Do not write a preferred cart yourself to fill a null.

## Bake-off metrics

For each arm:

- `tasks` is the number of rows.
- `clean_successes` counts rows with `clean_success` true.
- `cost_micro_usd` sums `cost_micro_usd` over every row in the arm, failures included.
- `cost_per_clean_success_micro_usd` is that sum floor-divided by `clean_successes` (`//`). Use `None` when the arm has no clean success.
- `latency_p50_clean_ms` is the lower median of `latency_ms` on clean successes only: sort ascending, index `(count - 1) // 2`. Failed rows do not enter the latency list. Use `None` when there is no clean success.

Return a dict keyed by `small_v1`, `small_v2`, and `large_v1`.

## Steps

From the repo root, with the virtualenv active.

1. Read `skills/recommend_v1.md` and `skills/recommend_v2.md`. Then skim `fixtures/bakeoff_rows.jsonl` and notice which `rule_ids` remain on each arm.

2. Run the starter. It loads the rows and stops on the TODO.

   ```bash
   python labs/ch15-pulling-the-model-lever/bakeoff.py
   ```

3. Implement `build_pairs` and `summarize_bakeoff`. Run the script again.

4. Run the spec.

   ```bash
   python labs/ch15-pulling-the-model-lever/test_bakeoff.py
   ```

   Neither command contacts Ollama, a hosted API, or a training cluster.

## What to write up

Paste the table. Then answer, from the rows rather than from memory:

- Which `rule_ids` does `small_v2` still record, and on which `case_id`?
- Which `rule_ids` does `large_v1` still record?
- Why a higher sticker price per call (`large_v1` at 40000 micro-usd a row) is not the same number as micro-usd per clean success.
- Which lever you ship first, and what you would measure next (the residual case, not a new demo).
- Which reject ids were dropped, and why.

## Troubleshooting

- Pair test expects five case ids and gets nine: null preferred sides, the identical pair, and the empty `rule_ids` row are still included.
- Pair test gets zero ids: `build_pairs` is still the starter.
- `NotImplementedError` from the bake-off: `summarize_bakeoff` is still the starter.
- `large_v1` clean successes equal 6: you counted rows, not `clean_success`.
- Cost per clean success for `small_v2` is 12000: that is one row's price. Sum all six rows, then divide by five clean successes.
- Latency for `small_v2` is 1550: that row is the stockout failure. It stays out of the p50 list.
- You changed a number inside `bakeoff_rows.jsonl`: put it back. The spec matches the recorded file, not a hand-edited winner.
