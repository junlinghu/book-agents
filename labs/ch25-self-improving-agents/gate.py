#!/usr/bin/env python3
"""Decide whether a proposed skill patch may merge.

``suite.py`` scores the Chapter 12 cases. You decide the merge. The
function must not write files. There is no SOLUTION.md.
"""

from __future__ import annotations


def patch_surface_ok(patch: dict) -> bool:
    """Return whether every path in ``patch['files']`` is a skill file.

    TODO: return true only when ``files`` is a non-empty list of
    strings and each string is a single skill path.

    - Use forward slashes. Reject backslashes and absolute paths.
    - Reject empty segments and ``.`` or ``..`` segments.
    - The only accepted shape is ``skills/<name>.md``.
    - ``<name>`` is one or more letters, digits, underscores, or hyphens.
    - One bad path fails the whole list. A skill plus a grader is not ok.

    The starter raises ``NotImplementedError``.
    """
    del patch
    raise NotImplementedError(
        "patch_surface_ok is not implemented. See the lab README."
    )


def decide_merge(patch: dict, report: dict, reviewer: str) -> str:
    """Return ``merge`` or ``reject``.

    TODO: return ``merge`` only when all of these hold.

    - ``reviewer`` is a string, and after stripping whitespace it is
      non-empty and is not ``agent`` in any capitalization.
    - ``patch_surface_ok(patch)`` is true.
    - ``report`` is a dict, ``report['passed']`` is true, and
      ``report['failures']`` is empty.

    Otherwise return ``reject``. Do not write the proposal onto the
    skill file. A person does that after you return ``merge``.

    The starter raises ``NotImplementedError``.
    """
    del patch, report, reviewer
    raise NotImplementedError(
        "decide_merge is not implemented. See the lab README."
    )
