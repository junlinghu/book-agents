#!/usr/bin/env python3
"""Café preferences that survive a restart, and a quiz the next day.

Chapter 6 lab. Day 1 stores what the staff said about Priya. ``quiz`` starts
a fresh message list and reads the JSON store. ``forget`` is still a stub
in memory_api.py. ``--check`` does not call a model.

  python labs/ch06-memory/prefs_agent.py --check
  python labs/ch06-memory/prefs_agent.py --reset
  python labs/ch06-memory/prefs_agent.py
  python labs/ch06-memory/prefs_agent.py quiz
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAB_DIR = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from labs.common.client import describe_runtime, make_client, redact, require_settings  # noqa: E402
from labs.common.loop import DEFAULT_MAX_STEPS, run_tool_agent  # noqa: E402
from labs.common.tools import READ_FILE_TOOL, read_file  # noqa: E402
from memory_api import (  # noqa: E402
    MEMORY_TOOLS,
    ensure_store,
    load_store,
    memory_forget,
    memory_get,
    memory_search,
    memory_set,
    rejects_generalization,
    reset_store,
)

DOCS = ROOT / "labs" / "ch02-your-first-loop" / "docs"
SEED = LAB_DIR / "seed_memory.json"
STORE = LAB_DIR / "memory" / "cafe_memory.json"

DAY1_QUESTION = (
    "Priya from the mill office is picking up tomorrow. She is allergic to almonds. "
    "She takes oat milk in a pour-over, not dairy. Her office order has to stay at "
    "or under $40. Please remember that for the morning."
)

QUIZ = [
    (
        "Priya is picking up a pour-over and a pastry. What must not be in her order, "
        "and can we promise her a nut-free cardamom bun?"
    ),
    "A new hire asks: Priya is allergic to almonds, so is Hearth Lane a nut-free café now?",
    "What is the ceiling on Priya's office order? Answer from memory, not from a guess.",
]

DAY1_SYSTEM = """You are the counter concierge for Hearth Lane Café.
Store durable facts with memory_set. Use scope customer:priya for Priya.
An allergy is kind constraint. A milk choice is kind preference.
A spending ceiling is kind constraint.
Do not store shop rules that already live in the documents.
Do not store a shop belief that the café is nut-free because one guest has an allergy.
Do not invent a Wi-Fi password.
"""

QUIZ_SYSTEM = """You are the counter concierge for Hearth Lane Café on the next morning.
The message list is new. Durable facts are only in memory tools.
Search memory before you answer about a guest.
For an allergen, a bun, or a shop rule, read faq.md with read_file and treat that file as the shop fact.
If an active memory record conflicts with the file, call memory_forget on that id and answer from the file.
One guest's constraint is not a rule for every customer. Do not memory_set a shop-wide nut-free belief.
If memory has no record for a fact, say you do not have it. Do not invent a budget.
"""

REPEAT_NOTE = (
    "\n\nNOTE: You already called this tool with the same arguments. "
    "Answer from the result you have."
)


def _dispatch(name: str, args: dict) -> str:
    if name == "read_file":
        path = args.get("path", "")
        if not isinstance(path, str):
            path = ""
        return read_file(DOCS, path)
    if name == "memory_get":
        memory_id = args.get("id", "")
        return memory_get(STORE, memory_id if isinstance(memory_id, str) else "")
    if name == "memory_set":
        return memory_set(
            STORE,
            args.get("text", "") if isinstance(args.get("text"), str) else "",
            args.get("scope", "") if isinstance(args.get("scope"), str) else "",
            args.get("kind", "") if isinstance(args.get("kind"), str) else "",
            args.get("source", "") if isinstance(args.get("source"), str) else "",
        )
    if name == "memory_search":
        query = args.get("query", "")
        scope = args.get("scope")
        if not isinstance(query, str):
            query = ""
        if scope is not None and not isinstance(scope, str):
            scope = ""
        return memory_search(STORE, query, scope if scope else None)
    if name == "memory_forget":
        memory_id = args.get("id", "")
        return memory_forget(STORE, memory_id if isinstance(memory_id, str) else "")
    return json.dumps(
        {
            "ok": False,
            "code": "unknown_tool",
            "retryable": False,
            "message": f"Unknown tool {name!r}.",
            "hint": "Use memory_get, memory_set, memory_search, memory_forget, or read_file.",
        },
        indent=2,
    )


def _active_texts(path: Path) -> list[str]:
    store = load_store(path)
    return [row["text"] for row in store["records"] if row.get("status") == "active"]


def run_check() -> int:
    """Persistence, search, and the forget stub. Uses a temporary store."""
    print(f"SEED={SEED}")
    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "cafe_memory.json"
        reset_store(path, SEED)
        again = load_store(path)
        if not any(row["id"] == "mem_buns_nutfree" for row in again["records"]):
            print("CHECK FAIL: the seed belief did not load.")
            return 1
        stored = json.loads(
            memory_set(
                path,
                "Priya is allergic to almonds.",
                "customer:priya",
                "constraint",
                "staff note, day 1",
            )
        )
        print(f"--- set: code={stored.get('code')} ok={stored.get('ok')} ---")
        if stored.get("ok") is not True:
            print("CHECK FAIL: memory_set rejected a customer constraint.")
            failures += 1
        found = json.loads(memory_search(path, "almond"))
        texts = [row["text"] for row in found.get("records", [])]
        print(f"--- search almond: {texts} ---")
        if "Priya is allergic to almonds." not in texts:
            print("CHECK FAIL: memory_search did not return the new constraint.")
            failures += 1
        if "Cardamom buns are nut-free." not in texts and "Cardamom buns are nut-free." not in _active_texts(path):
            print("CHECK FAIL: the seeded belief disappeared.")
            failures += 1
        reloaded = load_store(path)
        if not any(row["text"] == "Priya is allergic to almonds." for row in reloaded["records"]):
            print("CHECK FAIL: the record did not survive a reload from disk.")
            failures += 1
        forgotten = json.loads(memory_forget(path, "mem_buns_nutfree"))
        print(f"--- forget: code={forgotten.get('code')} ok={forgotten.get('ok')} ---")
        still = json.loads(memory_search(path, "nut-free"))
        still_texts = [row["text"] for row in still.get("records", [])]
        if forgotten.get("code") == "forget_not_implemented":
            if "Cardamom buns are nut-free." not in still_texts:
                print("CHECK FAIL: the stub forget changed search results.")
                failures += 1
            else:
                print(
                    "TASK OPEN: memory_forget still returns forget_not_implemented. "
                    "The nut-free belief is active after the call. Fill in memory_api.py."
                )
        elif forgotten.get("ok") is True:
            if "Cardamom buns are nut-free." in still_texts:
                print("CHECK FAIL: forget reported success and search still returns the belief.")
                failures += 1
            else:
                audit = json.loads(memory_get(path, "mem_buns_nutfree"))
                record = audit.get("record") or {}
                if record.get("status") != "forgotten":
                    print("CHECK FAIL: the row was removed or not marked forgotten.")
                    failures += 1
                else:
                    print("TASK DONE: the belief is forgotten and memory_get can still audit it.")
        else:
            print(f"CHECK FAIL: unexpected forget result: {forgotten}")
            failures += 1
        bad_scope = json.loads(
            memory_set(path, "Priya likes the window seat.", "everyone", "preference", "staff")
        )
        print(f"--- bad scope: code={bad_scope.get('code')} ---")
        if bad_scope.get("code") != "bad_scope":
            print("CHECK FAIL: an illegal scope was stored.")
            failures += 1

    refusal = rejects_generalization("The café is nut-free.", "shop")
    print(f"--- generalization guard: {refusal!r} ---")
    if refusal is None:
        print(
            "TASK OPEN: rejects_generalization still returns None for a shop-wide "
            "nut-free claim. A memory_set of that sentence would be stored."
        )
    elif refusal != "refused_generalization":
        print("CHECK FAIL: the guard returned an unexpected code.")
        failures += 1
    else:
        print("TASK DONE: a shop-wide nut-free claim is refused.")

    if failures:
        return 1
    print("CHECK OK")
    return 0


def _run_turn(client: object, model: str, system: str, question: str) -> int:
    print(f"QUESTION: {question}\n")
    result = run_tool_agent(
        client,
        model,
        question,
        [*MEMORY_TOOLS, READ_FILE_TOOL],
        _dispatch,
        system_prompt=system,
        max_steps=DEFAULT_MAX_STEPS,
        verbose=True,
        arguments_hint='{"query": "Priya"}',
        repeat_note=REPEAT_NOTE,
    )
    print("--- answer ---")
    print(result.text)
    print()
    print(f"--- stop: {result.stopped} after {result.steps} model call(s) ---")
    if result.stopped == "final" and not result.tool_log:
        print("NOTE: No tool ran. A guest fact in the answer was not loaded from the store or the FAQ.")
    print()
    return 0


def _prepare_client(reset: bool) -> tuple[object, str, str] | None:
    if reset:
        reset_store(STORE, SEED)
        print(f"RESET store from {SEED.name}")
    else:
        ensure_store(STORE, SEED)
    print(describe_runtime())
    print(f"STORE={STORE}")
    print(f"DOCS={DOCS}")
    print(f"MAX_STEPS={DEFAULT_MAX_STEPS}")
    print("SESSION=fresh message list for each question; the JSON file is the durable store")
    print()
    api_key, model = require_settings()
    try:
        client = make_client()
    except Exception as exc:
        print(redact(f"Request failed: {type(exc).__name__}: {exc}", api_key), file=sys.stderr)
        return None
    return client, model, api_key


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if "--check" in args:
        return run_check()

    positional = [arg for arg in args if not arg.startswith("--")]
    reset = "--reset" in args
    quiz = "quiz" in positional
    if reset and not positional:
        reset_store(STORE, SEED)
        print(f"STORE={STORE}")
        print("Reset to the seed belief. Run the day-1 question next, without --reset.")
        return 0

    prepared = _prepare_client(reset)
    if prepared is None:
        return 1
    client, model, api_key = prepared
    try:
        if quiz:
            extra = " ".join(arg for arg in positional if arg != "quiz").strip()
            questions = [extra] if extra else list(QUIZ)
            for question in questions:
                status = _run_turn(client, model, QUIZ_SYSTEM, question)
                if status != 0:
                    return status
            print("--- active memory after quiz ---")
            print(memory_search(STORE, ""))
            return 0
        question = " ".join(arg for arg in args if not arg.startswith("--") and arg != "quiz").strip()
        question = question or DAY1_QUESTION
        return _run_turn(client, model, DAY1_SYSTEM, question)
    except Exception as exc:
        print(redact(f"Request failed: {type(exc).__name__}: {exc}", api_key), file=sys.stderr)
        print(
            "Check OPENAI_API_KEY and MODEL in .env.",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
