#!/usr/bin/env python3
"""Same Chapter 2 loop. The only model switch is MODEL in the repo-root .env.

Prints MODEL, runs one question against the Chapter 2 docs, then
prints the OpenAI model ids this file will follow if you edit .env
and run it again.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from labs.common.client import (  # noqa: E402
    MAX_TOKENS,
    TEMPERATURE,
    describe_runtime,
    make_client,
    redact,
    require_settings,
)
from labs.common.loop import (  # noqa: E402
    DEFAULT_MAX_STEPS,
    observation_notes,
    run_file_agent,
)

# Same documents and harness as Chapter 2. This lab does not copy them.
DOCS = Path(__file__).resolve().parents[1] / "ch02-your-first-loop" / "docs"

DEFAULT_QUESTION = "How much is local delivery, and which day are you closed?"

MODEL_NOTES = """
---
Swap models by editing MODEL in .env only, then run this script again.
Do not change this file. Do not commit .env.

The client uses the official OpenAI API (https://api.openai.com/v1).
Set OPENAI_API_KEY from https://platform.openai.com/api-keys.

Default (tool calling):
  MODEL=gpt-4.1-mini

A second run, same key, different weights:
  MODEL=gpt-4.1

Both ids support tool calls on this loop. If an id is retired, pick
another current tool-capable model from
https://developers.openai.com/api/docs/models
and change only MODEL.

Harness knobs that stay put when MODEL changes:
  temperature and max_tokens in labs/common/client.py
    (this run uses TEMPERATURE={temperature}, MAX_TOKENS={max_tokens})
  the loop and read_file tool in labs/common/
  docs in labs/ch02-your-first-loop/docs/
"""


def print_model_notes() -> None:
    print(MODEL_NOTES.format(temperature=TEMPERATURE, max_tokens=MAX_TOKENS).rstrip())


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    question = " ".join(args).strip() or DEFAULT_QUESTION
    print(describe_runtime())
    print(f"DOCS={DOCS}")
    print(f"MAX_STEPS={DEFAULT_MAX_STEPS}")
    print(f"TEMPERATURE={TEMPERATURE}")
    print(f"MAX_TOKENS={MAX_TOKENS}")
    print(f"QUESTION: {question}\n")

    if not DOCS.is_dir():
        print(f"Missing docs directory: {DOCS}", file=sys.stderr)
        return 1

    api_key, model = require_settings()
    client = make_client()
    try:
        result = run_file_agent(
            client,
            model,
            question,
            DOCS,
            max_steps=DEFAULT_MAX_STEPS,
            verbose=True,
        )
    except Exception as exc:
        print(redact(f"Request failed: {type(exc).__name__}: {exc}", api_key), file=sys.stderr)
        print(
            "Check OPENAI_API_KEY and MODEL in .env. "
            "A 401 means the key is wrong. A 404 means MODEL is not a current id.",
            file=sys.stderr,
        )
        print_model_notes()
        return 1

    print("--- answer ---")
    print(result.text)
    print()
    print(f"--- stop: {result.stopped} after {result.steps} model call(s) ---")
    for note in observation_notes(result):
        print(f"NOTE: {note}")
    print_model_notes()
    return 0


if __name__ == "__main__":
    sys.exit(main())
