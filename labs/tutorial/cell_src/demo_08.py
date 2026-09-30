reset_db()
print("=== checker on two proposals, no model required ===")
bad = verify_proposal({"sku": "OM-32", "qty": 1000, "ship": True, "citation": ""})
good_row = row_for("OM-32")
good = verify_proposal({
    "sku": "OM-32",
    "qty": good_row["gap"],
    "ship": False,
    "citation": "inventory",
})
print(bad)
print(good)
check(json.loads(bad)["status"] == "rejected", "an invented quantity and a ship flag fail")
check("not_shippable" in bad and "missing_citation" in bad, "ship and citation rules both fire")
check(json.loads(good)["status"] == "accepted", "the shelf gap passes the checker")

print("=== the agent may propose; the checker decides ===")
result = run_agent(
    "Propose an oat milk restock and have the checker score it. Do not ship it.",
    "8-verify",
    system_text(),
)
print("ANSWER:", result["text"])
check(result["stopped"] == "final", "verify demo finished")
check("query_inventory" in "\n".join(result["tool_log"]), "the proposal looked at the shelf")
check("verify_proposal" in "\n".join(result["tool_log"]), "a separate checker ran")
check("accepted" in result["text"].lower(), "the reported proposal is the one the checker accepted")
