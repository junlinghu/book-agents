        # Tutorial 8. A verification loop

        ## Purpose

        Split proposing from checking. A proposal that orders 1000 cartons and ships dairy fails. A proposal whose quantity is par minus on_hand, that does not ship, and that cites the shelf, passes. The agent then calls the same checker as a tool.

        ## What you should learn

        - The checker recomputes the gap from the database.
- Dairy and bakery do not ship, even if the proposal says they do.
- A missing citation is a failure.
- The agent's accepted plan is the one the checker accepted, not the boldest number.

        ## How this maps to the book

        | Tutorial idea | Book chapter and lab |
        |---|---|
        | A separate checker with hard findings | Chapter 11, `labs/ch11-verification-loops` |

        The café in these files is fictional. Prices, hours, and the shelf match the Local Shop Concierge labs. Do not point the tools at a private document.

        ## How to run

        From the repository root, with the virtualenv from `labs/README.md` active:

        ```bash
        jupyter notebook labs/tutorial/8-verification.ipynb
        ```

        In VS Code or Cursor, open `labs/tutorial/8-verification.ipynb` and choose Run All. The setup cell walks parent folders until it finds `labs/common/client.py`, so the kernel may start in `labs/tutorial` or at the repo root.

        Scripted demo (no API call):

        ```bash
        DEMO_MODE=1 jupyter nbconvert --to notebook --execute labs/tutorial/8-verification.ipynb --output /tmp/8-verification-out.ipynb
        ```

        Live Chat Completions API:

        ```bash
        DEMO_MODE=0 jupyter nbconvert --to notebook --execute labs/tutorial/8-verification.ipynb --output /tmp/8-verification-out.ipynb
        ```

        `DEMO_MODE=0` needs `OPENAI_API_KEY` in the repo-root `.env`. `DEMO_MODE` unset uses the API when a key is present and the scripted demo when it is not. The notebook's first code cell can also set `DEMO_MODE` to `True` or `False`.

        This notebook is standalone. The cells include the working code from earlier tutorials and then add this lesson.

        Series map: [README.md](README.md).
