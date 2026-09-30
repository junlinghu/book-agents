        # Tutorial 9. Evals from a small failure set

        ## Purpose

        Start an eval set from behaviors you already care about: opened-coffee returns, shipping milk, and a canned answer that invents a Wi-Fi password. The grader looks at the text and the tool log. The canned row is supposed to fail.

        ## What you should learn

        - A case names the question, the required tool, phrases that must appear, and phrases that must not.
- Passing means the tool ran and the text matches. It does not mean the model felt confident.
- Keep the failure. Deleting it makes the set look healthier than the product is.
- The same agent loop from earlier tutorials produces the two live cases.

        ## How this maps to the book

        | Tutorial idea | Book chapter and lab |
        |---|---|
        | Graders over traces, including a failure you keep | Chapter 12, `labs/ch12-evals-from-real-failures` |

        The café in these files is fictional. Prices, hours, and the shelf match the Local Shop Concierge labs. Do not point the tools at a private document.

        ## How to run

        From the repository root, with the virtualenv from `labs/README.md` active:

        ```bash
        jupyter notebook labs/tutorial/9-evals.ipynb
        ```

        In VS Code or Cursor, open `labs/tutorial/9-evals.ipynb` and choose Run All. The setup cell walks parent folders until it finds `labs/common/client.py`, so the kernel may start in `labs/tutorial` or at the repo root.

        Scripted demo (no API call):

        ```bash
        DEMO_MODE=1 jupyter nbconvert --to notebook --execute labs/tutorial/9-evals.ipynb --output /tmp/9-evals-out.ipynb
        ```

        Live Chat Completions API:

        ```bash
        DEMO_MODE=0 jupyter nbconvert --to notebook --execute labs/tutorial/9-evals.ipynb --output /tmp/9-evals-out.ipynb
        ```

        `DEMO_MODE=0` needs `OPENAI_API_KEY` in the repo-root `.env`. `DEMO_MODE` unset uses the API when a key is present and the scripted demo when it is not. The notebook's first code cell can also set `DEMO_MODE` to `True` or `False`.

        This notebook is standalone. The cells include the working code from earlier tutorials and then add this lesson.

        Series map: [README.md](README.md).
