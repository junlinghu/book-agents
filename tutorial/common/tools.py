"""Schemas, registration, and call dispatch for Chat Completions tools.

Lesson modules register model-facing tools here. ``get_shop_fact`` is
registered from ``tutorial.common.facts``. ``query_inventory`` is
registered from ``tutorial.common.shelf``.

Reading a document and opening the shelf are not tools. Those live in
``read_file``, ``get_db``, and ``read_db``.
"""

HANDLERS = {}
TOOLS = []


def register(name, description, properties, required, fn):
    """Add one Chat Completions tool. ``fn`` runs only if the harness allows it."""
    spec = {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }
    # Re-running a cell replaces the previous schema instead of stacking a second copy.
    TOOLS[:] = [tool for tool in TOOLS if tool["function"]["name"] != name]
    TOOLS.append(spec)
    HANDLERS[name] = fn


def call_tool(call):
    """Run one handler. Bad arguments become an ERROR string, not a crash."""
    name = call["name"]
    args = call["arguments"]
    if not isinstance(args, dict):
        return "ERROR: arguments must be a JSON object."
    if args.get("_error"):
        return "ERROR: " + str(args["_error"])
    fn = HANDLERS.get(name)
    if fn is None:
        return "ERROR: unknown tool " + repr(name) + "."
    return fn(args)


__all__ = [
    "HANDLERS",
    "TOOLS",
    "call_tool",
    "register",
]
