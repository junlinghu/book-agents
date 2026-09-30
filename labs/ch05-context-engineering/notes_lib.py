"""Notes for the Tuesday huddle: a dump, a map, and a budget.

``file_durable_notes`` is the starter. It writes one transcript the next
turn cannot reload under the cap. Split the huddle into small notes, and
set ``CONTEXT_STRATEGY`` to ``"map"`` so the next question pulls a note
by name instead of pasting the folder.
"""

from __future__ import annotations

import re
from pathlib import Path

from labs.common.payload import tool_payload

# Characters allowed in one note the model is allowed to read back.
PER_NOTE_CAP = 800

# Characters the next turn may spend on the map plus notes it reads.
TURN_BUDGET = 2000

# "paste" copies every note into the system prompt.
# "map" copies only the catalog. The model calls read_note.
# TODO(learner): set this to "map" once the huddle is split into notes
# that fit under PER_NOTE_CAP.
CONTEXT_STRATEGY = "paste"

WRITE_NOTE_TOOL: dict = {
    "type": "function",
    "function": {
        "name": "write_note",
        "description": (
            "Write one durable markdown note under notes/. "
            "name is a file name such as orders.md or bakery.md. "
            f"The body must be at most {PER_NOTE_CAP} characters. "
            "Do not write chatter, a recipe change, or a Wi-Fi password."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "File name ending in .md."},
                "body": {"type": "string", "description": "The note, including a title line."},
            },
            "required": ["name", "body"],
        },
    },
}

LIST_NOTES_TOOL: dict = {
    "type": "function",
    "function": {
        "name": "list_notes",
        "description": (
            "List note files with a one-line title. This is the map. "
            "It does not include the body. Call read_note for a body."
        ),
        "parameters": {"type": "object", "properties": {}},
    },
}

READ_NOTE_TOOL: dict = {
    "type": "function",
    "function": {
        "name": "read_note",
        "description": (
            "Read one note by file name. Fails when the note is longer than "
            f"{PER_NOTE_CAP} characters, or when the turn budget is spent. "
            "A refusal is JSON. Do not guess a quantity the note did not return."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "File name from list_notes."},
            },
            "required": ["name"],
        },
    },
}


def tool_result(
    ok: bool,
    code: str,
    message: str,
    *,
    retryable: bool = False,
    hint: str = "",
    **extra: object,
) -> str:
    return tool_payload(ok, code, message, retryable=retryable, hint=hint, **extra)


def reset_notes(notes_dir: Path) -> None:
    """Delete markdown notes so a filing run starts empty."""
    notes_dir.mkdir(parents=True, exist_ok=True)
    for path in notes_dir.glob("*.md"):
        path.unlink()


def safe_note_name(name: str) -> str | None:
    """Return a single ``*.md`` file name, or None when the name is illegal."""
    if not isinstance(name, str):
        return None
    text = name.strip().replace("\\", "/")
    if "/" in text or text.startswith("."):
        return None
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,40}\.md", text):
        return None
    return text


def file_durable_notes(dialogue: str, notes_dir: Path) -> list[str]:
    """Write the notes the next turn is allowed to reload.

    TODO(learner): replace this body. Write small notes the morning shift
    can open by name, each under PER_NOTE_CAP characters. Keep quantities
    and the bun plan. Keep a lossy summary in its own file if you want one,
    and do not put the numbers only there. Leave out rain, the porridge
    bowl, the sweetness aside as a recipe change, the declined picnic, and
    any Wi-Fi guess. Do not write ``transcript.md``: the full huddle is over
    the read cap, so the next turn cannot open it.

    The starter writes the whole dialogue into ``transcript.md`` and returns.
    """
    notes_dir.mkdir(parents=True, exist_ok=True)
    (notes_dir / "transcript.md").write_text(dialogue, encoding="utf-8")
    return ["transcript.md"]


def note_title(path: Path) -> str:
    """First markdown heading, or the file name when the note has none."""
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip() or path.name
    return path.name


def list_map(notes_dir: Path) -> list[tuple[str, str, int]]:
    """Return ``(name, title, characters)`` for each note, sorted by name."""
    if not notes_dir.is_dir():
        return []
    rows = []
    for path in sorted(notes_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        rows.append((path.name, note_title(path), len(text)))
    return rows


def format_map(notes_dir: Path) -> str:
    rows = list_map(notes_dir)
    if not rows:
        return "(no notes)"
    lines = [f"{name} — {title} ({chars} chars)" for name, title, chars in rows]
    return "\n".join(lines)


def build_initial_context(notes_dir: Path) -> str:
    """Text placed in the system prompt before the model speaks.

    ``paste`` spends the budget up front. ``map`` spends almost none, and
    leaves the bodies behind ``read_note``.
    """
    catalog = format_map(notes_dir)
    if CONTEXT_STRATEGY == "map":
        return (
            "Note map (names and titles only; call read_note for a body):\n"
            f"{catalog}\n"
        )
    if CONTEXT_STRATEGY != "paste":
        return (
            f"CONTEXT_STRATEGY {CONTEXT_STRATEGY!r} is not 'paste' or 'map'. "
            "Fix notes_lib.py.\n"
        )
    chunks = [
        "The harness pasted every note into this prompt.",
        "Note map:",
        catalog,
        "",
    ]
    for name, _title, _chars in list_map(notes_dir):
        body = (notes_dir / name).read_text(encoding="utf-8")
        chunks.append(f"----- {name} -----")
        chunks.append(body)
        chunks.append("")
    return "\n".join(chunks)


def context_chars(notes_dir: Path) -> int:
    return len(build_initial_context(notes_dir))


class NoteSession:
    """Per-turn budget for read_note. One session is one question."""

    def __init__(self, notes_dir: Path, already_spent: int = 0) -> None:
        self.notes_dir = notes_dir
        self.spent = already_spent

    def list_notes(self) -> str:
        return tool_result(
            True,
            "ok",
            "Note map.",
            map=format_map(self.notes_dir),
            spent=self.spent,
            budget=TURN_BUDGET,
        )

    def read_note(self, name: str) -> str:
        safe = safe_note_name(name)
        if safe is None:
            return tool_result(
                False,
                "bad_name",
                "name must be a single file such as orders.md.",
                hint="Call list_notes and pass one of those names. No slashes.",
            )
        path = self.notes_dir / safe
        if not path.is_file():
            known = ", ".join(row[0] for row in list_map(self.notes_dir)) or "(none)"
            return tool_result(
                False,
                "not_found",
                f"{safe} is not in notes/.",
                hint=f"Available: {known}",
            )
        body = path.read_text(encoding="utf-8")
        if len(body) > PER_NOTE_CAP:
            return tool_result(
                False,
                "over_budget",
                f"{safe} is {len(body)} characters. The per-note cap is {PER_NOTE_CAP}.",
                retryable=False,
                hint=(
                    "Do not guess the quantities in a file the tool refused. "
                    "File a shorter note and read that name."
                ),
                chars=len(body),
                cap=PER_NOTE_CAP,
            )
        if self.spent + len(body) > TURN_BUDGET:
            return tool_result(
                False,
                "over_budget",
                f"Reading {safe} would spend {self.spent + len(body)} of {TURN_BUDGET} characters.",
                hint="Answer from notes already read, or read a shorter note.",
                spent=self.spent,
                budget=TURN_BUDGET,
            )
        self.spent += len(body)
        return tool_result(
            True,
            "ok",
            f"Read {safe}.",
            name=safe,
            chars=len(body),
            spent=self.spent,
            budget=TURN_BUDGET,
            body=body,
        )

    def write_note(self, name: str, body: str) -> str:
        safe = safe_note_name(name)
        if safe is None:
            return tool_result(
                False,
                "bad_name",
                "name must be a single file such as orders.md.",
                hint="Use letters, digits, hyphens, and a .md suffix. No slashes.",
            )
        if not isinstance(body, str) or not body.strip():
            return tool_result(
                False,
                "empty_note",
                "body is required.",
                hint="Include the quantity or the plan in the body.",
            )
        if len(body) > PER_NOTE_CAP:
            return tool_result(
                False,
                "over_budget",
                f"body is {len(body)} characters. The cap is {PER_NOTE_CAP}.",
                hint="Split durable facts into separate notes. Do not paste the huddle.",
            )
        self.notes_dir.mkdir(parents=True, exist_ok=True)
        (self.notes_dir / safe).write_text(body, encoding="utf-8")
        return tool_result(True, "written", f"Wrote {safe}.", name=safe, chars=len(body))


def dispatch_notes(session: NoteSession, name: str, args: dict) -> str:
    if name == "list_notes":
        return session.list_notes()
    if name == "read_note":
        note = args.get("name", "")
        return session.read_note(note if isinstance(note, str) else "")
    if name == "write_note":
        note = args.get("name", "")
        body = args.get("body", "")
        if not isinstance(note, str):
            note = ""
        if not isinstance(body, str):
            body = ""
        return session.write_note(note, body)
    return tool_result(
        False,
        "unknown_tool",
        f"Unknown tool {name!r}.",
        hint="Use list_notes, read_note, or write_note.",
    )
