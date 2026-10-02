"""Store-fact tool. The model passes a topic, never a filename.

This module maps the topic to a file and a heading. The path never
appears in the tool schema. The path jail is ``tutorial.common.read_file``,
which is not itself a tool.
"""

from tutorial.common.paths import DOCS
from tutorial.common.read_file import read_file
from tutorial.common.sections import section_body
from tutorial.common.tools import register

# topic -> (filename under tutorial/docs, markdown heading)
TOPICS = {
    "returns": ("policy.md", "Returns"),
    "shipping": ("policy.md", "Shipping"),
    "damage": ("policy.md", "Damage in transit"),
    "discounts": ("policy.md", "Discounts"),
    "hours": ("faq.md", "Hours and pickup"),
    "allergens": ("faq.md", "Allergens"),
    "gifts": ("faq.md", "Gift boxes"),
}


def topic_list():
    """Comma-separated topic names, in the order the tool accepts them."""
    return ", ".join(TOPICS)


def get_store_fact(args):
    """Return one policy or FAQ section. The model names a topic; this function opens the file."""
    topic = str(args.get("topic", "")).strip().lower()
    if topic not in TOPICS:
        return "ERROR: topic must be one of: " + topic_list() + "."
    path, heading = TOPICS[topic]
    document = read_file(str(DOCS), path)
    if document.startswith("ERROR:"):
        return document
    # read_file prefixes "PATH: ...". The section parser needs the markdown only.
    markdown = document.split("\n\n", 1)[1] if document.startswith("PATH:") else document
    body = section_body(markdown, heading)
    if not body:
        return "ERROR: " + heading + " is missing from the store documents."
    return "TOPIC: " + topic + "\nSOURCE: docs/" + path + "\n\n" + body


register(
    "get_store_fact",
    "Look up one Harbor Jar rule for a customer. Pass a topic, not a filename. "
    "topic is one of: " + topic_list() + ". "
    "The result is the store's text for that topic.",
    {
        "topic": {
            "type": "string",
            "description": "One topic: " + topic_list() + ".",
        }
    },
    ["topic"],
    get_store_fact,
)

__all__ = [
    "TOPICS",
    "get_store_fact",
    "topic_list",
]
