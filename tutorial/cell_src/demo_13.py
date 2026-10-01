reset_db()
result = run_agent(
    "Which products are at or below their reorder point, and may we ship oat milk?",
    "13-trace",
    system_text(),
    trace_id="trace-low-stock",
)
print("ANSWER:", result["text"])
print("SPANS:")
print(json.dumps(result["spans"], indent=2, sort_keys=True))
blob = json.dumps(result["spans"])
check(result["stopped"] == "final", "traced question finished")
check(len(result["spans"]) >= 2, "the turn span and at least one tool span were recorded")
check(all(span["user"]["id"] == "counter-lead" for span in result["spans"]), "every span names the user")
check(all(span["agent"]["id"] == "shop-concierge" for span in result["spans"]), "every span names the agent")
check(any(span["actor"]["kind"] == "tool" for span in result["spans"]), "a tool has its own actor")
check("sk-" not in blob and "canary" not in blob.lower(), "the trace does not carry a secret")
check("does not ship" in result["text"].lower(), "the answer is still grounded")
