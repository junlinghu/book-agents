        # Tutorial 5. Session and durable memory

        ## Purpose

        Separate the chat transcript from durable memory. Turn 1 stores Priya's almond allergy. Turn 2 starts a new message list and finds the row in the JSON file. Shop policy stays in the docs. It is not copied into memory.

        ## What you should learn

        - Session memory is the message list. It dies when you start a new list.
- Durable memory is a file. `memory_set` appends. `memory_search` reads.
- A guest allergy is a constraint on that guest, not a shop belief.
- The earlier tools and the loop still run in this same notebook.

        ## How this maps to the book

        | Tutorial idea | Book chapter and lab |
        |---|---|
        | JSON memory that survives the process | Chapter 6, `labs/ch06-memory` |

        The café in these files is fictional. Prices, hours, and the shelf match the Local Shop Concierge labs. Do not point the tools at a private document.

        ## How to run

        From the repository root, with the virtualenv from `labs/README.md` active:

        ```bash
        jupyter notebook labs/tutorial/5-memory.ipynb
        ```

        In VS Code or Cursor, open `labs/tutorial/5-memory.ipynb` and choose Run All. The setup cell walks parent folders until it finds `labs/common/client.py`, so the kernel may start in `labs/tutorial` or at the repo root.

        Scripted demo (no API call):

        ```bash
        DEMO_MODE=1 jupyter nbconvert --to notebook --execute labs/tutorial/5-memory.ipynb --output /tmp/5-memory-out.ipynb
        ```

        Live Chat Completions API:

        ```bash
        DEMO_MODE=0 jupyter nbconvert --to notebook --execute labs/tutorial/5-memory.ipynb --output /tmp/5-memory-out.ipynb
        ```

        `DEMO_MODE=0` needs `OPENAI_API_KEY` in the repo-root `.env`. `DEMO_MODE` unset uses the API when a key is present and the scripted demo when it is not. The notebook's first code cell can also set `DEMO_MODE` to `True` or `False`.

        This notebook is standalone. The cells include the working code from earlier tutorials and then add this lesson.

        Series map: [README.md](README.md).
