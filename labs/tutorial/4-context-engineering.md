        # Tutorial 4. Context engineering

        ## Purpose

        Show context rot with three huddle notes. Pasting every body overflows a small turn budget. A catalog of titles fits. The agent reads the oat-milk note and the Thursday bun note, checks the shelf, and leaves the long picnic note on disk.

        ## What you should learn

        - A turn budget is a character cap for what you put in the prompt on purpose.
- A per-note cap refuses an oversized body even if the model asks for it.
- Selection is a tool call, not a bigger paste.
- The shelf tool still confirms a number that also appears in a note.

        ## How this maps to the book

        | Tutorial idea | Book chapter and lab |
        |---|---|
        | Notes, caps, and a map instead of a paste | Chapter 5, `labs/ch05-context-engineering` |

        The café in these files is fictional. Prices, hours, and the shelf match the Local Shop Concierge labs. Do not point the tools at a private document.

        ## How to run

        From the repository root, with the virtualenv from `labs/README.md` active:

        ```bash
        jupyter notebook labs/tutorial/4-context-engineering.ipynb
        ```

        In VS Code or Cursor, open `labs/tutorial/4-context-engineering.ipynb` and choose Run All. The setup cell walks parent folders until it finds `labs/common/client.py`, so the kernel may start in `labs/tutorial` or at the repo root.

        Scripted demo (no API call):

        ```bash
        DEMO_MODE=1 jupyter nbconvert --to notebook --execute labs/tutorial/4-context-engineering.ipynb --output /tmp/4-context-engineering-out.ipynb
        ```

        Live Chat Completions API:

        ```bash
        DEMO_MODE=0 jupyter nbconvert --to notebook --execute labs/tutorial/4-context-engineering.ipynb --output /tmp/4-context-engineering-out.ipynb
        ```

        `DEMO_MODE=0` needs `OPENAI_API_KEY` in the repo-root `.env`. `DEMO_MODE` unset uses the API when a key is present and the scripted demo when it is not. The notebook's first code cell can also set `DEMO_MODE` to `True` or `False`.

        This notebook is standalone. The cells include the working code from earlier tutorials and then add this lesson.

        Series map: [README.md](README.md).
