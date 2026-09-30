#!/usr/bin/env python3
"""Chapter 3 lab. The same Chapter 2 loop. Change models only in .env.

Prints MODEL, runs one question against the Chapter 2 docs, then
prints which model ids to try next.
"""

import os
import sys

# This file is labs/ch03-models-without-the-pain/swap_model.py.
# The repo root is two folders up, so `import labs...` can find the shared loop.
this_folder = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(os.path.dirname(this_folder))
sys.path.insert(0, repo_root)

from dotenv import load_dotenv
from openai import OpenAI

from labs.common.client import DEFAULT_MODEL, MAX_TOKENS, TEMPERATURE
from labs.common.loop import DEFAULT_MAX_STEPS, observation_notes, run_file_agent

# Same documents and loop as Chapter 2. This lab does not copy them.
DOCS = os.path.realpath(os.path.join(repo_root, "labs", "ch02-your-first-loop", "docs"))

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

# A variable already set in the shell wins over .env.
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

print("MODEL=" + model)
print("OPENAI_API_KEY=" + key_status + " (value hidden)")
print("DOCS=" + DOCS)
print("MAX_STEPS=" + str(DEFAULT_MAX_STEPS))
print("TEMPERATURE=" + str(TEMPERATURE))
print("MAX_TOKENS=" + str(MAX_TOKENS))
print("QUESTION: " + question)
print()

if not os.path.isdir(DOCS):
    print("Missing docs directory: " + DOCS, file=sys.stderr)
    sys.exit(1)

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
    result = run_file_agent(
        client,
        model,
        question,
        DOCS,
        max_steps=DEFAULT_MAX_STEPS,
        verbose=True,
    )
except Exception as error:
    detail = str(error).replace(api_key, "***")
    print("Request failed: " + type(error).__name__ + ": " + detail, file=sys.stderr)
    print(
        "Check OPENAI_API_KEY and MODEL in .env. "
        "A 401 means the key is wrong. A 404 means MODEL is not a current id.",
        file=sys.stderr,
    )
    print(MODEL_NOTES.format(temperature=TEMPERATURE, max_tokens=MAX_TOKENS).rstrip())
    sys.exit(1)

print("--- answer ---")
print(result.text)
print()
print("--- stop: " + result.stopped + " after " + str(result.steps) + " model call(s) ---")
for note in observation_notes(result):
    print("NOTE: " + note)
print(MODEL_NOTES.format(temperature=TEMPERATURE, max_tokens=MAX_TOKENS).rstrip())
