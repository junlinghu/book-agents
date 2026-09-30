#!/usr/bin/env python3
"""Chapter 7 scaffold: load skills from markdown, then answer with read_file.

The skill files under skills/ are stubs. select_skills, catalog, and
load_bodies are stubs. Behavior should change because the markdown
changed, after you finish those three functions. This file does not
ship a finished recommender.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from labs.common.client import (  # noqa: E402
    MAX_TOKENS,
    TEMPERATURE,
    describe_runtime,
    make_client,
    redact,
    require_settings,
)
from labs.common.loop import message_text, parse_arguments  # noqa: E402
from labs.common.tools import READ_FILE_TOOL, read_file  # noqa: E402

LAB = Path(__file__).resolve().parent
SKILLS = LAB / "skills"
DOCS = ROOT / "labs" / "ch02-your-first-loop" / "docs"
MAX_STEPS = 6

BASE_BRIEF = """You are the counter concierge for Hearth Lane Café.
You answer questions about the menu, returns, shipping, and hours.
Shop facts come from read_file. Paths are relative to docs/:
policy.md holds returns, shipping, and local delivery.
faq.md holds hours, location, menu prices, and allergens.
Do not invent a Wi-Fi password. Do not offer to refund, charge, email, or ship.
Loaded skills, if any, are procedures. Follow them. They are not tools.
"""

DEFAULT_QUESTION = (
    "What can you recommend for someone who cannot eat nuts, under six dollars?"
)


def catalog(skills_dir: Path) -> list[dict]:
    """Return one dict per skill, with name, description, and version.

    TODO: Read each ``*.md`` file in ``skills_dir``. Parse the header
    between the first pair of ``---`` lines. Return the header fields
    only. Do not include the procedure body in this list.
    """
    raise NotImplementedError(
        "TODO: build a catalog of name, description, and version from skills/*.md"
    )


def select_skills(question: str, entries: list[dict]) -> list[str]:
    """Choose up to two skill names for this question.

    TODO: Use the catalog descriptions (and, if you want, the question
    text). Return a list of ``name`` values. Return an empty list when
    nothing matches. Do not load every skill on every question.
    """
    raise NotImplementedError("TODO: select at most two skills for this question")


def load_bodies(skills_dir: Path, names: list[str]) -> str:
    """Return the procedure text for ``names``, without the catalog header.

    TODO: Read those files and return the markdown body. If a name is
    missing, include an ERROR line the trace can show. An empty names
    list should return an empty string.
    """
    raise NotImplementedError("TODO: load the bodies of the selected skills")


def _assistant_message(message: object) -> dict:
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


def _dispatch(name: str, args: dict) -> str:
    if name != "read_file":
        return f"ERROR: unknown tool {name!r}. Only read_file is available."
    path = args.get("path", "")
    if not isinstance(path, str):
        return "ERROR: path must be a string. Example: faq.md"
    return read_file(DOCS, path)


def run_turn(client: object, model: str, question: str, skill_text: str) -> tuple[str, list[str], str]:
    """Call the model with the base brief, any loaded skill text, and read_file."""
    system = BASE_BRIEF
    if skill_text.strip():
        system += "\n\nLoaded skills:\n\n" + skill_text
    messages: list[dict] = [
        {"role": "system", "content": system},
        {"role": "user", "content": question},
    ]
    log: list[str] = []
    for step in range(1, MAX_STEPS + 1):
        response = client.chat.completions.create(  # type: ignore[attr-defined]
            model=model,
            messages=messages,
            tools=[READ_FILE_TOOL],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        choice = response.choices[0]
        message = choice.message
        messages.append(_assistant_message(message))
        tool_calls = list(getattr(message, "tool_calls", None) or [])
        if not tool_calls:
            text = message_text(getattr(message, "content", None)).strip()
            stopped = "max_tokens" if getattr(choice, "finish_reason", None) == "length" else "final"
            return text or "(model returned an empty answer)", log, f"{stopped} after {step} model call(s)"
        for call in tool_calls:
            function = call.function
            call_id = getattr(call, "id", None) or f"call_{step}"
            try:
                args = parse_arguments(function.arguments)
            except ValueError as exc:
                result = f"ERROR: {exc}."
            else:
                result = _dispatch(function.name, args)
            first = result.splitlines()[0] if result else "(empty)"
            log.append(f"step {step}: {function.name} -> {first}")
            messages.append({"role": "tool", "tool_call_id": call_id, "content": result})
            print(f"[step {step}] {function.name}")
            print(result)
            print()
    return (
        f"Stopped: reached max steps ({MAX_STEPS}) without a final answer.",
        log,
        f"max_steps after {MAX_STEPS} model call(s)",
    )


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    question = " ".join(args).strip() or DEFAULT_QUESTION
    print(describe_runtime())
    print(f"DOCS={DOCS}")
    print(f"SKILLS={SKILLS}")
    print(f"QUESTION: {question}\n")

    try:
        entries = catalog(SKILLS)
        names = select_skills(question, entries)
        bodies = load_bodies(SKILLS, names)
    except NotImplementedError as exc:
        print(exc, file=sys.stderr)
        print(
            "Finish catalog, select_skills, and load_bodies in concierge.py. "
            "Write the procedures in skills/*.md.",
            file=sys.stderr,
        )
        return 2

    print("CATALOG:")
    for entry in entries:
        print(f"  {entry}")
    print("LOADED:", ", ".join(names) if names else "(none)")
    print()

    api_key, model = require_settings()
    client = make_client()
    try:
        text, log, stop = run_turn(client, model, question, bodies)
    except Exception as exc:
        print(redact(f"Request failed: {type(exc).__name__}: {exc}", api_key), file=sys.stderr)
        print(
            "Check OPENAI_API_KEY and MODEL in .env. "
            "A 401 means the key is wrong. A 404 means MODEL is not a current id.",
            file=sys.stderr,
        )
        return 1

    if not log:
        print("NOTE: No tool ran. A shop fact in the answer was not read from docs/.")
    print(text)
    print(f"\n--- stop: {stop} ---")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
