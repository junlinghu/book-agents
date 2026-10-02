"""Optional loop behavior.

A gate, a trace, or a cache registers here from its lesson module.
Tutorial 14 and tutorial 15 register a plan here. ``tutorial.common.loop``
reads this dict. This module imports nothing else from the tutorial, so
those registrations do not import the loop.
"""

HOOKS = {}


def set_hook(name, fn):
    """Register one optional behavior. See ``tutorial.common.loop``."""
    HOOKS[name] = fn


__all__ = [
    "HOOKS",
    "set_hook",
]
