#!/usr/bin/env python3
"""File-reading concierge: a tool loop with read_file limited to docs/.

Chapter 2 lab. Answers should cite docs/policy.md or docs/faq.md.
The harness stops on a final message, max steps, a repeated call, or
a completion cut off by max_tokens.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from labs.common.client import describe_runtime, make_client, redact, require_settings  # noqa: E402
from labs.common.loop import (  # noqa: E402
    DEFAULT_MAX_STEPS,
    observation_notes,
    run_file_agent,
)

DOCS = Path(__file__).resolve().parent / "docs"

DEFAULT_QUESTION = (
    "I opened a bag of your house coffee and they're not for me. "
    "Can I return them? Also, can you ship a cardamom bun to another state?"
)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    question = " ".join(args).strip() or DEFAULT_QUESTION
    print(describe_runtime())
    print(f"DOCS={DOCS}")
    print(f"MAX_STEPS={DEFAULT_MAX_STEPS}")
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
        return 1

    print("--- answer ---")
    print(result.text)
    print()
    print(f"--- stop: {result.stopped} after {result.steps} model call(s) ---")
    for note in observation_notes(result):
        print(f"NOTE: {note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
