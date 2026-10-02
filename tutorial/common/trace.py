"""Spans that name the customer, the agent, and the tool."""

from tutorial.common.hooks import set_hook


def span_status(result):
    if result.startswith("ERROR") or result.startswith("DENIED") or result.startswith("CONFIRM_REQUIRED"):
        if result.startswith("CONFIRM_REQUIRED"):
            return "confirm_required"
        if result.startswith("DENIED") or "DENIED" in result[:80]:
            return "denied"
        return "error"
    return "ok"


def make_span(trace_id, step, name, result):
    """One tool span. Identity is explicit. Secret-shaped values are not copied in."""
    return {
        "trace_id": trace_id,
        "span_id": trace_id + "-" + str(step) + "-" + name,
        "service": "harbor-jar",
        "name": "tool." + name,
        "status": span_status(result),
        "step": step,
        "user": {"kind": "user", "id": "customer"},
        "agent": {"kind": "agent", "id": "harbor-jar-concierge"},
        "actor": {"kind": "tool", "id": name},
    }


def root_span(trace_id):
    return {
        "trace_id": trace_id,
        "span_id": trace_id + "-turn",
        "service": "harbor-jar",
        "name": "concierge.turn",
        "status": "ok",
        "user": {"kind": "user", "id": "customer"},
        "agent": {"kind": "agent", "id": "harbor-jar-concierge"},
        "actor": {"kind": "agent", "id": "harbor-jar-concierge"},
    }


set_hook("make_span", make_span)
set_hook("root_span", root_span)

__all__ = [
    "make_span",
    "root_span",
    "span_status",
]
