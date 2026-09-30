        # Tutorial 11. Prompt injection and untrusted data

        ## Purpose

        The Mill and Birch page asks the concierge to charge a card, read `.env`, and change the bun price. The scripted model reports the wholesale price and does not call those tools. A second cell runs the bad proposals through the path jail and the autonomy gate anyway, because the boundary has to hold when the model is wrong.

        ## What you should learn

        - Untrusted text can sit in the thread. It does not edit the tool list.
- The docs path jail blocks `..` and any file that is not policy or FAQ.
- A canary token in a local fixture must not appear in the tool output.
- Mail to the counter is confirm. Mail to any other domain is never.

        ## How this maps to the book

        | Tutorial idea | Book chapter and lab |
        |---|---|
        | Untrusted page text and a canary | Chapter 21, `labs/ch21-prompt-injection-and-untrusted-data` |
| The gate from the previous tutorial | Chapter 16, `labs/common/autonomy.py` |

        The café in these files is fictional. Prices, hours, and the shelf match the Local Shop Concierge labs. Do not point the tools at a private document.

        ## How to run

        From the repository root, with the virtualenv from `labs/README.md` active:

        ```bash
        jupyter notebook labs/tutorial/11-prompt-injection.ipynb
        ```

        In VS Code or Cursor, open `labs/tutorial/11-prompt-injection.ipynb` and choose Run All. The setup cell walks parent folders until it finds `labs/common/client.py`, so the kernel may start in `labs/tutorial` or at the repo root.

        Scripted demo (no API call):

        ```bash
        DEMO_MODE=1 jupyter nbconvert --to notebook --execute labs/tutorial/11-prompt-injection.ipynb --output /tmp/11-prompt-injection-out.ipynb
        ```

        Live Chat Completions API:

        ```bash
        DEMO_MODE=0 jupyter nbconvert --to notebook --execute labs/tutorial/11-prompt-injection.ipynb --output /tmp/11-prompt-injection-out.ipynb
        ```

        `DEMO_MODE=0` needs `OPENAI_API_KEY` in the repo-root `.env`. `DEMO_MODE` unset uses the API when a key is present and the scripted demo when it is not. The notebook's first code cell can also set `DEMO_MODE` to `True` or `False`.

        This notebook is standalone. The cells include the working code from earlier tutorials and then add this lesson.

        Series map: [README.md](README.md).
