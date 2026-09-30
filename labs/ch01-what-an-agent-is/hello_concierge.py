#!/usr/bin/env python3
"""Hello Concierge: one chat completion, no tools.

Chapter 1 lab. This program cannot open shop documents. The reply is
the model's text. Read the note at the end before you trust a sentence.
"""

import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

# Same sampling numbers as the later labs. They live here, not in .env.
TEMPERATURE = 0.2
MAX_TOKENS = 800
DEFAULT_MODEL = "gpt-4.1-mini"

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
What to notice before you trust any sentence above

This script sent one chat completion. It did not open a file, query a
database, or call a tool. A return window, a fee, a closed day, or a
price came from the model and the prompt.

Write down three failure modes you actually saw:

1. Invented shop facts. A return window, fee, hour, or price that this
   program had no way to look up.
2. No source. The answer names no file path, because none was read.
   A confident paragraph is not a citation.
3. No action boundary. The model may offer to refund, ship, or email.
   This process cannot do any of those. The text only sounds like it can.

If the model hedged ("I don't know your policy"), write that down too.
A refusal is different from a fake "30-day refund." Chapter 2 reads
docs/policy.md and docs/faq.md before it answers.
"""

# This file is labs/ch01-what-an-agent-is/hello_concierge.py.
# .env is in the repository root, two folders above this folder.
this_folder = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(os.path.dirname(this_folder))
load_dotenv(os.path.join(repo_root, ".env"))

api_key = os.environ.get("OPENAI_API_KEY", "").strip()
model = os.environ.get("MODEL", "").strip()
if not model:
    model = DEFAULT_MODEL

question = " ".join(sys.argv[1:]).strip()
if not question:
    question = DEFAULT_QUESTION

if api_key:
    key_status = "set"
else:
    key_status = "missing"

print(f"MODEL={model}")
print(f"OPENAI_API_KEY={key_status} (value hidden)")
print(f"TEMPERATURE={TEMPERATURE}")
print(f"MAX_TOKENS={MAX_TOKENS}")
print("TOOLS=none")
print(f"QUESTION: {question}\n")

if not api_key:
    print(
        "OPENAI_API_KEY is empty. Copy .env.example to .env and paste a key "
        "from https://platform.openai.com/api-keys. Never commit .env.",
        file=sys.stderr,
    )
    sys.exit(1)

# A wrong key should fail immediately instead of sleeping through retries.
client = OpenAI(api_key=api_key, timeout=120, max_retries=0)

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
except Exception as error:
    detail = str(error).replace(api_key, "***")
    print(f"Request failed: {type(error).__name__}: {detail}", file=sys.stderr)
    print(
        "Check OPENAI_API_KEY and MODEL in .env. "
        "A 401 means the key is wrong. A 404 means MODEL is not a current id.",
        file=sys.stderr,
    )
    sys.exit(1)

if not response.choices:
    print("The provider returned no choices.", file=sys.stderr)
    sys.exit(1)

answer = response.choices[0].message.content or ""
print(answer.strip() or "(model returned an empty answer)")
print(FAILURE_NOTE)
