"""Chat Completions for the tutorial, live or scripted.

Notebooks call :func:`chat`. ``DEMO_MODE`` in the notebook or in the
environment chooses the path:

- ``True`` / ``1``: scripted model, real tools. No network.
- ``False`` / ``0``: OpenAI Chat Completions. Requires ``OPENAI_API_KEY``.
- unset: scripted when the key is missing, live when it is set.

The key is read from the repository-root ``.env`` by
``labs.tutorial.common.client``. This module never prints the key.
"""

from __future__ import annotations

import json
import time

from labs.tutorial.common.client import (
    MAX_TOKENS,
    TEMPERATURE,
    describe_runtime,
    load_settings,
    make_client,
    redact,
)


def using_demo(flag):
    """Return True when this run should use the scripted model.

    ``flag`` is the notebook's ``DEMO_MODE`` value. ``None`` means
    "follow the environment, then whether a key is present."
    """
    if flag is True:
        return True
    if flag is False:
        return False
    return _env_wants_demo()


def _env_wants_demo():
    import os

    raw = os.environ.get("DEMO_MODE", "").strip().lower()
    if raw in {"1", "true", "yes", "on"}:
        return True
    if raw in {"0", "false", "no", "off"}:
        return False
    api_key, _model = load_settings()
    return not bool(api_key)


def describe_mode(flag):
    """One banner: lesson mode, model name, key present or missing."""
    if using_demo(flag):
        mode = "demo (scripted model, real tools, no API call)"
    else:
        mode = "live (OpenAI Chat Completions)"
    return "mode: " + mode + "\n" + describe_runtime()


def chat(messages, tools, *, lesson, demo):
    """Return one assistant turn as a plain dict.

    ``tool_calls`` is a list of ``{id, name, arguments, raw}``.
    ``arguments`` is a dict when the JSON parsed. ``usage`` is token
    counts. In demo mode the counts are a character estimate so the
    cost lesson has numbers without a bill.
    """
    if using_demo(demo):
        from labs.tutorial.demo_model import scripted_turn

        _api_key, model = load_settings()
        started = time.perf_counter()
        turned = scripted_turn(messages, tools, lesson)
        elapsed = (time.perf_counter() - started) * 1000
        usage = _estimate_usage(messages, turned)
        return {
            "content": turned["content"],
            "tool_calls": turned["tool_calls"],
            "usage": usage,
            "latency_ms": round(max(elapsed, 0.1), 3),
            "model": model,
            "mode": "demo",
        }

    api_key, model = load_settings()
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is empty. Copy .env.example to .env and paste a key "
            "from https://platform.openai.com/api-keys, or set DEMO_MODE=1 "
            "to run the scripted lesson. Never commit .env."
        )
    client = make_client()
    kwargs = {
        "model": model,
        "messages": messages,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
    }
    if tools:
        kwargs["tools"] = tools
    started = time.perf_counter()
    try:
        response = client.chat.completions.create(**kwargs)
    except Exception as error:
        raise RuntimeError(redact(str(error), api_key)) from None
    elapsed = (time.perf_counter() - started) * 1000
    if not response.choices:
        return {
            "content": "",
            "tool_calls": [],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0},
            "latency_ms": round(elapsed, 3),
            "model": model,
            "mode": "live",
        }
    message = response.choices[0].message
    usage_obj = getattr(response, "usage", None)
    if usage_obj is None:
        usage = {"prompt_tokens": 0, "completion_tokens": 0}
    else:
        usage = {
            "prompt_tokens": int(getattr(usage_obj, "prompt_tokens", 0) or 0),
            "completion_tokens": int(getattr(usage_obj, "completion_tokens", 0) or 0),
        }
    return {
        "content": message.content or "",
        "tool_calls": _normalize_calls(getattr(message, "tool_calls", None) or []),
        "usage": usage,
        "latency_ms": round(elapsed, 3),
        "model": model,
        "mode": "live",
    }


def _normalize_calls(calls):
    normalized = []
    for index, call in enumerate(calls):
        function = call.function
        raw = function.arguments
        if not isinstance(raw, str):
            raw = json.dumps(raw)
        try:
            arguments = json.loads(raw) if raw else {}
        except json.JSONDecodeError as error:
            arguments = {"_error": "arguments are not valid JSON (" + str(error) + ")"}
        if not isinstance(arguments, dict):
            arguments = {"_error": "arguments must be a JSON object"}
        call_id = getattr(call, "id", None) or ("call_live_" + str(index))
        normalized.append({
            "id": call_id,
            "name": function.name,
            "arguments": arguments,
            "raw": raw,
        })
    return normalized


def _estimate_usage(messages, turned):
    """Rough tokens for the scripted path. Not an invoice."""
    prompt_chars = len(json.dumps(messages, default=str))
    completion = turned["content"] or ""
    if turned["tool_calls"]:
        completion += json.dumps(turned["tool_calls"], default=str)
    return {
        "prompt_tokens": max(1, prompt_chars // 4),
        "completion_tokens": max(1, len(completion) // 4),
    }
