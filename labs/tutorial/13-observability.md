        # Tutorial 13. Traces and identity

        ## Purpose

        Print a structured trace for the low-stock question. Every span names `counter-lead`, `shop-concierge`, and the tool that ran. The trace does not copy API keys or the supplier canary. You can explain the run from the spans without reading the model provider's private logs.

        ## What you should learn

        - Identity is a field: user, agent, and tool are different actors.
- A confirm or an error is a status, not a hidden branch.
- Do not put secrets, page bodies, or raw credentials on a span.
- The answer is still grounded in the shelf and the policy file.

        ## How this maps to the book

        | Tutorial idea | Book chapter and lab |
        |---|---|
        | Spans you can replay without a collector | Chapter 22, `labs/ch22-identity-and-observability` |

        The café in these files is fictional. Prices, hours, and the shelf match the Local Shop Concierge labs. Do not point the tools at a private document.

        ## How to run

        From the repository root, with the virtualenv from `labs/README.md` active:

        ```bash
        jupyter notebook labs/tutorial/13-observability.ipynb
        ```

        In VS Code or Cursor, open `labs/tutorial/13-observability.ipynb` and choose Run All. The setup cell walks parent folders until it finds `labs/common/client.py`, so the kernel may start in `labs/tutorial` or at the repo root.

        Scripted demo (no API call):

        ```bash
        DEMO_MODE=1 jupyter nbconvert --to notebook --execute labs/tutorial/13-observability.ipynb --output /tmp/13-observability-out.ipynb
        ```

        Live Chat Completions API:

        ```bash
        DEMO_MODE=0 jupyter nbconvert --to notebook --execute labs/tutorial/13-observability.ipynb --output /tmp/13-observability-out.ipynb
        ```

        `DEMO_MODE=0` needs `OPENAI_API_KEY` in the repo-root `.env`. `DEMO_MODE` unset uses the API when a key is present and the scripted demo when it is not. The notebook's first code cell can also set `DEMO_MODE` to `True` or `False`.

        This notebook is standalone. The cells include the working code from earlier tutorials and then add this lesson.

        Series map: [README.md](README.md).
