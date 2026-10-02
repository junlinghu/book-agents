"""Graded cases over an answer and a tool log.

Five cases call the model. One canned case is a known failure and stays
in the set on purpose.
"""


CASES = (
    {
        "id": "opened-jar",
        "live": True,
        "kind": "support",
        "question": "I opened a jar of fig jam last night. Can I return it?",
        "contains": ["final sale"],
        "excludes": [],
        "tools": ["get_store_fact"],
    },
    {
        "id": "chili-ohio",
        "live": True,
        "kind": "buy",
        "question": "Do you have Calabrian chili oil, and can you ship a jar to Ohio?",
        "contains": ["ohio"],
        "excludes": ["out of stock"],
        "tools": ["query_catalog", "get_store_fact"],
    },
    {
        "id": "sesame-crunch",
        "live": True,
        "kind": "support",
        "question": "Does the sesame crunch contain sesame? I need to avoid sesame.",
        "contains": ["sesame"],
        "excludes": [],
        "tools": ["get_store_fact"],
    },
    {
        "id": "labneh-ohio",
        "live": True,
        "kind": "buy",
        "question": "Can you ship fresh labneh to Ohio?",
        "contains": ["does not ship"],
        "excludes": [],
        "tools": ["query_catalog"],
    },
    {
        "id": "cracked-jar",
        "live": True,
        "kind": "support",
        "question": "My jar arrived cracked. What should I do?",
        "contains": ["48"],
        "excludes": [],
        "tools": ["get_store_fact"],
    },
    {
        "id": "canned-cash-refund",
        "live": False,
        "kind": "known-failure",
        "question": "(canned) opened jar, no tools",
        "text": (
            "Opened jars get a full cash refund. "
            "The guest password is harbor-guest-123."
        ),
        "tool_log": [],
        "contains": ["final sale"],
        "excludes": ["cash refund", "password"],
        "tools": ["get_store_fact"],
    },
)


def grade_answer(text, tool_log, contains, excludes, tool_name=None, tools=None):
    """A failure is a list of reasons. An empty list is a pass."""
    failures = []
    lowered = (text or "").lower()
    for needle in contains:
        if needle.lower() not in lowered:
            failures.append("missing " + needle)
    for banned in excludes:
        if banned.lower() in lowered:
            failures.append("should not say " + banned)
    names = list(tools or [])
    if tool_name and tool_name not in names:
        names.append(tool_name)
    for name in names:
        if not any(name in line for line in tool_log):
            failures.append("did not use " + name)
    return failures


def grade_case(case, text, tool_log):
    """Grade one case dict from ``CASES``."""
    return grade_answer(
        text,
        tool_log,
        case.get("contains") or [],
        case.get("excludes") or [],
        tools=case.get("tools"),
    )


def print_grade(case_id, failures):
    if failures:
        print("FAIL", case_id + ":", "; ".join(failures))
    else:
        print("PASS", case_id)
    return not failures


__all__ = [
    "CASES",
    "grade_answer",
    "grade_case",
    "print_grade",
]
