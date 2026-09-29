#!/usr/bin/env python3
"""Hello Concierge: one chat completion, no tools.

Chapter 1 lab. This process cannot open shop documents. The reply is
the model's text. Read the failure-mode note before you trust a sentence.
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
from labs.common.loop import message_text  # noqa: E402

SYSTEM = """You are the counter concierge for Hearth Lane Café, a small neighborhood café.
Customers ask about the menu, hours, returns, and shipping.
Answer in a short, specific paragraph they could hear at the counter.
"""

DEFAULT_QUESTION = (
    "I opened a bag of your house coffee and they're not for me. "
    "Can I return them? Also, can you ship a cardamom bun to another state?"
)

FAILURE_NOTE = """
---
What to notice before you ship any sentence above

This script sent one chat completion. It did not open a file, query a
database, or call a tool. Anything specific — a return window, a shipping
fee, a closed day, a price — came from the model and the prompt.

Write down three failure modes you actually saw. Start with these:

1. Invented shop facts. A return window, fee, hour, or price that this
   program had no way to look up.
2. No source. The answer names no file path, because none was read.
   A confident paragraph is not a citation.
3. No action boundary. The model may offer to refund, ship, or email.
   This process cannot do any of those. The text only sounds like it can.

If the model hedged ("I don't know your policy"), record that too. A
refusal is a different miss from a fake "30-day refund." Chapter 2 is
the loop that reads docs/policy.md and docs/faq.md before it answers.
"""


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    question = " ".join(args).strip() or DEFAULT_QUESTION
    print(describe_runtime())
    print(f"TEMPERATURE={TEMPERATURE}")
    print(f"MAX_TOKENS={MAX_TOKENS}")
    print("TOOLS=none")
    print(f"QUESTION: {question}\n")

    _base_url, api_key, model = require_settings()
    client = make_client()
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": question},
            ],
        )
    except Exception as exc:
        print(redact(f"Request failed: {type(exc).__name__}: {exc}", api_key), file=sys.stderr)
        print(
            "Check BASE_URL, API_KEY, and MODEL in .env, and that the server is running.",
            file=sys.stderr,
        )
        return 1

    if not response.choices:
        print("The provider returned no choices.", file=sys.stderr)
        return 1
    content = message_text(response.choices[0].message.content).strip()
    print(content or "(model returned an empty answer)")
    print(FAILURE_NOTE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
