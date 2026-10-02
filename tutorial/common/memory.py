"""Durable customer preferences in tutorial/data/customer_preference.md.

The model passes a customer name. This module returns that heading's
section. The path never appears in the tool schema. Both sample
customers use the same fields.
"""

from tutorial.common.paths import DATA
from tutorial.common.sections import heading_names, section_body
from tutorial.common.tools import register

PREFERENCE_PATH = DATA / "customer_preference.md"
FIELDS = ("Name", "Allergy", "Favorite", "Last order", "Notes")


def customer_list():
    """Comma-separated customer names, in file order."""
    if not PREFERENCE_PATH.is_file():
        return "(none)"
    names = heading_names(PREFERENCE_PATH.read_text(encoding="utf-8"))
    if not names:
        return "(none)"
    return ", ".join(names)


def get_preference(args):
    """Return one customer's entry. The model names the customer; this function opens the file."""
    name = str(args.get("name", "")).strip()
    if not name:
        return "ERROR: name is required. Example: Maya."
    if not PREFERENCE_PATH.is_file():
        return "ERROR: customer_preference.md is missing."
    document = PREFERENCE_PATH.read_text(encoding="utf-8")
    match = None
    for heading in heading_names(document):
        if heading.lower() == name.lower():
            match = heading
            break
    if match is None:
        return (
            "ERROR: no preference entry for " + name
            + ". Known customers: " + customer_list() + "."
        )
    body = section_body(document, match)
    if not body:
        return "ERROR: " + match + " has an empty entry."
    return "CUSTOMER: " + match + "\nSOURCE: data/customer_preference.md\n\n" + body


register(
    "get_preference",
    "Look up one customer in the shared preference file. Pass a name, not a filename. "
    "Known customers: " + customer_list() + ". "
    "The result is that customer's entry only. The chat transcript is not this file.",
    {
        "name": {
            "type": "string",
            "description": "One customer name: " + customer_list() + ".",
        }
    },
    ["name"],
    get_preference,
)

__all__ = [
    "FIELDS",
    "PREFERENCE_PATH",
    "customer_list",
    "get_preference",
]
