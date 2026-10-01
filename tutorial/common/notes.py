"""Huddle notes: titles in the prompt, bodies on request."""

from tutorial.common.harness import DATA
from tutorial.common.tools import register

NOTES = DATA / "notes"
PER_NOTE_CAP = 500
TURN_BUDGET = 600


def _note_path(name):
    if not isinstance(name, str) or not name.strip():
        return "ERROR: name is required. Example: oat-milk.md"
    cleaned = name.strip().replace("\\", "/")
    if "/" in cleaned or cleaned.startswith("."):
        return "ERROR: name must be a file in the notes catalog, not a path."
    if not cleaned.endswith(".md"):
        return "ERROR: notes are markdown files, such as oat-milk.md."
    candidate = (NOTES / cleaned).resolve()
    if candidate.parent != NOTES.resolve():
        return "ERROR: name escapes the notes folder."
    if not candidate.is_file():
        return "ERROR: " + cleaned + " is not in the catalog."
    return candidate


def _note_title(text):
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return "(untitled)"


def list_notes(args):
    """Titles and sizes only. Bodies stay on disk until read_note."""
    del args
    lines = ["NOTES"]
    for path in sorted(NOTES.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        lines.append(
            "- " + path.name + " | " + _note_title(text) + " | " + str(len(text)) + " chars"
        )
    return "\n".join(lines)


def read_note(args):
    found = _note_path(args.get("name", ""))
    if isinstance(found, str):
        return found
    text = found.read_text(encoding="utf-8")
    if len(text) > PER_NOTE_CAP:
        return (
            "ERROR: " + found.name + " is " + str(len(text))
            + " characters. The per-note cap is " + str(PER_NOTE_CAP)
            + ". File a shorter note."
        )
    return "NOTE: " + found.name + "\n\n" + text


def paste_chars():
    total = 0
    for path in NOTES.glob("*.md"):
        total += len(path.read_text(encoding="utf-8"))
    return total


register(
    "list_notes",
    "List huddle notes by name, title, and size. Does not return bodies.",
    {},
    [],
    list_notes,
)
register(
    "read_note",
    "Read one short note by file name, such as oat-milk.md. "
    "A note over the per-note cap returns ERROR. The picnic note is an example.",
    {"name": {"type": "string", "description": "File name from list_notes."}},
    ["name"],
    read_note,
)

__all__ = [
    "NOTES",
    "PER_NOTE_CAP",
    "TURN_BUDGET",
    "list_notes",
    "paste_chars",
    "read_note",
]
