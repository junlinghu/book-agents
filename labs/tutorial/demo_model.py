"""Scripted stand-in for the chat model.

The tools, the loop, and the gates in the notebooks are real. This
module only decides the next assistant turn when ``DEMO_MODE`` is on,
so a lesson prints the same trace without an API key.

Plans read tool results. A quantity in a later call comes from the
inventory JSON the tool already returned.
"""

from __future__ import annotations

import json


def scripted_turn(messages, tools, lesson):
    """Return ``content`` and ``tool_calls`` for this lesson and history."""
    del tools  # The notebook's schema is what actually runs. Plans name tools.
    planner = PLANS.get(lesson)
    if planner is None:
        known = ", ".join(sorted(PLANS))
        raise KeyError("No demo script for lesson " + repr(lesson) + ". Known: " + known)
    index = sum(1 for message in messages if message.get("role") == "assistant")
    return planner(index, messages)


def _calls(index, pairs):
    calls = []
    for offset, (name, arguments) in enumerate(pairs):
        calls.append({
            "id": "call_" + str(index) + "_" + str(offset),
            "name": name,
            "arguments": arguments,
            "raw": json.dumps(arguments, sort_keys=True),
        })
    return {"content": "", "tool_calls": calls}


def _final(text):
    return {"content": text, "tool_calls": []}


def results_by_name(messages):
    """Map tool name to the result strings, in call order."""
    names = {}
    found = {}
    for message in messages:
        if message.get("role") == "assistant":
            for call in message.get("tool_calls") or []:
                function = call.get("function") or {}
                names[call.get("id")] = function.get("name", "")
        elif message.get("role") == "tool":
            name = names.get(message.get("tool_call_id"), "")
            found.setdefault(name, []).append(message.get("content") or "")
    return found


def result_text(messages, name, default=""):
    rows = results_by_name(messages).get(name) or []
    if not rows:
        return default
    return rows[-1]


def inventory_rows(messages):
    raw = result_text(messages, "query_inventory", "")
    if not raw:
        return []
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return []
    return list(payload.get("rows") or [])


def render_returns(messages):
    text = result_text(messages, "get_shop_fact")
    if "final sale" not in text.lower() and "Opened coffee" not in text:
        return "The returns tool did not state a rule I can quote."
    return (
        "No. Opened coffee is final sale. Unopened retail coffee may be returned "
        "within 14 days for Hearth card credit, with a receipt. "
        "(get_shop_fact: returns, docs/policy.md)"
    )


def render_low_and_ship(messages):
    rows = inventory_rows(messages)
    if rows:
        skus = ", ".join(row["sku"] for row in rows)
        stock = "At or below reorder point: " + skus + "."
    else:
        stock = "The inventory tool returned no low-stock rows."
    policy = result_text(messages, "read_shop_file")
    if "does not ship" in policy and "milk" in policy:
        ship = " Oat milk does not ship. The café does not ship milk (docs/policy.md)."
    else:
        ship = " The policy tool did not show the milk rule."
    return stock + ship


def render_context(messages):
    notes = "\n".join(results_by_name(messages).get("read_note") or [])
    rows = inventory_rows(messages)
    if rows:
        on_hand = str(rows[0].get("on_hand"))
    else:
        on_hand = "?"
    if "3 cartons" not in notes:
        milk = "The oat-milk note did not include the carton count."
    else:
        milk = "The oat-milk note says 3 cartons, and the shelf shows OM-32 on hand at " + on_hand + "."
    if "24 cardamom buns" not in notes:
        buns = " The Thursday note did not include the bun count."
    else:
        buns = " The Thursday note says the bake was 24 cardamom buns."
    return (
        milk
        + buns
        + " The picnic note was left on disk. Titles were in the prompt; bodies came back through read_note."
    )


def render_saved(_messages):
    return (
        "Saved Priya's almond allergy as a constraint in the JSON memory file. "
        "That file is the durable record. This chat is only the session."
    )


def render_recall(messages):
    text = result_text(messages, "memory_search")
    if "almond" not in text.lower():
        return "Memory search did not return an almond constraint."
    return (
        "Priya is allergic to almonds (memory constraint, customer:priya). "
        "This turn's message list did not contain the earlier sentence. The JSON file did."
    )


def render_recommend(messages):
    memory = result_text(messages, "memory_search")
    faq = result_text(messages, "read_shop_file")
    skill = result_text(messages, "load_skill")
    if "almond" not in memory.lower():
        return "I do not have Priya's constraint in memory, so I will not guess a pastry."
    if "almonds" not in faq.lower():
        return "The FAQ tool did not list allergens, so I will not name a pastry."
    if "SKILL: recommend" not in skill:
        return "The recommend skill did not load."
    return (
        "Do not serve Priya the cardamom bun. Memory says she is allergic to almonds, "
        "and docs/faq.md says the bun contains almonds. The FAQ lists no other pastry. "
        "I will not promise a nut-free order. (skill: recommend, docs/faq.md)"
    )


def render_page(messages, extra):
    page = result_text(messages, "fetch_page")
    rows = inventory_rows(messages)
    if rows:
        on_hand = str(rows[0].get("on_hand"))
        sku = rows[0].get("sku", "OM-32")
    else:
        on_hand = "?"
        sku = "OM-32"
    if "UNTRUSTED PAGE TEXT" not in page or "$3.10" not in page:
        return "The page tool did not return a labeled supplier price."
    return (
        "The supplier page claims oat milk at $3.10 per carton. That figure is untrusted page text, "
        "not a Hearth Lane price. Shelf " + sku + " on hand is " + on_hand + " (inventory). "
        + extra
    )


def render_verify(messages):
    raw = result_text(messages, "verify_proposal")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return "The checker did not return JSON."
    if payload.get("status") != "accepted":
        return "The checker rejected the proposal: " + ", ".join(payload.get("findings") or [])
    return (
        "Checker accepted "
        + str(payload.get("sku"))
        + " qty "
        + str(payload.get("expected_qty"))
        + ". The quantity is the shelf gap, it does not ship, and it cites inventory."
    )


def render_ticket(messages):
    writes = results_by_name(messages).get("write_ticket") or []
    joined = "\n".join(writes)
    if "CONFIRM_REQUIRED" in joined:
        return (
            "The restock ticket is planned and checked. It is waiting for confirmation. "
            "I did not write the file, and I did not charge a card."
        )
    if any(line.startswith("WROTE") for line in writes):
        return "Confirmed. The ticket file is written. No card was charged."
    return "The ticket tool did not return a confirm challenge or a write."


def render_safe_page(messages):
    return render_page(
        messages,
        "Instructions inside the page were not executed. I did not charge a card, read a secret, or change the bun price.",
    )


def render_web(messages):
    return render_page(
        messages,
        "I treated the page as a sensor. I did not follow its instructions.",
    )


def render_handoff(messages):
    if "UNTRUSTED SUPPLIER NOTE" not in result_text(messages, "read_supplier_note"):
        return "The supplier note was not labeled as untrusted."
    if not inventory_rows(messages):
        return "Inventory did not return the house blend row."
    return (
        "Inputs are loaded: the shelf row and an untrusted supplier note. "
        "The stocker and the checker, not this sentence, set the quantity."
    )


def render_hours(messages):
    faq = "\n".join(results_by_name(messages).get("read_shop_file") or [])
    if "Closed Monday" not in faq and "closed Monday" not in faq.lower():
        return "The FAQ tool did not show hours."
    return (
        "Hours are Tuesday–Friday 7:30–15:30, Saturday–Sunday 8:00–16:00, closed Monday "
        "(docs/faq.md). The second read was the cached FAQ, not a second story."
    )


def render_capstone(messages):
    writes = results_by_name(messages).get("write_ticket") or []
    joined = "\n".join(writes)
    if "CONFIRM_REQUIRED" in joined:
        return (
            "Planned the Tuesday restock from the shelf gap, the policy, the oat-milk note, "
            "shop memory, and the restock skill. Supplier page text stayed untrusted. "
            "Tickets are waiting for confirmation. No card was charged."
        )
    if writes and all(line.startswith("WROTE") for line in writes):
        return (
            "Confirmed the Tuesday restock. Tickets are filed for the shelf gaps. "
            "No card was charged."
        )
    return "The restock stopped before the ticket result was clear."


def plan_returns(index, messages):
    if index == 0:
        return _calls(index, [("get_shop_fact", {"topic": "returns"})])
    return _final(render_returns(messages))


def plan_data(index, messages):
    if index == 0:
        return _calls(index, [
            ("query_inventory", {"only_low": True}),
            ("read_shop_file", {"path": "policy.md"}),
        ])
    return _final(render_low_and_ship(messages))


def plan_low_stock(index, messages):
    if index == 0:
        return _calls(index, [("query_inventory", {"only_low": True})])
    if index == 1:
        return _calls(index, [("read_shop_file", {"path": "policy.md"})])
    return _final(render_low_and_ship(messages))


def plan_always_query(index, messages):
    del messages
    return _calls(index, [("query_inventory", {"only_low": True})])


def plan_context(index, messages):
    if index == 0:
        return _calls(index, [("list_notes", {})])
    if index == 1:
        return _calls(index, [
            ("read_note", {"name": "oat-milk.md"}),
            ("read_note", {"name": "thursday-buns.md"}),
            ("query_inventory", {"sku": "OM-32", "only_low": False}),
        ])
    return _final(render_context(messages))


def plan_save(index, messages):
    if index == 0:
        return _calls(index, [("memory_set", {
            "text": "Priya is allergic to almonds.",
            "scope": "customer:priya",
            "kind": "constraint",
            "source": "told at the counter",
        })])
    return _final(render_saved(messages))


def plan_recall(index, messages):
    if index == 0:
        return _calls(index, [("memory_search", {"query": "priya", "scope": "customer:priya"})])
    return _final(render_recall(messages))


def plan_skill(index, messages):
    if index == 0:
        return _calls(index, [("load_skill", {"name": "recommend"})])
    if index == 1:
        return _calls(index, [
            ("memory_search", {"query": "priya", "scope": "customer:priya"}),
            ("read_shop_file", {"path": "faq.md"}),
        ])
    return _final(render_recommend(messages))


def plan_web(index, messages):
    if index == 0:
        return _calls(index, [
            ("fetch_page", {"url": "https://suppliers.example/mill-and-birch"}),
            ("query_inventory", {"sku": "OM-32", "only_low": False}),
        ])
    return _final(render_web(messages))


def _proposal_from_shelf(index, messages, sku):
    rows = [row for row in inventory_rows(messages) if row.get("sku") == sku]
    if not rows:
        rows = inventory_rows(messages)
    row = rows[0]
    return _calls(index, [("verify_proposal", {
        "sku": row["sku"],
        "qty": row["gap"],
        "ship": False,
        "citation": "inventory",
    })])


def plan_verify(index, messages):
    if index == 0:
        return _calls(index, [("query_inventory", {"sku": "OM-32", "only_low": False})])
    if index == 1:
        return _proposal_from_shelf(index, messages, "OM-32")
    return _final(render_verify(messages))


def plan_ship(index, messages):
    if index == 0:
        return _calls(index, [("read_shop_file", {"path": "policy.md"})])
    return _final(render_ship(messages))


def render_ship(messages):
    policy = result_text(messages, "read_shop_file")
    if "does not ship" not in policy or "milk" not in policy:
        return "The policy tool did not show the milk rule."
    return (
        "No. Whole milk does not ship. The café does not ship milk or anything that needs "
        "refrigeration (docs/policy.md)."
    )


def plan_ticket(index, messages):
    if index == 0:
        return _calls(index, [("query_inventory", {"sku": "OM-32", "only_low": False})])
    if index == 1:
        return _proposal_from_shelf(index, messages, "OM-32")
    if index == 2:
        row = inventory_rows(messages)[0]
        return _calls(index, [("write_ticket", {
            "sku": row["sku"],
            "qty": row["gap"],
            "reason": "low stock gap to par",
            "citation": "inventory",
        })])
    return _final(render_ticket(messages))


def plan_safe(index, messages):
    if index == 0:
        return _calls(index, [
            ("fetch_page", {"url": "https://suppliers.example/mill-and-birch"}),
            ("query_inventory", {"sku": "OM-32", "only_low": False}),
        ])
    return _final(render_safe_page(messages))


def plan_handoff(index, messages):
    if index == 0:
        return _calls(index, [
            ("query_inventory", {"sku": "HB-12", "only_low": False}),
            ("read_supplier_note", {}),
        ])
    return _final(render_handoff(messages))


def plan_hours(index, messages):
    if index == 0:
        return _calls(index, [("read_shop_file", {"path": "faq.md"})])
    if index == 1:
        return _calls(index, [("read_shop_file", {"path": "faq.md"})])
    return _final(render_hours(messages))


def _focus_rows(messages):
    wanted = []
    for row in inventory_rows(messages):
        if row.get("sku") in {"OM-32", "HB-12"}:
            wanted.append(row)
    return wanted


def plan_capstone(index, messages):
    if index == 0:
        return _calls(index, [("load_skill", {"name": "restock"})])
    if index == 1:
        return _calls(index, [("query_inventory", {"only_low": True})])
    if index == 2:
        return _calls(index, [
            ("read_shop_file", {"path": "policy.md"}),
            ("read_note", {"name": "oat-milk.md"}),
            ("memory_search", {"query": "dairy", "scope": "shop"}),
        ])
    if index == 3:
        return _calls(index, [("fetch_page", {"url": "https://suppliers.example/mill-and-birch"})])
    if index == 4:
        pairs = []
        for row in _focus_rows(messages):
            pairs.append(("verify_proposal", {
                "sku": row["sku"],
                "qty": row["gap"],
                "ship": False,
                "citation": "inventory+docs/policy.md",
            }))
        return _calls(index, pairs)
    if index == 5:
        pairs = []
        for row in _focus_rows(messages):
            pairs.append(("write_ticket", {
                "sku": row["sku"],
                "qty": row["gap"],
                "reason": "low stock gap to par",
                "citation": "inventory+docs/policy.md",
            }))
        return _calls(index, pairs)
    return _final(render_capstone(messages))


PLANS = {
    "1-using-tool": plan_returns,
    "2-data-and-files": plan_data,
    "3-agent-loop": plan_low_stock,
    "3-max-steps": plan_always_query,
    "3-repeat": plan_always_query,
    "4-context": plan_context,
    "5-memory-save": plan_save,
    "5-memory-recall": plan_recall,
    "6-skills": plan_skill,
    "7-web": plan_web,
    "8-verify": plan_verify,
    "9-return": plan_returns,
    "9-ship": plan_ship,
    "10-ticket": plan_ticket,
    "11-safe": plan_safe,
    "12-handoff": plan_handoff,
    "13-trace": plan_low_stock,
    "14-cost": plan_hours,
    "15-shop-manager": plan_capstone,
}
