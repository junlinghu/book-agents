reset_memory()
print("memory file before turn 1:", MEMORY_PATH)
print(MEMORY_PATH.read_text(encoding="utf-8"))

print("=== turn 1: save during this session ===")
saved = run_agent(
    "Remember that Priya is allergic to almonds.",
    "5-memory-save",
    system_text(),
)
print("ANSWER:", saved["text"])
stored = MEMORY_PATH.read_text(encoding="utf-8")
print("memory file after turn 1:")
print(stored)
check(saved["stopped"] == "final", "save turn finished")
check("almond" in stored.lower(), "the JSON file holds the constraint")

print("=== turn 2: new message list, same file ===")
recalled = run_agent(
    "What constraint do we have for Priya before I recommend a pastry?",
    "5-memory-recall",
    system_text(),
)
print("ANSWER:", recalled["text"])
check(recalled["stopped"] == "final", "recall turn finished")
check("memory_search" in "\n".join(recalled["tool_log"]), "recall used the memory tool")
check("almond" in recalled["text"].lower(), "the new session found the durable constraint")
