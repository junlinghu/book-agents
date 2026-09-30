        # Tutorial 12. Constrained roles and a handoff

        ## Purpose

        Two roles pass a structured artifact. The supplier note says to order 1000 bags. The stocker sets quantity to par minus on_hand and stores the note as untrusted data. The checker rejects an artifact that copied 1000. The chat model can load inputs. It does not get the last word.

        ## What you should learn

        - A handoff is a dict with a role, the shelf numbers, and the untrusted note.
- The checker compares the artifact to the shelf row. It does not trust the note.
- A failed check stops the handoff. It does not become an order.
- The fetch tool, the gate, and the loop are still in this notebook.

        ## How this maps to the book

        | Tutorial idea | Book chapter and lab |
        |---|---|
        | Roles, contracts, and an untrusted supplier note | Chapter 23, `labs/ch23-multi-agent-patterns` |

        The café in these files is fictional. Prices, hours, and the shelf match the Local Shop Concierge labs. Do not point the tools at a private document.

        ## How to run

        From the repository root, with the virtualenv from `labs/README.md` active:

        ```bash
        jupyter notebook labs/tutorial/12-multi-agent.ipynb
        ```

        In VS Code or Cursor, open `labs/tutorial/12-multi-agent.ipynb` and choose Run All. The setup cell walks parent folders until it finds `labs/common/client.py`, so the kernel may start in `labs/tutorial` or at the repo root.

        Scripted demo (no API call):

        ```bash
        DEMO_MODE=1 jupyter nbconvert --to notebook --execute labs/tutorial/12-multi-agent.ipynb --output /tmp/12-multi-agent-out.ipynb
        ```

        Live Chat Completions API:

        ```bash
        DEMO_MODE=0 jupyter nbconvert --to notebook --execute labs/tutorial/12-multi-agent.ipynb --output /tmp/12-multi-agent-out.ipynb
        ```

        `DEMO_MODE=0` needs `OPENAI_API_KEY` in the repo-root `.env`. `DEMO_MODE` unset uses the API when a key is present and the scripted demo when it is not. The notebook's first code cell can also set `DEMO_MODE` to `True` or `False`.

        This notebook is standalone. The cells include the working code from earlier tutorials and then add this lesson.

        Series map: [README.md](README.md).
