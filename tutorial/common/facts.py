"""The tutorial 1 shop-fact tool, importable by later lessons.

The model passes a topic. This module maps that topic to a file and a
section. The path never appears in the tool schema. The path jail is
``tutorial.common.read_file``, which is not itself a tool.
"""

from tutorial.common.harness import DOCS
from tutorial.common.read_file import read_file
from tutorial.common.tools import register

# topic -> (filename under tutorial/docs, markdown heading)
TOPICS = {
    "returns": ("policy.md", "Returns"),
    "shipping": ("policy.md", "Shipping"),
    "damage": ("policy.md", "Damage in transit"),
    "delivery": ("policy.md", "Local delivery"),
    "hours": ("faq.md", "Where and when"),
    "menu": ("faq.md", "Counter menu (dine-in and takeaway)"),
    "allergens": ("faq.md", "Allergens"),
    "wifi": ("faq.md", "Wi-Fi and payment"),
}


def topic_list():
    """Comma-separated topic names, in the order the tool accepts them."""
    return ", ".join(TOPICS)


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


def get_shop_fact(args):
    """Return one policy or FAQ section. The model names a topic; this function opens the file."""
    topic = str(args.get("topic", "")).strip().lower()
    if topic not in TOPICS:
        return "ERROR: topic must be one of: " + topic_list() + "."
    path, heading = TOPICS[topic]
    document = read_file(str(DOCS), path)
    if document.startswith("ERROR:"):
        return document
    body = _section(document, heading)
    if not body:
        return "ERROR: " + heading + " is missing from the shop documents."
    return "TOPIC: " + topic + "\nSOURCE: docs/" + path + "\n\n" + body


register(
    "get_shop_fact",
    "Look up one Hearth Lane rule. Pass a topic, not a filename. "
    "topic is one of: " + topic_list() + ". "
    "The result is the shop's text for that topic.",
    {
        "topic": {
            "type": "string",
            "description": "One topic: " + topic_list() + ".",
        }
    },
    ["topic"],
    get_shop_fact,
)

__all__ = [
    "TOPICS",
    "get_shop_fact",
    "topic_list",
]
