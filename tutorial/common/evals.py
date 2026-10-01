"""Small grader over an answer and a tool log."""


def grade_answer(text, tool_log, contains, excludes, tool_name=None):
    """Small grader. A failure is a list of reasons. An empty list is a pass."""
    failures = []
    lowered = (text or "").lower()
    for needle in contains:
        if needle.lower() not in lowered:
            failures.append("missing " + needle)
    for banned in excludes:
        if banned.lower() in lowered:
            failures.append("should not say " + banned)
    if tool_name and not any(tool_name in line for line in tool_log):
        failures.append("did not use " + tool_name)
    return failures


def print_grade(case_id, failures):
    if failures:
        print("FAIL", case_id + ":", "; ".join(failures))
    else:
        print("PASS", case_id)
    return not failures

__all__ = [
    "grade_answer",
    "print_grade",
]
