"""Optional loop behavior.

Leaf modules register a gate, a trace, a cache, or a plan here.
``tutorial.common.loop`` reads this dict. This module imports nothing
else from the tutorial, so those leaves do not import the loop.
"""

HOOKS = {}


def set_hook(name, fn):
    """Register one optional behavior. See ``tutorial.common.loop``."""
    HOOKS[name] = fn


__all__ = [
    "HOOKS",
    "set_hook",
]
