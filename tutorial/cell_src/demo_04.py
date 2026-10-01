reset_db()
catalog = list_notes({})
print("paste_all_chars:", paste_chars())
print("catalog_chars:", len(catalog))
print("TURN_BUDGET:", TURN_BUDGET)
print("PER_NOTE_CAP:", PER_NOTE_CAP)
print(catalog)
print()
print("oversized note:")
print(read_note({"name": "picnic.md"}))
print()
check(paste_chars() > TURN_BUDGET, "pasting every note exceeds the turn budget")
check(len(catalog) < TURN_BUDGET, "the title catalog fits in the budget")

question = (
    "From the huddle notes, how many oat milk cartons were on hand, "
    "and how many cardamom buns did we bake on Thursday? Check the shelf for OM-32. "
    "Do not load the picnic note."
)
result = run_agent(question, system_text())
print("ANSWER:", result["text"])
joined = "\n".join(result["tool_log"])
check(result["stopped"] == "final", "context run finished")
check("oat-milk.md" in joined and "thursday-buns.md" in joined, "the relevant notes were read")
check("picnic.md" not in joined, "the picnic note was not loaded into the loop")
check("3" in result["text"] and "24" in result["text"], "both counts are in the answer")
check("query_inventory" in joined, "the shelf tool from tutorial 2 still runs")
