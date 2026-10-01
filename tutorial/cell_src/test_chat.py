def test_chat(question):
    """One Chat Completions call with no tools. Prints the assistant answer.

    Uses the key and model already loaded by the setup cell.
    """
    require_key()
    turn = chat([{"role": "user", "content": question}], tools=[])
    print("ANSWER:", turn["content"])
    return turn


test_chat("Reply with exactly: ok")
