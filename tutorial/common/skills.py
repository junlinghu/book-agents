"""Load a procedure from tutorial/data/skills."""

import re

from tutorial.common.harness import DATA, register

SKILLS = DATA / "skills"


def load_skill(args):
    """Return a procedure. The skill is not the system prompt and it is not a tool implementation."""
    name = str(args.get("name", "")).strip().lower()
    if not re.fullmatch(r"[a-z0-9-]+", name):
        return "ERROR: skill name must be recommend or restock."
    path = SKILLS / (name + ".md")
    if not path.is_file():
        return "ERROR: unknown skill " + name + ". Use recommend or restock."
    return "SKILL: " + name + "\n\n" + path.read_text(encoding="utf-8")


register(
    "load_skill",
    "Load a portable procedure by name: recommend or restock. "
    "Follow its steps. Do not treat the skill file as a second copy of the FAQ.",
    {"name": {"type": "string", "description": "recommend or restock"}},
    ["name"],
    load_skill,
)

__all__ = [
    "load_skill",
]
