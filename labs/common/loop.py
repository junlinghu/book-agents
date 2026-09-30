"""The Chapter 2 loop: ask the model, run read_file, ask again.

Stops:
- final: the model replied with text and did not call a tool
- max_steps: too many model calls, and this code does not invent an answer
- repeated_call: the same tool call happened too many times
- max_tokens: the reply was cut off by the length limit

The model proposes read_file calls. This module runs them and appends
the result. It does not write a customer-facing answer when it stops early.
"""

import json

from labs.common.client import MAX_TOKENS, TEMPERATURE
from labs.common.tools import READ_FILE_TOOL, read_file

# Model turns, including turns that only call a tool. A café question
# needs at most two reads; six is room for a bad path and a retry.
DEFAULT_MAX_STEPS = 6

# The second identical call still runs (with a nudge). The next one stops.
MAX_IDENTICAL_CALLS = 2

SYSTEM_PROMPT = """You are the counter concierge for Hearth Lane Café.
You answer questions about returns, shipping, hours, and the menu.

Use the read_file tool to read shop documents before you state a rule,
price, hour, or fee. Paths are relative to docs/:
- policy.md — returns, shipping, damage, local delivery
- faq.md — hours, location, menu prices, allergens

Every factual claim about the shop must include the file you read,
in parentheses, for example (docs/policy.md).
If the documents do not say, answer that you don't know.
Do not invent a Wi-Fi password, a refund, or a shipping exception.
Do not offer to refund, charge, email, or ship anything yourself.
You can only read files and reply.
"""


class AgentResult:
    """What the loop returns when it stops."""

    def __init__(self, text, steps, stopped, tool_log):
        self.text = text
        self.steps = steps
        self.stopped = stopped
        self.tool_log = tool_log


def message_text(content):
    """Turn model content into one string.

    Content may be a string, None, or a list of parts.
    """
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        chunks = []
        for part in content:
            if isinstance(part, str):
                chunks.append(part)
            elif isinstance(part, dict) and part.get("type") == "text":
                chunks.append(str(part.get("text", "")))
            else:
                text = getattr(part, "text", None)
                if text:
                    chunks.append(str(text))
        return "".join(chunks)
    return str(content)


def parse_arguments(raw):
    """Turn tool-call arguments into a dict. Raise ValueError if they are not one."""
    if raw is None or raw == "":
        return {}
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as error:
            raise ValueError("arguments are not valid JSON (" + str(error) + ")") from error
        if not isinstance(parsed, dict):
            raise ValueError("arguments must be a JSON object")
        return parsed
    raise ValueError("unexpected arguments type: " + type(raw).__name__)


def run_one_tool(docs_dir, name, args):
    """Run one tool call. Unknown tools become an ERROR string, not a crash."""
    if name != "read_file":
        return "ERROR: unknown tool " + repr(name) + ". Only read_file is available."
    path = args.get("path", "")
    if not isinstance(path, str):
        return "ERROR: path must be a string. Example: policy.md"
    return read_file(docs_dir, path)


def run_file_agent(client, model, user_text, docs_dir, max_steps=DEFAULT_MAX_STEPS, verbose=True):
    """Run the tool loop until the model stops or a limit hits.

    `stopped` is one of `final`, `max_steps`, `repeated_call`, or `max_tokens`.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_text},
    ]
    seen = {}
    log = []

    for step in range(1, max_steps + 1):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=[READ_FILE_TOOL],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        if not response.choices:
            return AgentResult(
                "Stopped: the provider returned no choices.",
                step,
                "max_steps",
                log,
            )

        choice = response.choices[0]
        message = choice.message
        tool_calls = list(getattr(message, "tool_calls", None) or [])

        # Copy the assistant turn into the message list, including any tool calls.
        # Chat Completions wants the arguments as a string, even if we received a dict.
        prepared = []
        for index, call in enumerate(tool_calls):
            function = call.function
            if getattr(call, "id", None):
                call_id = call.id
            else:
                call_id = "call_" + str(index)
            raw_args = function.arguments
            if isinstance(raw_args, str):
                stored_args = raw_args
            else:
                stored_args = json.dumps(raw_args)
            prepared.append({
                "id": call_id,
                "name": function.name,
                "raw": raw_args,
                "stored": stored_args,
            })

        assistant = {
            "role": "assistant",
            "content": message_text(getattr(message, "content", None)),
        }
        if prepared:
            assistant["tool_calls"] = []
            for item in prepared:
                assistant["tool_calls"].append({
                    "id": item["id"],
                    "type": "function",
                    "function": {
                        "name": item["name"],
                        "arguments": item["stored"],
                    },
                })
        messages.append(assistant)

        if not prepared:
            text = message_text(getattr(message, "content", None)).strip()
            if getattr(choice, "finish_reason", None) == "length":
                if not text:
                    text = "Stopped: the completion hit max_tokens before it finished."
                return AgentResult(text, step, "max_tokens", log)
            if not text:
                text = "(model returned an empty answer)"
            return AgentResult(text, step, "final", log)

        for item in prepared:
            name = item["name"]
            try:
                args = parse_arguments(item["raw"])
            except ValueError as error:
                result = (
                    "ERROR: " + str(error) + ". "
                    + 'Pass a JSON object such as {"path": "policy.md"}.'
                )
                log.append("step " + str(step) + ": " + name + " invalid arguments")
            else:
                signature = name + " " + json.dumps(args, sort_keys=True, default=str)
                count = seen.get(signature, 0) + 1
                seen[signature] = count
                if count > MAX_IDENTICAL_CALLS:
                    log.append("step " + str(step) + ": repeated " + signature)
                    if verbose:
                        print("[step " + str(step) + "] repeated " + name + " — harness stop")
                    return AgentResult(
                        "Stopped: the model repeated the same tool call ("
                        + name
                        + ") more than "
                        + str(MAX_IDENTICAL_CALLS)
                        + " times. The harness ended the loop.",
                        step,
                        "repeated_call",
                        log,
                    )
                result = run_one_tool(docs_dir, name, args)
                if count == MAX_IDENTICAL_CALLS:
                    result = (
                        result
                        + "\n\nNOTE: You already read this file. "
                        + "Answer the customer now without calling read_file again."
                    )
                if result:
                    first_line = result.splitlines()[0]
                else:
                    first_line = "(empty)"
                log.append(
                    "step "
                    + str(step)
                    + ": "
                    + name
                    + " "
                    + json.dumps(args, sort_keys=True)
                    + " -> "
                    + first_line
                )

            messages.append({
                "role": "tool",
                "tool_call_id": item["id"],
                "content": result,
            })
            if verbose:
                print("[step " + str(step) + "] " + name)
                print(result)
                print()

    return AgentResult(
        "Stopped: reached max steps ("
        + str(max_steps)
        + ") without a final answer. The harness did not write one.",
        max_steps,
        "max_steps",
        log,
    )


def observation_notes(result):
    """Soft checks for the lab scripts. They do not change the answer."""
    notes = []
    if result.stopped == "final" and not result.tool_log:
        notes.append(
            "No tool ran. Shop facts in the answer were not read from docs/. "
            "The lab does not send tool_choice, so the model can skip the read. "
            "Try another tool-capable MODEL in .env, such as gpt-4.1, and run again."
        )
    if result.stopped == "final" and "docs/" not in result.text:
        notes.append(
            "No docs/ citation in the answer. A specific fee, hour, or rule "
            "without a path is not yet a grounded answer."
        )
    if result.stopped == "max_steps":
        notes.append(
            "Hit the max-steps stop. The trace above is the work that happened. "
            "There is no customer answer from the harness."
        )
    if result.stopped == "repeated_call":
        notes.append(
            "The model called read_file with the same arguments too many times. "
            "The harness stopped it."
        )
    if result.stopped == "max_tokens":
        notes.append(
            "The completion hit MAX_TOKENS in labs/common/client.py. "
            "A cut-off tool call looks like a broken model. Raise MAX_TOKENS "
            "if the trace shows a truncated arguments JSON."
        )
    return notes
