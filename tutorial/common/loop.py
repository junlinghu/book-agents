"""Agent loop for tutorials 3 through 15.

One step is one model call. The loop stops on a final answer, on
``max_steps``, or when the same tool call repeats.

Later lessons register optional pieces on ``HOOKS``: a gate (tutorial 10),
trace spans (tutorial 13), and a token ledger with a read cache (tutorial 14).
Those stay off until the lesson imports them.
"""

import json

from tutorial.common.harness import HOOKS, assistant_message, preview
from tutorial.common.tools import TOOLS, call_tool
from tutorial.runtime import chat

MAX_IDENTICAL_CALLS = 2
REPEAT_NOTE = (
    "\n\nNOTE: You already made this call. Answer the question without repeating it."
)


def run_agent(user_text, system, max_steps=6, confirmed_tokens=None, trace_id="tutorial"):
    """Perceive the thread, let the model reason, act on tool calls, observe the results."""
    gate_call = HOOKS.get("gate_call")
    format_decision = HOOKS.get("format_decision")
    root_span = HOOKS.get("root_span")
    make_span = HOOKS.get("make_span")
    route_task = HOOKS.get("route_task")
    costing = HOOKS.get("cached_call") is not None
    confirmed = set(confirmed_tokens or [])
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_text},
    ]
    seen = {}
    log = []
    spans = []
    usage_rows = []
    if root_span:
        spans.append(root_span(trace_id))
    for step in range(1, max_steps + 1):
        if route_task and step == 1:
            routed = route_task(user_text)
            print(
                "route: task=" + routed["task"]
                + " model=" + routed["model"]
                + " (" + routed["reason"] + ")"
            )
        turned = chat(messages, TOOLS)
        if costing:
            usage_rows.append({
                "step": step,
                "prompt_tokens": turned["usage"]["prompt_tokens"],
                "completion_tokens": turned["usage"]["completion_tokens"],
                "latency_ms": turned["latency_ms"],
            })
            print(
                "usage: step=" + str(step)
                + " prompt_tokens=" + str(turned["usage"]["prompt_tokens"])
                + " completion_tokens=" + str(turned["usage"]["completion_tokens"])
                + " latency_ms=" + str(turned["latency_ms"])
            )
        messages.append(assistant_message(turned))
        calls = turned["tool_calls"] or []
        if not calls:
            text = (turned["content"] or "").strip() or "(empty answer)"
            print("stop: final after " + str(step) + " model call(s)")
            return _finish(text, step, "final", log, spans, usage_rows)
        for call in calls:
            signature = (
                call["name"] + " "
                + json.dumps(call["arguments"], sort_keys=True, default=str)
            )
            count = seen.get(signature, 0) + 1
            seen[signature] = count
            if count > MAX_IDENTICAL_CALLS:
                log.append("step " + str(step) + ": repeated " + signature)
                print("stop: repeated_call after " + str(step) + " model call(s)")
                text = (
                    "Stopped: the model repeated the same tool call ("
                    + call["name"] + ") more than " + str(MAX_IDENTICAL_CALLS)
                    + " times. The harness ended the loop."
                )
                return _finish(text, step, "repeated_call", log, spans, usage_rows)
            if gate_call:
                decision = gate_call(call["name"], call["arguments"], confirmed)
                print(format_decision(decision))
                if decision["decision"] != "allowed":
                    result = decision["decision"].upper() + ": " + decision["reason"]
                    if decision["tier"] == "confirm":
                        result += " token=" + decision["approval_token"]
                else:
                    result = _invoke(call)
            else:
                result = _invoke(call)
            if count == MAX_IDENTICAL_CALLS:
                result += REPEAT_NOTE
            first = result.splitlines()[0] if result else "(empty)"
            log.append(
                "step " + str(step) + ": " + call["name"] + " "
                + json.dumps(call["arguments"], sort_keys=True, default=str)
                + " -> " + first
            )
            if make_span:
                spans.append(make_span(trace_id, step, call["name"], result))
            messages.append({
                "role": "tool",
                "tool_call_id": call["id"],
                "content": result,
            })
            print(
                "[step " + str(step) + "] " + call["name"] + " "
                + json.dumps(call["arguments"], sort_keys=True)
            )
            print(preview(result))
            print()
    text = (
        "Stopped: reached max steps (" + str(max_steps)
        + ") without a final answer. The harness did not write one."
    )
    print("stop: max_steps after " + str(max_steps) + " model call(s)")
    return _finish(text, max_steps, "max_steps", log, spans, usage_rows)


def _invoke(call):
    cached_call = HOOKS.get("cached_call")
    if cached_call:
        result, _hit = cached_call(call)
        return result
    return call_tool(call)


def _finish(text, steps, stopped, log, spans, usage_rows):
    return {
        "text": text,
        "steps": steps,
        "stopped": stopped,
        "tool_log": log,
        "spans": spans,
        "usage": usage_rows,
    }
