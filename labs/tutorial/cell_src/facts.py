from labs.tutorial.common.tools import read_file as read_docs_file


def _read_docs(path):
    """Read one shop document. The path jail lives in ``labs.tutorial.common.tools``."""
    if not isinstance(path, str):
        return "ERROR: path must be a string. Example: policy.md"
    return read_docs_file(str(DOCS), path)


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
    mapping = {
        "returns": ("policy.md", "Returns"),
        "shipping": ("policy.md", "Shipping"),
        "hours": ("faq.md", "Where and when"),
        "allergens": ("faq.md", "Allergens"),
    }
    if topic not in mapping:
        return "ERROR: topic must be returns, shipping, hours, or allergens."
    path, heading = mapping[topic]
    document = _read_docs(path)
    if document.startswith("ERROR:"):
        return document
    body = _section(document, heading)
    if not body:
        return "ERROR: " + heading + " is missing from " + path + "."
    return "TOPIC: " + topic + "\nSOURCE: docs/" + path + "\n\n" + body


register(
    "get_shop_fact",
    "Look up one Hearth Lane rule. topic is returns, shipping, hours, or allergens. "
    "The result quotes docs/policy.md or docs/faq.md.",
    {"topic": {"type": "string", "description": "returns, shipping, hours, or allergens"}},
    ["topic"],
    get_shop_fact,
)
