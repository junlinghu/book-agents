"""OpenAI client shared by every lab.

The labs keep this module stable. Set ``OPENAI_API_KEY`` in the
repo-root ``.env``. Optionally set ``MODEL``. The client uses the
official SDK default API (``https://api.openai.com/v1``). Temperature
and max tokens live here, in the harness, not in ``.env``.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# Harness sampling defaults. Chapter 3 explains why these are code, not env.
TEMPERATURE = 0.2
MAX_TOKENS = 800

# Used when MODEL is unset or blank. Documented in .env.example.
# gpt-4.1-mini supports tool calling, which Chapters 2 and 3 need.
# https://developers.openai.com/api/docs/models/gpt-4.1-mini
DEFAULT_MODEL = "gpt-4.1-mini"


def repo_root() -> Path:
    """Repository root (the directory that contains ``.env.example``)."""
    return Path(__file__).resolve().parents[2]


def ensure_env_loaded() -> None:
    """Load repo-root ``.env`` without overriding existing process variables."""
    load_dotenv(repo_root() / ".env", override=False)


def settings_from_env(env: Mapping[str, str]) -> tuple[str, str]:
    """Resolve ``(api_key, model)`` from a mapping.

    ``OPENAI_API_KEY`` is the variable the official SDK reads. A missing
    or blank key stays empty so the run can stop before a request.
    A missing or blank ``MODEL`` becomes :data:`DEFAULT_MODEL`.
    """
    api_key = env.get("OPENAI_API_KEY", "").strip()
    model = env.get("MODEL", "").strip() or DEFAULT_MODEL
    return api_key, model


def load_settings() -> tuple[str, str]:
    """Return ``(api_key, model)`` after loading ``.env``."""
    ensure_env_loaded()
    return settings_from_env(os.environ)


def require_settings() -> tuple[str, str]:
    """Like :func:`load_settings`, but exit if the API key is blank."""
    api_key, model = load_settings()
    if not api_key:
        raise SystemExit(
            "OPENAI_API_KEY is empty. Copy .env.example to .env and paste a key "
            "from https://platform.openai.com/api-keys. Never commit .env."
        )
    if not model:
        raise SystemExit(f"MODEL is empty. Leave it unset to use {DEFAULT_MODEL}.")
    return api_key, model


def make_client() -> OpenAI:
    """Build a client. Does not send a request.

    The base URL is the SDK default. ``max_retries=0`` so an auth or
    network error fails in this process instead of after a retry sleep.
    """
    api_key, _model = require_settings()
    return OpenAI(
        api_key=api_key,
        timeout=120.0,
        max_retries=0,
    )


def describe_runtime() -> str:
    """Non-secret runtime config for lab scripts to print."""
    api_key, model = load_settings()
    key_state = "set" if api_key else "missing"
    return f"MODEL={model}\nOPENAI_API_KEY={key_state} (value hidden)"


def redact(text: str, secret: str) -> str:
    """Remove an API key from an error string before printing it."""
    if secret and secret in text:
        return text.replace(secret, "***")
    return text
