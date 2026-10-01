"""Durable memory in tutorial/var/memory.json."""

import json

from tutorial.common.harness import VAR, register

MEMORY_PATH = VAR / "memory.json"


def reset_memory():
    """Start this lesson from an empty durable store. Session messages are separate."""
    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    MEMORY_PATH.write_text("[]\n", encoding="utf-8")


def _load_memory():
    if not MEMORY_PATH.is_file():
        return []
    return json.loads(MEMORY_PATH.read_text(encoding="utf-8"))


def _save_memory(rows):
    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    MEMORY_PATH.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")


def memory_set(args):
    text = str(args.get("text", "")).strip()
    scope = str(args.get("scope", "")).strip()
    kind = str(args.get("kind", "")).strip()
    source = str(args.get("source", "")).strip()
    if kind not in {"preference", "constraint", "belief"}:
        return "ERROR: kind must be preference, constraint, or belief."
    if not text or not scope or not source:
        return "ERROR: text, scope, and source are required."
    if len(text) > 500:
        return "ERROR: text is too long."
    rows = _load_memory()
    record = {
        "id": "mem_" + str(len(rows) + 1),
        "text": text,
        "scope": scope,
        "kind": kind,
        "source": source,
        "forgotten": False,
    }
    rows.append(record)
    _save_memory(rows)
    return "SAVED id=" + record["id"] + " kind=" + kind + " scope=" + scope


def memory_search(args):
    query = str(args.get("query", "")).strip().lower()
    scope = str(args.get("scope", "")).strip()
    rows = [row for row in _load_memory() if not row.get("forgotten")]
    if scope:
        rows = [row for row in rows if row["scope"] == scope]
    if query:
        rows = [
            row for row in rows
            if query in row["text"].lower() or query in row["scope"].lower()
        ]
    if not rows:
        return "MATCHES\n(none)"
    lines = ["MATCHES"]
    for row in rows:
        lines.append(
            "- id=" + row["id"]
            + " kind=" + row["kind"]
            + " scope=" + row["scope"]
            + " text=" + row["text"]
        )
    return "\n".join(lines)


register(
    "memory_set",
    "Append one durable memory row to JSON. scope is customer:<name> or shop. "
    "kind is preference, constraint, or belief. This survives a new message list.",
    {
        "text": {"type": "string"},
        "scope": {"type": "string"},
        "kind": {"type": "string"},
        "source": {"type": "string"},
    },
    ["text", "scope", "kind", "source"],
    memory_set,
)
register(
    "memory_search",
    "Search durable memory. Session chat is not searched. Forgotten rows are skipped.",
    {
        "query": {"type": "string"},
        "scope": {"type": "string", "description": "Optional exact scope, such as customer:priya or shop."},
    },
    [],
    memory_search,
)

__all__ = [
    "MEMORY_PATH",
    "memory_search",
    "memory_set",
    "reset_memory",
]
