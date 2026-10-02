"""Help articles: titles in the prompt, bodies on request.

The model passes an article id from the list, not a filesystem path.
"""

import re

from tutorial.common.paths import HELP
from tutorial.common.tools import register

ARTICLE_CAP = 500


def _slug(name):
    if not isinstance(name, str) or not name.strip():
        return "ERROR: name is required. Example: opened-jars."
    cleaned = name.strip().replace("\\", "/")
    if "/" in cleaned or cleaned.startswith("."):
        return "ERROR: name must be an article id from the list, not a path."
    if cleaned.endswith(".md"):
        cleaned = cleaned[:-3]
    if not re.fullmatch(r"[a-z0-9-]+", cleaned):
        return "ERROR: name must be an article id from the list, not a path."
    return cleaned


def _article_path(name):
    found = _slug(name)
    if isinstance(found, str) and found.startswith("ERROR:"):
        return found
    candidate = (HELP / (found + ".md")).resolve()
    if candidate.parent != HELP.resolve():
        return "ERROR: name escapes the help folder."
    if not candidate.is_file():
        return "ERROR: " + found + " is not in the help list."
    return candidate


def _title(text):
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return "(untitled)"


def list_help_articles(args):
    """Ids, titles, and sizes only. Bodies stay on disk until read_help_article."""
    del args
    lines = ["HELP ARTICLES"]
    if not HELP.is_dir():
        return "HELP ARTICLES\n(none)"
    for path in sorted(HELP.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        lines.append(
            "- " + path.stem + " | " + _title(text) + " | " + str(len(text)) + " chars"
        )
    return "\n".join(lines)


def read_help_article(args):
    """Return one short article. A body over the cap is refused."""
    found = _article_path(args.get("name", ""))
    if isinstance(found, str):
        return found
    text = found.read_text(encoding="utf-8")
    if len(text) > ARTICLE_CAP:
        return (
            "ERROR: " + found.stem + " is " + str(len(text))
            + " characters. The article cap is " + str(ARTICLE_CAP)
            + ". Use a shorter article."
        )
    return "ARTICLE: " + found.stem + "\n\n" + text


def catalog_chars():
    """Total characters if every article body were pasted at once."""
    total = 0
    if not HELP.is_dir():
        return 0
    for path in HELP.glob("*.md"):
        total += len(path.read_text(encoding="utf-8"))
    return total


register(
    "list_help_articles",
    "List Harbor Jar help articles by id, title, and size. Does not return bodies.",
    {},
    [],
    list_help_articles,
)
register(
    "read_help_article",
    "Read one help article by id, such as opened-jars. "
    "Pass an id from list_help_articles, not a filename path. "
    "An article over the cap returns ERROR. preserving-mega-guide is the example.",
    {"name": {"type": "string", "description": "Article id from list_help_articles."}},
    ["name"],
    read_help_article,
)

__all__ = [
    "ARTICLE_CAP",
    "catalog_chars",
    "list_help_articles",
    "read_help_article",
]
