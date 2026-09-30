#!/usr/bin/env python3
"""Chapter 2 lab. The model may call read_file. This process reads the file.

Answers should cite docs/policy.md or docs/faq.md.
The loop stops on a final message, max steps, a repeated call, or
a completion cut off by max_tokens. The loop itself is run_file_agent
in labs/common/loop.py.
"""

import os
import sys

# This file is labs/ch02-your-first-loop/file_agent.py.
# Python would otherwise only search this folder for imports.
# The repo root is two folders up, which is where the labs package lives.
this_folder = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(os.path.dirname(this_folder))
sys.path.insert(0, repo_root)

from dotenv import load_dotenv
from openai import OpenAI

from labs.common.client import DEFAULT_MODEL
from labs.common.loop import DEFAULT_MAX_STEPS, observation_notes, run_file_agent

DOCS = os.path.realpath(os.path.join(this_folder, "docs"))

DEFAULT_QUESTION = (
    "I opened a bag of your house coffee and they're not for me. "
    "Can I return them? Also, can you ship a cardamom bun to another state?"
)

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
    sys.exit(1)

print("--- answer ---")
print(result.text)
print()
print("--- stop: " + result.stopped + " after " + str(result.steps) + " model call(s) ---")
for note in observation_notes(result):
    print("NOTE: " + note)
