"""Agent loop for tutorial 2 onward.

One step is one model call. The loop stops on a final answer, on
``max_steps``, or when the same tool call repeats.

``run_agent`` starts a fresh message list. ``run_turn`` continues a list
the caller kept, which is how tutorial 15 holds one customer visit.
``tutorial.common.chat_session`` is that caller. This module does not
import it.

Optional pieces register on ``HOOKS``: a plan (tutorial 14), a gate
(tutorial 9), trace spans (tutorial 12), and a token ledger with a read
cache (tutorial 13). Those stay off until the lesson imports them.

This module imports the tool registry. It does not import the leaf
modules that register tools.
"""

import json

from tutorial.common.hooks import HOOKS
from tutorial.common.messages import assistant_message, preview
from tutorial.common.tools import TOOLS, call_tool
from tutorial.runtime import chat

MAX_IDENTICAL_CALLS = 2
REPEAT_NOTE = (
    "\n\nNOTE: You already made this call. Answer the question without repeating it."
)


def run_agent(user_text, system, max_steps=6, confirmed_tokens=None, trace_id="tutorial"):
    """Perceive one new thread, let the model reason, act, and observe.

    The message list starts here. A later lesson that must remember the
    customer calls :func:`run_turn` on a list it kept.
    """
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_text},
    ]
    usage_rows = []
    plan = attach_plan(messages, user_text, usage_rows)
    return run_turn(
        messages,
        max_steps=max_steps,
        confirmed_tokens=confirmed_tokens,
        trace_id=trace_id,
        usage_rows=usage_rows,
        plan=plan,
    )


def attach_plan(messages, user_text, usage_rows):
    """Draft a plan once and attach it to the system message.

    No plan hook means an empty string and an unchanged system message.
    The plan cannot add tools. Returns the plan text.
    """
    draft_plan = HOOKS.get("draft_plan")
    if not draft_plan:
        return ""
    system = messages[0]["content"]
    drafted = draft_plan(user_text, system)
    plan = (drafted.get("text") or "").strip()
    if HOOKS.get("cached_call") is not None:
        usage_rows.append({
            "step": 0,
            "prompt_tokens": drafted.get("prompt_tokens", 0),
            "completion_tokens": drafted.get("completion_tokens", 0),
            "latency_ms": drafted.get("latency_ms", 0),
        })
        print(
            "usage: step=plan"
            + " prompt_tokens=" + str(drafted.get("prompt_tokens", 0))
            + " completion_tokens=" + str(drafted.get("completion_tokens", 0))
            + " latency_ms=" + str(drafted.get("latency_ms", 0))
        )
    if plan:
        messages[0] = {
            "role": "system",
            "content": (
                system
                + "\n\nPLAN (written before any tool call; it cannot add tools):\n"
                + plan
            ),
        }
    return plan


def run_turn(
    messages,
    max_steps=6,
    confirmed_tokens=None,
    trace_id="tutorial",
    spans=None,
    usage_rows=None,
    plan="",
):
    """Run one customer turn on an existing message list.

    ``messages`` already ends with this turn's user message. Assistant
    and tool rows are appended. Stops on a final answer, ``max_steps``,
    or a repeated call. ``pending_tokens`` lists confirm-tier calls that
    waited during this turn.
    """
    gate_call = HOOKS.get("gate_call")
    format_decision = HOOKS.get("format_decision")
    root_span = HOOKS.get("root_span")
    make_span = HOOKS.get("make_span")
    route_task = HOOKS.get("route_task")
    costing = HOOKS.get("cached_call") is not None
    confirmed = set(confirmed_tokens or [])
    if spans is None:
        spans = []
    if usage_rows is None:
        usage_rows = []
    seen = {}
    log = []
    pending = []
    if root_span:
        spans.append(root_span(trace_id))
    for step in range(1, max_steps + 1):
        if route_task and step == 1:
            routed = route_task(_latest_user(messages))
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
            _seal(messages, text)
            return _finish(text, step, "final", log, spans, usage_rows, plan, pending)
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
                _seal(messages, text)
                return _finish(
                    text, step, "repeated_call", log, spans, usage_rows, plan, pending
                )
            if gate_call:
                decision = gate_call(call["name"], call["arguments"], confirmed)
                print(format_decision(decision))
                if decision["decision"] != "allowed":
                    result = decision["decision"].upper() + ": " + decision["reason"]
                    if decision["tier"] == "confirm":
                        result += " token=" + decision["approval_token"]
                    _remember_pending(pending, decision)
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
    _seal(messages, text)
    return _finish(text, max_steps, "max_steps", log, spans, usage_rows, plan, pending)


def _latest_user(messages):
    for message in reversed(messages):
        if message.get("role") == "user":
            return message.get("content") or ""
    return ""


def _remember_pending(pending, decision):
    if decision.get("decision") != "confirm_required":
        return
    token = decision.get("approval_token")
    if token and token not in pending:
        pending.append(token)


def _seal(messages, text):
    """Close a stopped turn so a later customer line stays valid.

    A final answer is already an assistant message. A stop in the middle
    of a tool batch still needs one tool row per id, then the stop text.
    """
    pending_ids = []
    answered = set()
    for message in messages:
        if message.get("role") == "assistant" and message.get("tool_calls"):
            pending_ids = [call.get("id") for call in message["tool_calls"]]
            answered = set()
        elif message.get("role") == "tool":
            answered.add(message.get("tool_call_id"))
    for call_id in pending_ids:
        if call_id and call_id not in answered:
            messages.append({
                "role": "tool",
                "tool_call_id": call_id,
                "content": text,
            })
    last = messages[-1] if messages else {}
    if last.get("role") != "assistant" or last.get("tool_calls"):
        messages.append({"role": "assistant", "content": text})


def _invoke(call):
    cached_call = HOOKS.get("cached_call")
    if cached_call:
        result, _hit = cached_call(call)
        return result
    return call_tool(call)


def _finish(text, steps, stopped, log, spans, usage_rows, plan, pending):
    return {
        "text": text,
        "steps": steps,
        "stopped": stopped,
        "tool_log": log,
        "spans": spans,
        "usage": usage_rows,
        "plan": plan,
        "pending_tokens": list(pending),
    }
