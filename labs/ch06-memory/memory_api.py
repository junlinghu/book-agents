"""Durable café memory: get, set, search, and a forget the learner fills in.

Records live in a JSON file so they survive the process. Session messages
do not. ``forgets`` is still a stub: until it marks a row forgotten, a
stale belief comes back on the next run.
"""

from __future__ import annotations

import json
import re
import uuid
from datetime import date
from pathlib import Path

from labs.common.payload import tool_payload

KINDS = frozenset({"preference", "constraint", "belief"})
MAX_TEXT = 500
MAX_SOURCE = 200
MAX_SEARCH = 20

MEMORY_GET_TOOL: dict = {
    "type": "function",
    "function": {
        "name": "memory_get",
        "description": (
            "Fetch one memory record by id, including a forgotten record. "
            "Use this when you already have an id from memory_search."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Record id, such as mem_buns_nutfree."}
            },
            "required": ["id"],
        },
    },
}

MEMORY_SET_TOOL: dict = {
    "type": "function",
    "function": {
        "name": "memory_set",
        "description": (
            "Append one durable record. Does not replace an older record. "
            "scope is customer:<name> or shop. kind is preference, constraint, or belief. "
            "A customer's allergy is a constraint on that customer, not a shop belief. "
            "Shop facts that already live in faq.md or policy.md should not be copied here."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "scope": {"type": "string", "description": "customer:priya or shop."},
                "kind": {"type": "string", "description": "preference, constraint, or belief."},
                "source": {"type": "string", "description": "Who said this, and when."},
            },
            "required": ["text", "scope", "kind", "source"],
        },
    },
}

MEMORY_SEARCH_TOOL: dict = {
    "type": "function",
    "function": {
        "name": "memory_search",
        "description": (
            "Search active memory records. Forgotten records are omitted. "
            "query matches text, scope, or kind. Pass an empty query to list active records."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "scope": {
                    "type": "string",
                    "description": "Optional. When set, only this scope is returned.",
                },
            },
            "required": ["query"],
        },
    },
}

MEMORY_FORGET_TOOL: dict = {
    "type": "function",
    "function": {
        "name": "memory_forget",
        "description": (
            "Mark one record forgotten. The row stays for an audit, with "
            "status forgotten, and memory_search will skip it. "
            "Use this when a belief conflicts with faq.md or the guest's constraint changed."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Record id to invalidate."}
            },
            "required": ["id"],
        },
    },
}

MEMORY_TOOLS: list[dict] = [
    MEMORY_GET_TOOL,
    MEMORY_SET_TOOL,
    MEMORY_SEARCH_TOOL,
    MEMORY_FORGET_TOOL,
]


def tool_result(
    ok: bool,
    code: str,
    message: str,
    *,
    retryable: bool = False,
    hint: str = "",
    **extra: object,
) -> str:
    return tool_payload(ok, code, message, retryable=retryable, hint=hint, **extra)


def _empty_store() -> dict:
    return {"records": []}


def load_store(path: Path) -> dict:
    if not path.is_file():
        return _empty_store()
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("records"), list):
        raise ValueError(f"{path} is not a memory store")
    return data


def save_store(path: Path, data: dict) -> None:
    """Write the store by replacing the file. A crash mid-write keeps the old one."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def ensure_store(path: Path, seed: Path) -> None:
    """Copy the seed the first time. Later runs keep what set and forget did."""
    if path.is_file():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    save_store(path, json.loads(seed.read_text(encoding="utf-8")))


def reset_store(path: Path, seed: Path) -> None:
    if path.exists():
        path.unlink()
    ensure_store(path, seed)


def valid_scope(scope: str) -> bool:
    if scope == "shop":
        return True
    return re.fullmatch(r"customer:[a-z][a-z-]{0,40}", scope) is not None


def rejects_generalization(text: str, scope: str) -> str | None:
    """Return an error code when one guest is being written up as a shop rule.

    TODO(learner): return ``"refused_generalization"`` when ``scope`` is
    ``"shop"`` and the text claims the café is nut-free, or that every
    customer shares one guest's allergy or budget. A customer-scoped
    constraint such as "Priya is allergic to almonds" is allowed.
    The starter returns None, so the write is stored.
    """
    return None


def memory_get(path: Path, memory_id: str) -> str:
    if not isinstance(memory_id, str) or not memory_id.strip():
        return tool_result(False, "bad_id", "id is required.", hint="Pass an id from memory_search.")
    store = load_store(path)
    for record in store["records"]:
        if record.get("id") == memory_id:
            return tool_result(True, "ok", "Record.", record=record)
    return tool_result(
        False,
        "not_found",
        f"No record with id {memory_id!r}.",
        hint="memory_search lists active ids. Forgotten rows still resolve here.",
    )


def memory_set(path: Path, text: str, scope: str, kind: str, source: str) -> str:
    if not isinstance(text, str) or not text.strip():
        return tool_result(False, "empty_text", "text is required.", hint="State the preference or constraint.")
    if len(text) > MAX_TEXT:
        return tool_result(
            False,
            "too_long",
            f"text is longer than {MAX_TEXT} characters.",
            hint="Store one fact, not a transcript.",
        )
    if not isinstance(scope, str) or not valid_scope(scope.strip()):
        return tool_result(
            False,
            "bad_scope",
            "scope must be shop or customer:<name>.",
            hint="Priya's allergy is scope customer:priya, not shop.",
        )
    if not isinstance(kind, str) or kind.strip() not in KINDS:
        return tool_result(
            False,
            "bad_kind",
            "kind must be preference, constraint, or belief.",
            hint="An allergy is a constraint. A milk choice is a preference.",
        )
    if not isinstance(source, str) or not source.strip() or len(source) > MAX_SOURCE:
        return tool_result(
            False,
            "bad_source",
            "source is required and must be short.",
            hint="Name who said it. Example: staff note, day 1.",
        )
    scope = scope.strip()
    refusal = rejects_generalization(text.strip(), scope)
    if refusal:
        return tool_result(
            False,
            refusal,
            "This write would turn a guest fact into a shop rule.",
            hint="Keep the guest on scope customer:<name>. Do not rewrite the menu.",
        )
    record = {
        "id": "mem_" + uuid.uuid4().hex[:8],
        "text": text.strip(),
        "scope": scope,
        "kind": kind.strip(),
        "source": source.strip(),
        "updated": date.today().isoformat(),
        "status": "active",
    }
    store = load_store(path)
    store["records"].append(record)
    save_store(path, store)
    return tool_result(True, "stored", "Appended a record. Older records were left as they were.", record=record)


def memory_search(path: Path, query: str, scope: str | None = None) -> str:
    if query is None:
        query = ""
    if not isinstance(query, str):
        return tool_result(False, "bad_query", "query must be a string.", hint="Pass a name, an allergy, or an empty string.")
    if scope is not None and scope != "" and not valid_scope(scope):
        return tool_result(
            False,
            "bad_scope",
            "scope must be shop or customer:<name> when you set it.",
            hint="Omit scope to search every active record.",
        )
    needle = query.strip().lower()
    store = load_store(path)
    found = []
    for record in store["records"]:
        if record.get("status") != "active":
            continue
        if scope and record.get("scope") != scope:
            continue
        haystack = " ".join(
            str(record.get(field, "")) for field in ("text", "scope", "kind", "id")
        ).lower()
        if needle and needle not in haystack:
            continue
        found.append(record)
        if len(found) >= MAX_SEARCH:
            break
    return tool_result(
        True,
        "ok",
        f"{len(found)} active record(s).",
        records=found,
        hint="" if found else "No active memory matched. Do not invent a preference.",
    )


def memory_forget(path: Path, memory_id: str) -> str:
    """Mark one record forgotten without deleting it.

    TODO(learner): load the store, find ``memory_id``, set ``status`` to
    ``"forgotten"``, save, and return the record. Do not remove the row.
    ``memory_search`` already skips forgotten rows. ``memory_get`` still
    returns them so the bad belief can be audited.

    The starter leaves the file unchanged.
    """
    if not isinstance(memory_id, str) or not memory_id.strip():
        return tool_result(False, "bad_id", "id is required.", hint="Pass an id from memory_search.")
    return tool_result(
        False,
        "forget_not_implemented",
        "forget is not implemented yet. The record is unchanged.",
        hint="In memory_forget, set status to forgotten and save the store. Do not delete the row.",
        id=memory_id.strip(),
    )
