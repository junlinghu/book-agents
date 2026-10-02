"""Markdown heading helpers. Not a Chat Completions tool."""


def heading_names(markdown):
    """Return the ``##`` headings, in file order."""
    names = []
    for line in markdown.splitlines():
        if line.startswith("## "):
            names.append(line[3:].strip())
    return names


def section_body(markdown, heading):
    """Return the body under ``## heading``, up to the next heading."""
    lines = markdown.splitlines()
    start = None
    prefix = "## " + heading
    for index, line in enumerate(lines):
        if line.strip() == prefix:
            start = index + 1
            break
    if start is None:
        return ""
    body = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        body.append(line)
    return "\n".join(body).strip()


__all__ = [
    "heading_names",
    "section_body",
]
