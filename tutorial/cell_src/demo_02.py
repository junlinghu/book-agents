def run_exchange(user_text):
    """One model call, tool results, second model call. Tutorial 3 wraps this in a loop."""
    messages = [
        {"role": "system", "content": system_text()},
        {"role": "user", "content": user_text},
    ]
    print("QUESTION:", user_text)
    print()
    first = chat(messages, TOOLS)
    if not first["tool_calls"]:
        print("ANSWER:", first["content"])
        print("stop: final (no tool call)")
        return first["content"] or "", []
    messages.append(assistant_message(first))
    log = []
    for call in first["tool_calls"]:
        result = call_tool(call)
        line = call["name"] + " " + json.dumps(call["arguments"], sort_keys=True)
        log.append(line)
        print("[tool]", line)
        print(preview(result))
        print()
        messages.append({
            "role": "tool",
            "tool_call_id": call["id"],
            "content": result,
        })
    second = chat(messages, TOOLS)
    print("ANSWER:", second["content"])
    print("stop: final")
    return second["content"] or "", log


reset_db()
print("=== shelf and policy ===")
answer, log = run_exchange(
    "Which products are at or below their reorder point, and may we ship oat milk?",
)
check(any(line.startswith("query_inventory") for line in log), "inventory tool ran")
check(any(line.startswith("read_shop_file") for line in log), "policy file was read")
check("does not ship" in answer.lower(), "answer uses the shipping rule from the file")
check("HB-12" in answer and "OM-32" in answer, "low-stock skus are named")

print("=== carried forward: one shop fact ===")
fact, fact_log = run_exchange(
    "Can a customer return an opened bag of house coffee?",
)
check(any(line.startswith("get_shop_fact") for line in fact_log), "the lesson 1 tool still runs")
check("final sale" in fact.lower(), "the return rule still comes from the tool")
