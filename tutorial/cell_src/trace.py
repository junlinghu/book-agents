from tutorial.common.harness import set_hook


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
        "service": "hearth-lane-concierge",
        "name": "tool." + name,
        "status": span_status(result),
        "step": step,
        "user": {"kind": "user", "id": "counter-lead"},
        "agent": {"kind": "agent", "id": "shop-concierge"},
        "actor": {"kind": "tool", "id": name},
    }


def root_span(trace_id):
    return {
        "trace_id": trace_id,
        "span_id": trace_id + "-turn",
        "service": "hearth-lane-concierge",
        "name": "concierge.turn",
        "status": "ok",
        "user": {"kind": "user", "id": "counter-lead"},
        "agent": {"kind": "agent", "id": "shop-concierge"},
        "actor": {"kind": "agent", "id": "shop-concierge"},
    }


set_hook("make_span", make_span)
set_hook("root_span", root_span)
