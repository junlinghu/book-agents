"""Build preference pairs from checker rejects.

The raw log mixes repairs with rejects that have no preferred side.
``build_pairs`` is the TODO. There is no SOLUTION.md.
"""

from __future__ import annotations

import json
from pathlib import Path


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def build_pairs(rejects: list[dict]) -> list[dict]:
    """Return preference pairs in log order.

    TODO: keep a row only when all of these hold.

    - ``preferred`` is a dict (not null).
    - ``rejected`` is a dict.
    - ``preferred`` and ``rejected`` are not equal.
    - ``rule_ids`` is a non-empty list.

    Each returned object has ``case_id``, ``rule_ids``, ``rejected``,
    ``preferred``, and ``source``. Drop the other rows. Do not invent a
    preferred cart for a reject that has none.

    The starter returns an empty list.
    """
    del rejects
    return []
