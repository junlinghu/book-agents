print("registered tools:", [tool["function"]["name"] for tool in TOOLS])
print()

question = "Can a customer return an opened bag of house coffee?"
messages = [
    {"role": "system", "content": system_text()},
    {"role": "user", "content": question},
]
print("QUESTION:", question)
print()

# The model proposes a tool call. This process executes it. The model does not open the file.
first = chat(messages, TOOLS)
messages.append(assistant_message(first))
names = [call["name"] for call in first["tool_calls"]]
print("tool_calls:", names)
check("get_shop_fact" in names, "the model asks for get_shop_fact")

if not first["tool_calls"]:
    print("ANSWER:", first["content"])
    print("stop: final (no tool call)")
    check(False, "the model asked for a tool before answering")
else:
    for call in first["tool_calls"]:
        result = call_tool(call)
        print("[tool]", call["name"], json.dumps(call["arguments"], sort_keys=True))
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
    check(not second["tool_calls"], "the second turn is a final answer")
    check("final sale" in (second["content"] or "").lower(), "answer says opened coffee is final sale")
