"""Autonomy tiers for the tutorial.

A tool call is still only a proposal. :func:`decide` is the harness
check that runs before any side effect. ``auto`` may run. ``confirm``
runs only when a person approves that exact call. ``never`` does not
run, even with a token.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

AUTO = "auto"
CONFIRM = "confirm"
NEVER = "never"

ALLOWED = "allowed"
CONFIRM_REQUIRED = "confirm_required"
DENIED = "denied"

SHOP_EMAIL_DOMAIN = "hearthlane.example"

# Tools whose tier does not depend on arguments. Unknown names are never.
_FIXED = {
    "price_check": AUTO,
    "lookup_catalog": AUTO,
    "add_to_cart": AUTO,
    "draft_email": AUTO,
    "draft_calendar": AUTO,
    "place_order": CONFIRM,
    "checkout": CONFIRM,
    "charge_card": NEVER,
}

_MAIL_TOOLS = {"send_email", "send_draft"}

_CARD_KEYS = {"card", "card_number", "pan", "cvc", "cvv", "number"}
_ADDRESS = re.compile(r"[^@\s]+@[^@\s]+")
_PAN = re.compile(r"\d{13,19}")


def approval_token(name: str, arguments: dict | None) -> str:
    """Stable id for one tool name plus its arguments.

    A confirm button in the labs is this token. A different argument,
    including a different total or a different draft body, is a different
    token.
    """
    payload = json.dumps(
        {"tool": name, "arguments": arguments or {}},
        sort_keys=True,
        default=str,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:8]


def _recipient(arguments: dict) -> str:
    for key in ("to", "recipient", "email"):
        value = arguments.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def is_shop_address(address: str) -> bool:
    """True only for a plain address at the café's own domain."""
    text = address.strip()
    if not _ADDRESS.fullmatch(text):
        return False
    domain = text.rsplit("@", 1)[1].lower()
    return domain == SHOP_EMAIL_DOMAIN


def tier_for(
    name: str,
    arguments: dict | None = None,
    *,
    allow_external_mail: bool = False,
) -> str:
    """Return ``auto``, ``confirm``, or ``never``.

    ``allow_external_mail`` is a staff switch. The customer concierge leaves
    it false, so mail outside the shop domain stays ``never``. Either way,
    sending still requires a matching token.
    A missing or malformed address stays ``never``.
    """
    args = arguments or {}
    if name in _MAIL_TOOLS:
        recipient = _recipient(args)
        if not recipient or not _ADDRESS.fullmatch(recipient):
            return NEVER
        if is_shop_address(recipient):
            return CONFIRM
        if allow_external_mail:
            return CONFIRM
        return NEVER
    return _FIXED.get(name, NEVER)


def _looks_like_pan(value: object) -> bool:
    if not isinstance(value, str):
        return False
    digits = re.sub(r"[\s-]", "", value)
    return bool(_PAN.fullmatch(digits))


def redact_arguments(arguments: dict | None) -> dict[str, Any]:
    """Copy arguments with card-like values removed.

    A denial the model can read must not echo a full card number.
    """

    def _clean(value: object) -> object:
        if isinstance(value, dict):
            return redact_arguments(value)
        if isinstance(value, list):
            return [_clean(item) for item in value]
        if _looks_like_pan(value):
            return "[redacted]"
        return value

    cleaned: dict[str, Any] = {}
    for key, value in (arguments or {}).items():
        if key.lower() in _CARD_KEYS:
            cleaned[key] = "[redacted]"
        else:
            cleaned[key] = _clean(value)
    return cleaned


def _never_reason(name: str, arguments: dict) -> str:
    if name == "charge_card":
        return (
            "DENIED: charge_card is never available. "
            "This concierge does not charge cards."
        )
    if name in _MAIL_TOOLS:
        recipient = _recipient(arguments) or "(missing)"
        return (
            "DENIED: email outside "
            f"{SHOP_EMAIL_DOMAIN} is never sent ({recipient})."
        )
    return f"DENIED: unknown tool {name!r}. The harness will not run it."


def decide(
    name: str,
    arguments: dict | None = None,
    *,
    confirmed_token: str | None = None,
    allow_external_mail: bool = False,
) -> dict[str, Any]:
    """Decide whether the harness may execute this call.

    The returned ``arguments`` are redacted. ``confirmed_token`` is consulted
    only for the confirm tier, and only when it equals :func:`approval_token`
    for this name and these arguments. A token never promotes a ``never`` tool.
    """
    args = arguments or {}
    tier = tier_for(name, args, allow_external_mail=allow_external_mail)
    token = approval_token(name, args)
    base: dict[str, Any] = {
        "tool": name,
        "tier": tier,
        "arguments": redact_arguments(args),
        "approval_token": token,
        "confirmed": False,
    }
    if tier == NEVER:
        return {**base, "decision": DENIED, "reason": _never_reason(name, args)}
    if tier == CONFIRM:
        if confirmed_token and confirmed_token == token:
            return {
                **base,
                "decision": ALLOWED,
                "confirmed": True,
                "reason": "A person approved this exact call.",
            }
        return {
            **base,
            "decision": CONFIRM_REQUIRED,
            "reason": "Waiting for a person to approve this exact call.",
        }
    return {
        **base,
        "decision": ALLOWED,
        "reason": "Auto tier. The harness ran the call without a prompt.",
    }


def format_decision(decision: dict[str, Any]) -> str:
    """One stable block for lab traces. Confirm is the only tier that prints a token."""
    args = json.dumps(
        decision["arguments"], sort_keys=True, default=str, ensure_ascii=False
    )
    token = ""
    if decision["tier"] == CONFIRM:
        token = f" approval_token={decision['approval_token']}"
    confirmed = "yes" if decision.get("confirmed") else "no"
    return (
        f"tier={decision['tier']} decision={decision['decision']}{token} "
        f"confirmed={confirmed}\n"
        f"    arguments={args}\n"
        f"    reason={decision['reason']}"
    )
