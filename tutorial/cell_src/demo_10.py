reset_db()
reset_tickets()

print("=== unconfirmed ticket ===")
result = run_agent(
    "Write a restock ticket for oat milk. Do not charge a card.",
    "10-ticket",
    system_text(),
)
print("ANSWER:", result["text"])
check(result["stopped"] == "final", "the model can finish while the ticket waits")
check(any("CONFIRM_REQUIRED" in line for line in result["tool_log"]), "write_ticket is confirm-tier")
check(not any(TICKETS.glob("*.md")), "no ticket file before a matching token")

tokens = set(re.findall(r"token=([0-9a-f]{8})", "\n".join(result["tool_log"])))
print("approval tokens:", ", ".join(sorted(tokens)))
check(len(tokens) == 1, "one ticket call produced one token")

print("=== charge_card stays denied, even with a token for that exact call ===")
charge_args = {"amount_cents": 100}
charge = gate_call("charge_card", charge_args, {approval_token("charge_card", charge_args)})
print(format_decision(charge))
check(charge["decision"] == "denied", "never-tier ignores the token")

print("=== same ticket, token supplied ===")
confirmed = run_agent(
    "Write a restock ticket for oat milk. Do not charge a card.",
    "10-ticket",
    system_text(),
    confirmed_tokens=tokens,
)
print("ANSWER:", confirmed["text"])
written = sorted(TICKETS.glob("*.md"))
check(len(written) == 1, "one ticket file exists after confirmation")
print(written[0].read_text(encoding="utf-8"))
check("WROTE" in "\n".join(confirmed["tool_log"]), "the tool ran only after the token matched")
