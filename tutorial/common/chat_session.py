"""One customer visit for tutorial 15.

The seller greets, then reads lines until the customer leaves. The message
list grows across turns. A later line can approve a note the gate held on
an earlier turn. This module imports the loop. The loop does not import it.
"""

import re
import sys

from tutorial.common.loop import attach_plan, run_turn

WELCOME = (
    "Welcome to Harbor Jar. I'm the seller on the website. "
    "Tell me what you'd like. I can recommend a jar, check a cart, "
    "and file an order note after you say yes. "
    "No card is charged. Type bye when you want to leave."
)
FAREWELL = "Bye. No card was charged from this chat."

SESSION_NOTE = (
    "\n\nThis is one visit with one customer. "
    "Earlier messages in this list already happened. Continue from them. "
    "Recommend a jar, put it in a cart, call verify_cart, then file_order_note. "
    "file_order_note waits until the customer agrees in a later message. "
    "On that waiting turn, ask them to say yes. "
    "The note is filed only when the tool result says WROTE. "
    "charge_card stays denied. No card is charged in this chat."
)
_APPROVED_MARK = "The customer has approved the order note that was waiting."
APPROVED_NOTE = (
    "\n\n" + _APPROVED_MARK + " "
    "Call file_order_note again with the same arguments. "
    "Leave charge_card alone."
)

_BYE = {"bye", "quit", "exit", "goodbye"}
_YES = re.compile(
    r"("
    r"^\s*(yes|yep|yeah|sure|ok|okay|approve|approved|confirm|confirmed)\b"
    r"|\byes\b"
    r"|\bapprove[d]?\b"
    r"|\bconfirm(?:ed)?\b"
    r"|\bgo ahead\b"
    r"|\bplease file\b"
    r"|\bfile (?:the |that |my )?note\b"
    r"|\bfile it\b"
    r")",
    re.IGNORECASE,
)
_ONLY_NO = re.compile(r"^\s*(no|nope|nah)[.!]?\s*$", re.IGNORECASE)
_REFUSE_NOTE = re.compile(
    r"("
    r"\bdon'?t file\b"
    r"|\bdo not file\b"
    r"|\bdon'?t write\b"
    r"|\bdo not write\b"
    r"|\bnever mind\b"
    r"|\bnevermind\b"
    r")",
    re.IGNORECASE,
)


def is_bye(text):
    """True when the whole line is bye, quit, exit, or goodbye."""
    word = (text or "").strip().lower().strip("!.,;: ")
    return word in _BYE


def approved_tokens(text, pending):
    """Return confirm tokens this customer line approves.

    A pasted token approves that waiting call. "Yes", "yes, file the note",
    and the same kind of reply approve every call still waiting. A bare no,
    or a refusal to file, approves nothing. A token that was never waiting
    is ignored, so a card charge cannot be granted from the sentence.
    """
    waiting = [token for token in (pending or []) if token]
    if not text or not waiting:
        return []
    lowered = text.lower()
    pasted = [token for token in waiting if token.lower() in lowered]
    if pasted:
        return pasted
    if _ONLY_NO.search(text) or _REFUSE_NOTE.search(text):
        return []
    if _YES.search(text):
        return list(waiting)
    return []


def prompts_a_person():
    """True when ``input`` reaches a person.

    A terminal is the plain case. Jupyter, VS Code, and Colab also prompt,
    even though their stdin is not a TTY. ``nbconvert`` sets the kernel's
    stdin flag off, and a pipe has no kernel. Those replay ``demo_utterances``
    so the visit can finish.
    """
    stdin = sys.stdin
    if stdin is not None and getattr(stdin, "isatty", lambda: False)():
        return True
    shell = _ipython()
    if shell is None:
        return False
    allowed = _kernel_allow_stdin(shell)
    if allowed is not None:
        return allowed
    name = type(shell).__name__.lower()
    if "terminal" in name:
        return False
    return True


def run_customer_chat(
    system,
    demo_utterances=None,
    max_steps=8,
    trace_id="guided-purchase",
):
    """Greet the customer and talk until they leave.

    The primary path reads ``input("You: ")``. When nobody can type, the
    lines in ``demo_utterances`` are replayed instead. Returns the visit:
    the same message list, the seller's last reply, tool log, spans, usage,
    plan, and the confirm tokens the customer approved along the way.
    """
    mode = "interactive" if prompts_a_person() else "demo"
    messages = [{"role": "system", "content": (system or "").rstrip() + SESSION_NOTE}]
    usage = []
    spans = []
    tool_log = []
    pending = []
    confirmed = set()
    plan = ""
    planned = False
    last_text = ""
    turns = 0
    if mode == "demo" and not demo_utterances:
        print(
            "No terminal is attached, and no demo lines were given. The visit ends here."
        )
        return _visit(
            mode, messages, turns, last_text, plan, tool_log, spans, usage, pending, confirmed
        )
    if mode == "demo":
        print(
            "No terminal is attached, so this visit replays a short list of customer lines."
        )
        print()
    print("Seller: " + WELCOME)
    print(flush=True)
    for raw in _lines(mode, demo_utterances):
        text = (raw or "").strip()
        if not text:
            continue
        if is_bye(text):
            break
        messages.append({"role": "user", "content": text})
        turns += 1
        print()
        print("customer turn " + str(turns))
        if not planned:
            plan = attach_plan(messages, text, usage)
            planned = True
        approved = approved_tokens(text, pending)
        if approved:
            confirmed.update(approved)
            pending = [token for token in pending if token not in confirmed]
            _record_approval(messages)
            print("approved: " + " ".join(approved))
        turn_trace = trace_id if turns == 1 else trace_id + "-" + str(turns)
        result = run_turn(
            messages,
            max_steps=max_steps,
            confirmed_tokens=confirmed,
            trace_id=turn_trace,
            spans=spans,
            usage_rows=usage,
            plan=plan,
        )
        tool_log.extend(result["tool_log"])
        for token in result["pending_tokens"]:
            if token not in confirmed and token not in pending:
                pending.append(token)
        last_text = result["text"]
        print()
        print("Seller: " + last_text)
        if pending:
            print("Seller: " + _waiting_line(pending))
        print(flush=True)
    print()
    print("Seller: " + FAREWELL)
    print("visit: turns=" + str(turns) + " mode=" + mode)
    return _visit(
        mode, messages, turns, last_text, plan, tool_log, spans, usage, pending, confirmed
    )


def _visit(mode, messages, turns, text, plan, tool_log, spans, usage, pending, confirmed):
    return {
        "mode": mode,
        "messages": messages,
        "turns": turns,
        "text": text,
        "plan": plan,
        "tool_log": tool_log,
        "spans": spans,
        "usage": usage,
        "pending_tokens": list(pending),
        "confirmed_tokens": sorted(confirmed),
    }


def _lines(mode, demo_utterances):
    if mode == "interactive":
        return _input_lines()
    return _demo_lines(demo_utterances)


def _input_lines():
    while True:
        try:
            yield input("You: ")
        except EOFError:
            return
        except Exception as error:
            if type(error).__name__ == "StdinNotImplementedError":
                return
            raise


def _demo_lines(demo_utterances):
    for line in demo_utterances or []:
        print("You: " + line)
        yield line


def _record_approval(messages):
    content = messages[0]["content"]
    if _APPROVED_MARK in content:
        return
    messages[0]["content"] = content + APPROVED_NOTE


def _waiting_line(pending):
    codes = ", ".join(pending)
    return (
        "I still need a yes before I do that. "
        "Reply yes, or send this code: " + codes + "."
    )


def _ipython():
    try:
        from IPython import get_ipython
    except ImportError:
        return None
    try:
        return get_ipython()
    except Exception:
        return None


def _kernel_allow_stdin(shell):
    kernel = getattr(shell, "kernel", None)
    if kernel is not None and hasattr(kernel, "_allow_stdin"):
        return bool(kernel._allow_stdin)
    parent = None
    getter = getattr(shell, "get_parent", None)
    if callable(getter):
        try:
            parent = getter()
        except Exception:
            parent = None
    if isinstance(parent, dict):
        content = parent.get("content")
        if isinstance(content, dict) and "allow_stdin" in content:
            return bool(content["allow_stdin"])
    return None


__all__ = [
    "APPROVED_NOTE",
    "FAREWELL",
    "SESSION_NOTE",
    "WELCOME",
    "approved_tokens",
    "is_bye",
    "prompts_a_person",
    "run_customer_chat",
]
