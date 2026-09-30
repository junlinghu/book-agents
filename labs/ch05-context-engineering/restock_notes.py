#!/usr/bin/env python3
"""Tuesday huddle notes, then the next question under a context budget.

Chapter 5 lab. ``file`` writes notes with the starter dump. ``next`` asks
the morning question. ``size`` prints the budget with no model call.
``agent`` lets the model call write_note on the huddle.

  python labs/ch05-context-engineering/restock_notes.py
  python labs/ch05-context-engineering/restock_notes.py size
  python labs/ch05-context-engineering/restock_notes.py next
  python labs/ch05-context-engineering/restock_notes.py agent
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAB_DIR = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from labs.common.client import describe_runtime, make_client, redact, require_settings  # noqa: E402
from labs.common.loop import DEFAULT_MAX_STEPS, run_tool_agent  # noqa: E402
from notes_lib import (  # noqa: E402
    CONTEXT_STRATEGY,
    LIST_NOTES_TOOL,
    PER_NOTE_CAP,
    READ_NOTE_TOOL,
    TURN_BUDGET,
    WRITE_NOTE_TOOL,
    NoteSession,
    build_initial_context,
    context_chars,
    dispatch_notes,
    file_durable_notes,
    format_map,
    list_map,
    reset_notes,
)

DIALOGUE_PATH = LAB_DIR / "dialogue.md"
NOTES_DIR = LAB_DIR / "notes"

NEXT_QUESTION = (
    "The huddle is over. The notes are the only record you may use. "
    "How many cartons of oat milk did we decide to order, and how many "
    "cardamom buns on Thursday? If a note was refused, do not guess the number."
)

FILE_SYSTEM = """You are filing notes for Hearth Lane Café after the Tuesday restock huddle.
Call write_note for durable decisions: quantities, sku names, Wednesday buns, Thursday buns.
Each note must stay under the character cap in the tool description.
Do not write the rain, the porridge bowl, a recipe change, the Wi-Fi, or the picnic as if we accepted it.
The picnic was declined. The bun recipe does not change.
"""

NEXT_SYSTEM_HEAD = """You are the opener at Hearth Lane Café the morning after the Tuesday huddle.
Answer only from notes the harness shows you or that read_note returns.
If the tool result says over_budget or the notes do not contain a number, say you do not have that number.
Do not change the bun recipe. Do not invent a Wi-Fi password. Do not claim the café is catering.
"""


def _load_dialogue() -> str:
    if not DIALOGUE_PATH.is_file():
        raise SystemExit(f"Missing huddle: {DIALOGUE_PATH}")
    return DIALOGUE_PATH.read_text(encoding="utf-8")


def run_size() -> int:
    dialogue = _load_dialogue()
    print(f"DIALOGUE_CHARS={len(dialogue)}")
    print(f"PER_NOTE_CAP={PER_NOTE_CAP}")
    print(f"TURN_BUDGET={TURN_BUDGET}")
    print(f"CONTEXT_STRATEGY={CONTEXT_STRATEGY}")
    if not NOTES_DIR.is_dir() or not list_map(NOTES_DIR):
        print("NOTES=missing")
        print("Run `file` or `agent` before measuring a prompt.")
        return 0
    print("MAP:")
    print(format_map(NOTES_DIR))
    spent = context_chars(NOTES_DIR)
    print(f"INITIAL_CONTEXT_CHARS={spent}")
    if spent > TURN_BUDGET:
        print(
            f"NOTE: initial context exceeds TURN_BUDGET ({spent} > {TURN_BUDGET}). "
            "A quantity buried in that text is a candidate for context rot."
        )
    else:
        print(f"NOTE: initial context fits in TURN_BUDGET ({spent} <= {TURN_BUDGET}).")
    for name, _title, chars in list_map(NOTES_DIR):
        if chars > PER_NOTE_CAP:
            print(f"NOTE: read_note will refuse {name} ({chars} > {PER_NOTE_CAP}).")
        else:
            print(f"NOTE: read_note can return {name} ({chars} <= {PER_NOTE_CAP}).")
    return 0


def run_file() -> int:
    dialogue = _load_dialogue()
    reset_notes(NOTES_DIR)
    written = file_durable_notes(dialogue, NOTES_DIR)
    print(f"NOTES_DIR={NOTES_DIR}")
    print(f"WROTE={written}")
    print("MAP:")
    print(format_map(NOTES_DIR))
    print()
    print("Next, measure the budget, then ask the morning question:")
    print("  python labs/ch05-context-engineering/restock_notes.py size")
    print("  python labs/ch05-context-engineering/restock_notes.py next")
    return 0


def _run_model(system_prompt: str, user_text: str, tools: list[dict], session: NoteSession) -> int:
    print(describe_runtime())
    print(f"NOTES_DIR={NOTES_DIR}")
    print(f"CONTEXT_STRATEGY={CONTEXT_STRATEGY}")
    print(f"PER_NOTE_CAP={PER_NOTE_CAP}")
    print(f"TURN_BUDGET={TURN_BUDGET}")
    print(f"MAX_STEPS={DEFAULT_MAX_STEPS}")
    print(f"INITIAL_CONTEXT_CHARS={context_chars(NOTES_DIR)}")
    print(f"QUESTION: {user_text}\n")

    def dispatch(name: str, args: dict) -> str:
        return dispatch_notes(session, name, args)

    api_key, model = require_settings()
    client = make_client()
    try:
        result = run_tool_agent(
            client,
            model,
            user_text,
            tools,
            dispatch,
            system_prompt=system_prompt,
            max_steps=DEFAULT_MAX_STEPS,
            verbose=True,
            arguments_hint='{"name": "orders.md"}',
            repeat_note=(
                "\n\nNOTE: You already called this tool with the same arguments. "
                "Answer from the result you have."
            ),
        )
    except Exception as exc:
        print(redact(f"Request failed: {type(exc).__name__}: {exc}", api_key), file=sys.stderr)
        print(
            "Check OPENAI_API_KEY and MODEL in .env.",
            file=sys.stderr,
        )
        return 1

    print("--- answer ---")
    print(result.text)
    print()
    print(f"--- stop: {result.stopped} after {result.steps} model call(s) ---")
    if result.stopped == "final" and not result.tool_log and CONTEXT_STRATEGY == "map":
        print("NOTE: No tool ran. Under strategy map, a quantity needs read_note.")
    return 0


def run_next(question: str | None = None) -> int:
    if not list_map(NOTES_DIR):
        print("No notes yet. Run `file` or `agent` first.", file=sys.stderr)
        return 1
    initial = build_initial_context(NOTES_DIR)
    system = NEXT_SYSTEM_HEAD + "\n" + initial
    # The map is small. Pasted notes are the spend the budget is there to catch.
    session = NoteSession(NOTES_DIR, already_spent=0)
    return _run_model(
        system,
        question or NEXT_QUESTION,
        [LIST_NOTES_TOOL, READ_NOTE_TOOL],
        session,
    )


def run_agent() -> int:
    dialogue = _load_dialogue()
    reset_notes(NOTES_DIR)
    session = NoteSession(NOTES_DIR, already_spent=0)
    user = (
        "File durable notes from this huddle. Use write_note. "
        "Do not paste the whole transcript into one note.\n\n"
        + dialogue
    )
    status = _run_model(
        FILE_SYSTEM,
        user,
        [WRITE_NOTE_TOOL, LIST_NOTES_TOOL],
        session,
    )
    print("--- notes on disk ---")
    print(format_map(NOTES_DIR) or "(none)")
    return status


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    command = args[0] if args else "file"
    if command == "file":
        return run_file()
    if command == "size":
        return run_size()
    if command == "next":
        extra = " ".join(args[1:]).strip()
        return run_next(extra or None)
    if command == "agent":
        return run_agent()
    print(
        "Use file, size, next, or agent.\n"
        "  python labs/ch05-context-engineering/restock_notes.py file",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
