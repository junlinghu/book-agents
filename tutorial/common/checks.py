"""Lesson checks. A miss warns and the notebook continues."""


def check(condition, message):
    """Print whether a lesson expectation held.

    A live model can phrase an answer differently. The warning names the
    miss without stopping the notebook.
    """
    if condition:
        print("check ok:", message)
        return
    print("check warning:", message)


__all__ = [
    "check",
]
