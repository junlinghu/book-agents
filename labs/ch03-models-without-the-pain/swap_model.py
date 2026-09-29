#!/usr/bin/env python3
"""Same Chapter 2 loop. The only provider switch is the repo-root .env.

Prints BASE_URL and MODEL, runs one question against the Chapter 2
docs, then prints the Ollama / Groq / OpenRouter settings this file
will follow if you edit .env and run it again.
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

PROVIDER_NOTES = """
---
Switch providers by editing .env only, then run this script again.
Do not change this file. Do not commit .env.

Ollama (local weights; API key is ignored but must be non-empty):
  BASE_URL=http://localhost:11434/v1
  API_KEY=ollama
  MODEL=llama3.2
  Fallback if tool calls never appear: MODEL=llama3.1

Groq (hosted). Use a model with local tool-call support.
groq/compound cannot call this lab's read_file (its tools run on Groq).
  BASE_URL=https://api.groq.com/openai/v1
  API_KEY=<your Groq key>
  MODEL=llama-3.3-70b-versatile
  Smaller option: MODEL=llama-3.1-8b-instant

OpenRouter (hosted). Ids are vendor/name. Pick a model that lists tools.
  BASE_URL=https://openrouter.ai/api/v1
  API_KEY=<your OpenRouter key>
  MODEL=meta-llama/llama-3.3-70b-instruct

Harness knobs that stay put when the provider changes:
  temperature and max_tokens in labs/common/client.py
    (this run uses TEMPERATURE={temperature}, MAX_TOKENS={max_tokens})
  the loop and read_file tool in labs/common/
  docs in labs/ch02-your-first-loop/docs/
"""


def print_provider_notes() -> None:
    print(
        PROVIDER_NOTES.format(temperature=TEMPERATURE, max_tokens=MAX_TOKENS).rstrip()
    )


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

    _base_url, api_key, model = require_settings()
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
            "Check BASE_URL, API_KEY, and MODEL in .env, and that the server is running.",
            file=sys.stderr,
        )
        print_provider_notes()
        return 1

    print("--- answer ---")
    print(result.text)
    print()
    print(f"--- stop: {result.stopped} after {result.steps} model call(s) ---")
    for note in observation_notes(result):
        print(f"NOTE: {note}")
    print_provider_notes()
    return 0


if __name__ == "__main__":
    sys.exit(main())
