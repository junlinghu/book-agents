"""Folders the tutorial keeps on disk.

Leaf modules import paths from here. This module does not import the
rest of ``tutorial.common``.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "tutorial"
DOCS = HERE / "docs"
DATA = HERE / "data"
VAR = HERE / "var"
HELP = DATA / "help"
SKILLS = DATA / "skills"
