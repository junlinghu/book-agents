        # Tutorial 10. Autonomy policy

        ## Purpose

        Put a gate in front of side effects. Shelf reads are auto. `write_ticket` is confirm. `charge_card` is never, even with a token for that exact call. The first restock run prints a token and writes nothing. The second run passes the token and writes one file.

        ## What you should learn

        - The harness decides. The wording of the user message does not.
- A confirm token matches one tool name plus one argument object.
- A token never promotes a never-tier tool.
- This gate uses `labs.common.autonomy` for cards and email.

        ## How this maps to the book

        | Tutorial idea | Book chapter and lab |
        |---|---|
        | auto / confirm / never | Chapter 16, `labs/common/autonomy.py` and `labs/ch16-autonomy-policy` |

        The café in these files is fictional. Prices, hours, and the shelf match the Local Shop Concierge labs. Do not point the tools at a private document.

        ## How to run

        From the repository root, with the virtualenv from `labs/README.md` active:

        ```bash
        jupyter notebook labs/tutorial/10-autonomy-policy.ipynb
        ```

        In VS Code or Cursor, open `labs/tutorial/10-autonomy-policy.ipynb` and choose Run All. The setup cell walks parent folders until it finds `labs/common/client.py`, so the kernel may start in `labs/tutorial` or at the repo root.

        Scripted demo (no API call):

        ```bash
        DEMO_MODE=1 jupyter nbconvert --to notebook --execute labs/tutorial/10-autonomy-policy.ipynb --output /tmp/10-autonomy-policy-out.ipynb
        ```

        Live Chat Completions API:

        ```bash
        DEMO_MODE=0 jupyter nbconvert --to notebook --execute labs/tutorial/10-autonomy-policy.ipynb --output /tmp/10-autonomy-policy-out.ipynb
        ```

        `DEMO_MODE=0` needs `OPENAI_API_KEY` in the repo-root `.env`. `DEMO_MODE` unset uses the API when a key is present and the scripted demo when it is not. The notebook's first code cell can also set `DEMO_MODE` to `True` or `False`.

        This notebook is standalone. The cells include the working code from earlier tutorials and then add this lesson.

        Series map: [README.md](README.md).
