"""A plan step that runs before the tool loop.

One model call, with an empty tool list, writes a short ordered plan.
The loop then acts. The plan cannot add tools. This module does not
import the loop. Importing it registers ``draft_plan`` on ``HOOKS``.
"""

from tutorial.common.hooks import set_hook
from tutorial.common.tools import TOOLS
from tutorial.runtime import chat

PLAN_BRIEF = (
    "You write a short plan for the Harbor Jar seller. "
    "The person asking is a customer on the store website. "
    "Reply with 3 to 6 numbered steps. "
    "Each step names one registered tool and the argument you would pass. "
    "get_store_fact takes a topic, never a filename. "
    "query_catalog takes a product name or sku, never SQL. "
    "Do not call any tool in this reply. "
    "Do not name charge_card, cancel_order, or send_customer_email. "
    "The plan cannot grant tools or change prices. "
    "End with the line PLAN_READY."
)


def plan_steps(text):
    """Return the numbered lines of a plan. Empty when the text is not a list."""
    steps = []
    for line in (text or "").splitlines():
        stripped = line.strip()
        if not stripped or not stripped[0].isdigit():
            continue
        if len(stripped) > 1 and stripped[1] in ".)":
            steps.append(stripped)
        elif len(stripped) > 2 and stripped[1].isdigit() and stripped[2] in ".)":
            steps.append(stripped)
    return steps


def draft_plan(user_text, system):
    """One Chat Completions call with no tools. Returns the plan and its usage."""
    del system
    names = [tool["function"]["name"] for tool in TOOLS]
    allowed = ", ".join(names) if names else "(none)"
    brief = PLAN_BRIEF + " Registered tools right now: " + allowed + ". Name only those."
    turned = chat(
        [
            {"role": "system", "content": brief},
            {"role": "user", "content": user_text},
        ],
        tools=[],
    )
    text = (turned["content"] or "").strip() or "(empty plan)"
    print("PLAN:")
    print(text)
    print()
    return {
        "text": text,
        "prompt_tokens": turned["usage"]["prompt_tokens"],
        "completion_tokens": turned["usage"]["completion_tokens"],
        "latency_ms": turned["latency_ms"],
    }


set_hook("draft_plan", draft_plan)

__all__ = [
    "draft_plan",
    "plan_steps",
]
