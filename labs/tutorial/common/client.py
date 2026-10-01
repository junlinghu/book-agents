"""OpenAI settings for the tutorial notebooks.

Put `OPENAI_API_KEY` in the repository-root `.env`.
`MODEL` is optional. Temperature and max tokens live here, not in `.env`.
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

# Sampling defaults. They live in code so a lesson does not change them by accident.
TEMPERATURE = 0.2
MAX_TOKENS = 800

# Used when MODEL is unset or blank. Documented in the repository `.env.example`.
# gpt-4.1-mini supports tool calling.
# https://developers.openai.com/api/docs/models/gpt-4.1-mini
DEFAULT_MODEL = "gpt-4.1-mini"


def repo_root():
    """Repository root (the folder that contains `.env.example`).

    This file is `labs/tutorial/common/client.py`, so the root is three folders up.
    """
    this_folder = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(os.path.dirname(this_folder)))


def ensure_env_loaded():
    """Load repo-root `.env`. Variables already set in the shell stay as they are."""
    load_dotenv(os.path.join(repo_root(), ".env"), override=False)


def settings_from_env(env):
    """Return `(api_key, model)` from a dict or from `os.environ`.

    A missing or blank key stays empty so the run can stop before a request.
    A missing or blank `MODEL` becomes `DEFAULT_MODEL`.
    """
    api_key = env.get("OPENAI_API_KEY", "").strip()
    model = env.get("MODEL", "").strip()
    if not model:
        model = DEFAULT_MODEL
    return api_key, model


def load_settings():
    """Return `(api_key, model)` after loading `.env`."""
    ensure_env_loaded()
    return settings_from_env(os.environ)


def require_settings():
    """Like `load_settings`, but exit if the API key is blank."""
    api_key, model = load_settings()
    if not api_key:
        raise SystemExit(
            "OPENAI_API_KEY is empty. Copy .env.example to .env and paste a key "
            "from https://platform.openai.com/api-keys. Never commit .env."
        )
    if not model:
        raise SystemExit("MODEL is empty. Leave it unset to use " + DEFAULT_MODEL + ".")
    return api_key, model


def make_client():
    """Build a client. Does not send a request.

    `max_retries=0` so a bad key fails immediately instead of sleeping
    through retries.
    """
    api_key, _model = require_settings()
    return OpenAI(
        api_key=api_key,
        timeout=120.0,
        max_retries=0,
    )


def describe_runtime():
    """Model name and whether a key is set. The key value is not included."""
    api_key, model = load_settings()
    if api_key:
        key_state = "set"
    else:
        key_state = "missing"
    return "MODEL=" + model + "\nOPENAI_API_KEY=" + key_state + " (value hidden)"


def redact(text, secret):
    """Remove an API key from an error string before printing it."""
    if secret and secret in text:
        return text.replace(secret, "***")
    return text
