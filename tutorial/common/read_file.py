"""Path jail and document reading. Not a Chat Completions tool.

``get_store_fact`` maps a topic to a section and calls this function with
a path the program chose. The model does not see this name and does not
choose the path.
"""

import os

# Keep one read from filling the context.
MAX_FILE_CHARS = 12000


def read_file(docs_dir, path):
    """Read ``path`` if it stays inside ``docs_dir``.

    Failures return an ``ERROR:`` string. They do not raise. The caller
    sends that string back to the model when a tool asked for the file.
    """
    root = os.path.realpath(docs_dir)

    if not isinstance(path, str) or not path.strip():
        return "ERROR: path is required. Use policy.md or faq.md."

    cleaned = path.strip().replace("\\", "/")
    if os.path.isabs(cleaned):
        return "ERROR: path must stay inside docs/. Example: policy.md"

    # Split the path and drop "." pieces. ".." is a jail break.
    pieces = []
    for piece in cleaned.split("/"):
        if piece == "" or piece == ".":
            continue
        if piece == "..":
            return "ERROR: path must stay inside docs/. Example: policy.md"
        pieces.append(piece)

    # Allow "docs/policy.md" as well as "policy.md".
    if pieces and pieces[0] == "docs":
        pieces = pieces[1:]

    hidden = False
    for piece in pieces:
        if piece.startswith("."):
            hidden = True
    if not pieces or hidden:
        return (
            "ERROR: path must name a file inside docs/, such as policy.md or faq.md."
        )

    # realpath follows symlinks. If the real file sits outside docs/, refuse it.
    candidate = os.path.realpath(os.path.join(root, *pieces))
    if os.path.commonpath([root, candidate]) != root:
        return "ERROR: path escapes docs/."

    display = "docs/" + "/".join(pieces)
    if not os.path.isfile(candidate):
        names = []
        if os.path.isdir(root):
            for name in os.listdir(root):
                if name.endswith(".md"):
                    names.append(name)
        if names:
            available = ", ".join(sorted(names))
        else:
            available = "(none)"
        return "ERROR: " + display + " not found. Available markdown: " + available + "."

    try:
        with open(candidate, encoding="utf-8") as handle:
            text = handle.read()
    except UnicodeDecodeError:
        return "ERROR: " + display + " is not UTF-8 text."

    if len(text) > MAX_FILE_CHARS:
        text = text[:MAX_FILE_CHARS] + "\n\n[truncated by harness]"
    return "PATH: " + display + "\n\n" + text
