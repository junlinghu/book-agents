# Lab — Chapter 22. Identity and observability

An OpenTelemetry-shaped trace for session `restock-1842`, and a replay of one canned failure from the log alone. The starter emits no spans and copies a supplier token into the document. `replay_failure` returns `{}`.

Chapter: [Chapter 22: Identity and Observability](../../chapters/ch22-identity-and-observability/README.md)

## Goal

Emit a success trace a later reader can trust, and explain the failure fixture without rerunning the job and without a model. The success draft is 12 bags (par 16 minus on hand 4). The manager confirms. The ledger returns `po-1842`. The failure fixture drafts 20 and lets the agent confirm; place errors and stores no order id. Your replay has to compute the expected quantity from the shelf span, not from memory of this paragraph.

This lab does not need a model server or a trace collector. There is no `SOLUTION.md`.

## Assignment

Turn in:

1. Your `trace.py`.
2. The output of `python labs/ch22-identity-and-observability/trace.py` after the TODOs are done (the emit JSON and the replay JSON).
3. The output of `python labs/ch22-identity-and-observability/test_trace.py`. The starter fails these tests. A finished module passes them.
4. The answers in [What to write up](#what-to-write-up).

## Prerequisites

- The shared setup in [`../README.md`](../README.md) is enough if you want the same virtualenv as the earlier labs. The script and the tests use the standard library only.
- Python 3.10 or newer

## Setup

Reuse the shared setup in [`../README.md`](../README.md). No network service, no API key, no OpenTelemetry package.

Work from the repository root.

| File | Role |
|---|---|
| `fixtures/restock-1842-failure.json` | Canned failure. Do not edit it to make the test pass. |
| `trace.py` | Fill in `emit_restock_trace` and `replay_failure`. |
| `test_trace.py` | The spec. It fails until the TODOs are done. |

`SUPPLIER_TOKEN` in `trace.py` is a fake credential. It must not appear in the emitted JSON, under any key.

## Steps

Success document from `emit_restock_trace`:

- Top-level `trace_id` is `restock-1842` and `service` is `hearth-lane-restock`.
- `spans` is a list. Each span has exactly these keys: `span_id`, `trace_id`, `parent_span_id`, `name`, `actor`, `status`, `attributes`.
- `actor` is `{"kind": ..., "id": ...}`. `kind` is `user`, `agent`, or `tool`.
- `status` is `ok` or `error`. `parent_span_id` is `""` for the single root and a real `span_id` for every other span. Span ids are unique. Every span's `trace_id` is `restock-1842`.
- Include these spans:

| name | actor | status | attributes |
|---|---|---|---|
| `restock` | agent `restock-agent` | `ok` | root, `parent_span_id` `""` |
| `read_stock` | tool `inventory` | `ok` | `sku` `house-coffee`, `on_hand` 4, `par` 16 |
| `draft_order` | agent `restock-agent` | `ok` | `qty` 12 |
| `confirm` | user `manager` | `ok` | `qty` 12 |
| `place_order` | tool `ledger` | `ok` | `qty` 12, `order_id` `po-1842`, `idempotency_key` `restock-1842` |

`replay_failure(document)` returns a dict with:

- `trace_id` from the document
- `failed_span`, `status`, and `reason` from the span whose `status` is `error` (`reason` is `attributes.reason`)
- `on_hand` and `par` from the `read_stock` span
- `draft_qty` from the `draft_order` span's `qty`
- `expected_qty` computed as `par - on_hand`
- `confirm_actor_kind` and `confirm_actor_id` from the `confirm` span's actor
- `order_id` from the error span's attributes (the canned file stores JSON `null`, which is Python `None`)

The second test copies the fixture, sets the draft quantity to 18 and on-hand to 5, and expects `draft_qty` 18 and `expected_qty` 11. Read the document. Do not return 20 because the chapter mentioned 20.

From the repo root:

1. Run the starter.

   ```bash
   python labs/ch22-identity-and-observability/trace.py
   ```

   The emit section has `"spans": []` and a supplier token. The replay section is `{}`.

2. Fill in the two TODOs in `trace.py`.

3. Run the script again. You should see five spans on the success path and a replay that reports `expected_qty` 12, `draft_qty` 20, and `confirm_actor_kind` `agent`.

4. Run the spec.

   ```bash
   python labs/ch22-identity-and-observability/test_trace.py
   ```

   It should finish with `OK`. It does not contact a model server.

## What to write up

Answer in a few sentences each:

- Who the four child spans say acted, and why the confirm actor on the success trace cannot be `restock-agent`.
- What `expected_qty` is on the canned failure, which span you subtracted, and which span is wrong.
- Why the place span's error is the correct audit outcome even though a draft exists. Say what `order_id` is.
- Where `SUPPLIER_TOKEN` belongs, and why a span attribute is the wrong place. Refer to the canary idea from Chapter 21.
- One field you would add for Chapter 14's one-page report, and which span it would be copied from. You do not have to implement it.

## Troubleshooting

- `supplier_token` is still in the JSON: the starter return value is still there. Delete that key. Do not rename the token and keep it.
- Span key mismatch: the test wants exactly the seven keys listed above. Extra keys such as `start_time` fail the shape check.
- Replay stays at 20 after you edit the fixture in the test: the function is returning a constant. Read `draft_order` and `read_stock` from the argument.
- `order_id` is the string `"null"`: parse the JSON value. The file stores `null`, not the word null in quotes.
- `ModuleNotFoundError`: run from the repository root.
