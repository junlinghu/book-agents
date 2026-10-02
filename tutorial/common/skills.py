"""Load a procedure from tutorial/data/skills.

A skill is not the system prompt and it is not a second copy of the catalog.
"""

import re

from tutorial.common.paths import SKILLS
from tutorial.common.tools import register

SKILL_NAMES = ("recommend", "gift-box")


def load_skill(args):
    """Return a procedure file. The file does not run itself."""
    name = str(args.get("name", "")).strip().lower()
    if not re.fullmatch(r"[a-z0-9-]+", name) or name not in SKILL_NAMES:
        return "ERROR: skill name must be recommend or gift-box."
    path = SKILLS / (name + ".md")
    if not path.is_file():
        return "ERROR: unknown skill " + name + ". Use recommend or gift-box."
    return "SKILL: " + name + "\n\n" + path.read_text(encoding="utf-8")


register(
    "load_skill",
    "Load a portable procedure by name: recommend or gift-box. "
    "Follow its steps. The skill is not a second copy of the catalog or the FAQ.",
    {"name": {"type": "string", "description": "recommend or gift-box"}},
    ["name"],
    load_skill,
)

__all__ = [
    "SKILL_NAMES",
    "load_skill",
]
