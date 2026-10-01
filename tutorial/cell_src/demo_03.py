reset_db()
question = "Which products are at or below their reorder point, and may we ship oat milk?"

print("=== perceive, reason, act, observe ===")
result = run_agent(question, "3-agent-loop", system_text())
print("ANSWER:", result["text"])
check(result["stopped"] == "final", "loop stopped with a final answer")
check(result["steps"] >= 2, "the loop used more than one model call")
check(any("query_inventory" in line for line in result["tool_log"]), "inventory ran inside the loop")
check(any("read_shop_file" in line for line in result["tool_log"]), "policy was read on a later step")
check("does not ship" in result["text"].lower(), "the answer uses the file, not a guess")

print("=== max steps ===")
capped = run_agent(question, "3-max-steps", system_text(), max_steps=1)
print("ANSWER:", capped["text"])
check(capped["stopped"] == "max_steps", "max_steps stops without inventing an answer")
check("Stopped: reached max steps" in capped["text"], "the harness does not write a customer answer")

print("=== repeated call ===")
repeated = run_agent("List low stock again.", "3-repeat", system_text(), max_steps=6)
print("ANSWER:", repeated["text"])
check(repeated["stopped"] == "repeated_call", "the third identical call stops the loop")
