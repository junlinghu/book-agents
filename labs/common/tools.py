"""The only tool in the early labs: read a file under a docs directory."""

from __future__ import annotations

from pathlib import Path

# Keep tool results small enough that one read cannot fill the context.
MAX_FILE_CHARS = 12_000

READ_FILE_TOOL: dict = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": (
            "Read a UTF-8 text file from the shop docs folder. "
            "path is relative, for example policy.md or faq.md. "
            "policy.md has returns, shipping, damage, and local delivery. "
            "faq.md has hours, location, menu prices, and allergens. "
            "The result starts with a PATH header, or with ERROR if the "
            "path is missing or not allowed."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": (
                        "Relative path inside docs/, such as policy.md or faq.md."
                    ),
                }
            },
            "required": ["path"],
        },
    },
}


def read_file(docs_dir: Path, path: str) -> str:
    """Read ``path`` if it stays inside ``docs_dir``.

    Failures return an ``ERROR:`` string. They do not raise. The agent
    loop sends that string back to the model as the tool result.
    """
    root = docs_dir.resolve()
    if not isinstance(path, str) or not path.strip():
        return "ERROR: path is required. Use policy.md or faq.md."

    raw = path.strip().replace("\\", "/")
    rel = Path(raw)
    if rel.is_absolute() or any(part == ".." for part in rel.parts):
        return "ERROR: path must stay inside docs/. Example: policy.md"

    parts = [part for part in rel.parts if part != "."]
    if parts and parts[0] == "docs":
        parts = parts[1:]
    if not parts or any(part.startswith(".") for part in parts):
        return (
            "ERROR: path must name a file inside docs/, such as policy.md or faq.md."
        )

    candidate = root.joinpath(*parts).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return "ERROR: path escapes docs/."

    display = "docs/" + Path(*parts).as_posix()
    if not candidate.is_file():
        available = ", ".join(sorted(p.name for p in root.glob("*.md"))) or "(none)"
        return f"ERROR: {display} not found. Available markdown: {available}."

    try:
        text = candidate.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return f"ERROR: {display} is not UTF-8 text."

    if len(text) > MAX_FILE_CHARS:
        text = text[:MAX_FILE_CHARS] + "\n\n[truncated by harness]"
    return f"PATH: {display}\n\n{text}"
