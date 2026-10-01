reset_memory()
print("previous shift wrote memory; this message list starts empty")
print(memory_set({
    "text": "Priya is allergic to almonds.",
    "scope": "customer:priya",
    "kind": "constraint",
    "source": "previous shift",
}))
result = run_agent(
    "Recommend a pastry for Priya.",
    system_text(),
)
print("ANSWER:", result["text"])
joined = "\n".join(result["tool_log"])
check(result["stopped"] == "final", "recommendation finished")
check("load_skill" in joined, "the recommend skill was loaded")
check("memory_search" in joined, "memory from tutorial 5 was searched")
check("read_shop_file" in joined, "the FAQ was read instead of trusting the skill as a menu")
check("cardamom" in result["text"].lower() and "almond" in result["text"].lower(), "the bun and the allergy are both in the answer")
check("nut-free" in result["text"].lower(), "the skill's refusal is in the answer")
