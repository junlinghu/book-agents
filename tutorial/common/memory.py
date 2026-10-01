"""Durable guest preferences in tutorial/data/customer_preference.md.

The model passes a guest name. This module returns that heading's section.
The path never appears in the tool schema.
"""

from tutorial.common.harness import DATA
from tutorial.common.tools import register

PREFERENCE_PATH = DATA / "customer_preference.md"


def _headings(markdown):
    names = []
    for line in markdown.splitlines():
        if line.startswith("## "):
            names.append(line[3:].strip())
    return names


def _section(markdown, heading):
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


def guest_list():
    """Comma-separated guest names, in file order."""
    if not PREFERENCE_PATH.is_file():
        return "(none)"
    names = _headings(PREFERENCE_PATH.read_text(encoding="utf-8"))
    if not names:
        return "(none)"
    return ", ".join(names)


def get_preference(args):
    """Return one guest's entry. The model names the guest; this function opens the file."""
    name = str(args.get("name", "")).strip()
    if not name:
        return "ERROR: name is required. Example: Priya."
    if not PREFERENCE_PATH.is_file():
        return "ERROR: customer_preference.md is missing."
    document = PREFERENCE_PATH.read_text(encoding="utf-8")
    match = None
    for heading in _headings(document):
        if heading.lower() == name.lower():
            match = heading
            break
    if match is None:
        return (
            "ERROR: no preference entry for " + name
            + ". Known guests: " + guest_list() + "."
        )
    body = _section(document, match)
    if not body:
        return "ERROR: " + match + " has an empty entry."
    return "CUSTOMER: " + match + "\nSOURCE: data/customer_preference.md\n\n" + body


register(
    "get_preference",
    "Look up one guest in the shared preference file. Pass a name, not a filename. "
    "name is one of: " + guest_list() + ". "
    "The result is that guest's entry only.",
    {
        "name": {
            "type": "string",
            "description": "One guest name: " + guest_list() + ".",
        }
    },
    ["name"],
    get_preference,
)

__all__ = [
    "PREFERENCE_PATH",
    "get_preference",
    "guest_list",
]
