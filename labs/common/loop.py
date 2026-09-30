"""Perceive → reason → act → observe, with stop conditions.

The model proposes ``read_file`` calls. This module executes them and
appends the result. It does not invent a customer-facing answer when
the loop stops early.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

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


@dataclass
class AgentResult:
    """What the harness returns after the loop stops."""

    text: str
    steps: int
    stopped: str
    tool_log: list[str] = field(default_factory=list)


def message_text(content: object) -> str:
    """Normalize provider content that is a string, null, or a list of parts."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        chunks: list[str] = []
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


def parse_arguments(raw: object) -> dict:
    """Parse tool-call arguments into an object. Raise ``ValueError`` if not."""
    if raw is None or raw == "":
        return {}
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"arguments are not valid JSON ({exc})") from exc
        if not isinstance(parsed, dict):
            raise ValueError("arguments must be a JSON object")
        return parsed
    raise ValueError(f"unexpected arguments type: {type(raw).__name__}")


def _assistant_message(message: object) -> dict:
    # Empty string, not null: Chat Completions accepts "" on tool turns.
    content = message_text(getattr(message, "content", None))
    assistant: dict = {"role": "assistant", "content": content}
    tool_calls = list(getattr(message, "tool_calls", None) or [])
    if not tool_calls:
        return assistant
    dumped = []
    for index, call in enumerate(tool_calls):
        function = call.function
        raw_args = function.arguments
        if not isinstance(raw_args, str):
            raw_args = json.dumps(raw_args)
        dumped.append(
            {
                "id": getattr(call, "id", None) or f"call_{index}",
                "type": "function",
                "function": {"name": function.name, "arguments": raw_args},
            }
        )
    assistant["tool_calls"] = dumped
    return assistant


def _dispatch(docs_dir: Path, name: str, args: dict) -> str:
    if name != "read_file":
        return f"ERROR: unknown tool {name!r}. Only read_file is available."
    path = args.get("path", "")
    if not isinstance(path, str):
        return "ERROR: path must be a string. Example: policy.md"
    return read_file(docs_dir, path)


def run_file_agent(
    client: object,
    model: str,
    user_text: str,
    docs_dir: Path,
    *,
    max_steps: int = DEFAULT_MAX_STEPS,
    verbose: bool = True,
) -> AgentResult:
    """Run the tool loop until the model stops or a harness limit hits.

    ``stopped`` is one of ``final``, ``max_steps``, ``repeated_call``,
    or ``max_tokens``.
    """
    messages: list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_text},
    ]
    seen: dict[str, int] = {}
    log: list[str] = []

    for step in range(1, max_steps + 1):
        response = client.chat.completions.create(  # type: ignore[attr-defined]
            model=model,
            messages=messages,
            tools=[READ_FILE_TOOL],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        if not response.choices:
            return AgentResult(
                text="Stopped: the provider returned no choices.",
                steps=step,
                stopped="max_steps",
                tool_log=log,
            )
        choice = response.choices[0]
        message = choice.message
        messages.append(_assistant_message(message))
        tool_calls = list(getattr(message, "tool_calls", None) or [])

        if not tool_calls:
            text = message_text(getattr(message, "content", None)).strip()
            if getattr(choice, "finish_reason", None) == "length":
                return AgentResult(
                    text=text
                    or "Stopped: the completion hit max_tokens before it finished.",
                    steps=step,
                    stopped="max_tokens",
                    tool_log=log,
                )
            if not text:
                text = "(model returned an empty answer)"
            return AgentResult(text=text, steps=step, stopped="final", tool_log=log)

        for call in tool_calls:
            function = call.function
            name = function.name
            call_id = getattr(call, "id", None) or f"call_{step}"
            try:
                args = parse_arguments(function.arguments)
            except ValueError as exc:
                result = (
                    f"ERROR: {exc}. "
                    'Pass a JSON object such as {"path": "policy.md"}.'
                )
                log.append(f"step {step}: {name} invalid arguments")
            else:
                signature = name + " " + json.dumps(args, sort_keys=True, default=str)
                seen[signature] = seen.get(signature, 0) + 1
                if seen[signature] > MAX_IDENTICAL_CALLS:
                    log.append(f"step {step}: repeated {signature}")
                    if verbose:
                        print(f"[step {step}] repeated {name} — harness stop")
                    return AgentResult(
                        text=(
                            "Stopped: the model repeated the same tool call "
                            f"({name}) more than {MAX_IDENTICAL_CALLS} times. "
                            "The harness ended the loop."
                        ),
                        steps=step,
                        stopped="repeated_call",
                        tool_log=log,
                    )
                result = _dispatch(docs_dir, name, args)
                if seen[signature] == MAX_IDENTICAL_CALLS:
                    result += (
                        "\n\nNOTE: You already read this file. "
                        "Answer the customer now without calling read_file again."
                    )
                first_line = result.splitlines()[0] if result else "(empty)"
                log.append(f"step {step}: {name} {json.dumps(args, sort_keys=True)} -> {first_line}")

            messages.append(
                {"role": "tool", "tool_call_id": call_id, "content": result}
            )
            if verbose:
                print(f"[step {step}] {name}")
                print(result)
                print()

    return AgentResult(
        text=(
            f"Stopped: reached max steps ({max_steps}) without a final answer. "
            "The harness did not write one."
        ),
        steps=max_steps,
        stopped="max_steps",
        tool_log=log,
    )


def observation_notes(result: AgentResult) -> list[str]:
    """Soft checks for the lab scripts. They do not change the answer."""
    notes: list[str] = []
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
