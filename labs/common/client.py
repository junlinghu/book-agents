"""OpenAI-compatible client shared by every lab.

Chapters 1–3 keep this module stable. Switch Ollama, Groq, or OpenRouter
by editing the repo-root ``.env`` (``BASE_URL``, ``API_KEY``, ``MODEL``).
Temperature and max tokens live here, in the harness, not in ``.env``.
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

# Used when BASE_URL / MODEL are unset. Documented in .env.example.
OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_API_KEY = "ollama"
OLLAMA_MODEL = "llama3.2"


def repo_root() -> Path:
    """Repository root (the directory that contains ``.env.example``)."""
    return Path(__file__).resolve().parents[2]


def ensure_env_loaded() -> None:
    """Load repo-root ``.env`` without overriding existing process variables."""
    load_dotenv(repo_root() / ".env", override=False)


def settings_from_env(env: Mapping[str, str]) -> tuple[str, str, str]:
    """Resolve ``(base_url, api_key, model)`` from a mapping.

    A missing ``API_KEY`` becomes the Ollama placeholder ``ollama``.
    An empty ``API_KEY`` stays empty so a hosted provider can reject it
    instead of silently receiving a fake key.
    """
    base_url = env.get("BASE_URL", OLLAMA_BASE_URL).strip()
    if "API_KEY" in env:
        api_key = env["API_KEY"].strip()
    else:
        api_key = OLLAMA_API_KEY
    model = env.get("MODEL", OLLAMA_MODEL).strip()
    return base_url, api_key, model


def load_settings() -> tuple[str, str, str]:
    """Return ``(base_url, api_key, model)`` after loading ``.env``."""
    ensure_env_loaded()
    return settings_from_env(os.environ)


def require_settings() -> tuple[str, str, str]:
    """Like :func:`load_settings`, but exit if a required value is blank."""
    base_url, api_key, model = load_settings()
    if not base_url:
        raise SystemExit("BASE_URL is empty. Copy .env.example to .env.")
    if not api_key:
        raise SystemExit(
            "API_KEY is empty. For Ollama use the literal value ollama. "
            "For Groq or OpenRouter paste a real key into .env (never commit it)."
        )
    if not model:
        raise SystemExit("MODEL is empty. Set MODEL in .env.")
    return base_url, api_key, model


def make_client() -> OpenAI:
    """Build a client. Does not send a request.

    ``tool_choice`` is intentionally never set: Ollama's compatible
    endpoint does not support that field. ``max_retries=0`` so a stopped local
    server fails in this process instead of after a retry sleep.
    """
    base_url, api_key, _model = require_settings()
    return OpenAI(
        base_url=base_url,
        api_key=api_key,
        timeout=120.0,
        max_retries=0,
    )


def describe_runtime() -> str:
    """Non-secret runtime config for lab scripts to print."""
    base_url, api_key, model = load_settings()
    shown_url = base_url.replace(api_key, "***") if api_key else base_url
    key_state = "set" if api_key else "missing"
    return (
        f"BASE_URL={shown_url}\n"
        f"MODEL={model}\n"
        f"API_KEY={key_state} (value hidden)"
    )


def redact(text: str, secret: str) -> str:
    """Remove an API key from an error string before printing it."""
    if secret and secret in text:
        return text.replace(secret, "***")
    return text
