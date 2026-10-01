"""Chat Completions for the tutorial.

Notebooks call :func:`chat`. Every turn goes to the OpenAI Chat Completions
API through :mod:`tutorial.common.client`. ``OPENAI_API_KEY`` is required.
The key is read from the repository-root ``.env``, or from the process
environment (including a Colab secret the setup cell copied in). This
module never prints the key.
"""

from __future__ import annotations

import json
import time

from tutorial.common.client import (
    MAX_TOKENS,
    MISSING_KEY,
    TEMPERATURE,
    load_settings,
    make_client,
    redact,
)


def require_key():
    """Return ``(api_key, model)``. Raise if the key is missing."""
    api_key, model = load_settings()
    if not api_key:
        raise RuntimeError(MISSING_KEY)
    return api_key, model


def chat(messages, tools):
    """Return one assistant turn as a plain dict.

    ``tool_calls`` is a list of ``{id, name, arguments, raw}``.
    ``arguments`` is a dict when the JSON parsed. ``usage`` is token
    counts from the API response.
    """
    api_key, model = require_key()
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
