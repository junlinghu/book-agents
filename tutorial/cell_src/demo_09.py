reset_db()
cases = [
    {
        "id": "opened-return",
        "question": "I opened the house coffee. Can I return it?",
        "contains": ["final sale"],
        "excludes": ["full cash refund"],
        "tool": "get_shop_fact",
    },
    {
        "id": "ship-milk",
        "question": "Please ship a gallon of whole milk to Ohio.",
        "contains": ["does not ship"],
        "excludes": ["tracking number"],
        "tool": "read_shop_file",
    },
]
passed = 0
for case in cases:
    print("===", case["id"], "===")
    result = run_agent(case["question"], system_text())
    print("ANSWER:", result["text"])
    failures = grade_answer(
        result["text"],
        result["tool_log"],
        case["contains"],
        case["excludes"],
        case["tool"],
    )
    if print_grade(case["id"], failures):
        passed += 1

print("=== invented-wifi (a failure kept from an earlier bad answer) ===")
canned = "The Wi-Fi password is hearth123."
print("CANNED ANSWER:", canned)
failures = grade_answer(canned, [], [], ["hearth123"], "read_shop_file")
if print_grade("invented-wifi", failures):
    passed += 1
else:
    check(True, "the canned failure is supposed to fail the grader")
print("scored_passes:", passed, "of 3 (the canned row is in the set because it fails)")
check(passed == 2, "the two tool-using cases pass")
