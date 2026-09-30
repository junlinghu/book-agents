        # Tutorial 3. The agent loop

        ## Purpose

        Wrap the tutorial 1 exchange in a loop with a step cap and a repeated-call stop. The same low-stock question now takes more than one model call. Two extra runs show the harness stopping without writing a customer answer.

        ## What you should learn

        - Each model call is one step: look at the thread, maybe call tools, read the results.
- `max_steps` ends the loop. The harness does not invent the rest of the answer.
- The same tool call, with the same arguments, stops on the third try.
- A final answer is the turn where the model calls no tool.

        ## How this maps to the book

        | Tutorial idea | Book chapter and lab |
        |---|---|
        | Perceive, reason, act, observe | Chapter 2, `labs/ch02-your-first-loop/file_agent.py` |
| Stop reasons | Chapter 2, `labs/common/loop.py` (`final`, `max_steps`, `repeated_call`) |

        The café in these files is fictional. Prices, hours, and the shelf match the Local Shop Concierge labs. Do not point the tools at a private document.

        ## How to run

        From the repository root, with the virtualenv from `labs/README.md` active:

        ```bash
        jupyter notebook labs/tutorial/3-agent-loop.ipynb
        ```

        In VS Code or Cursor, open `labs/tutorial/3-agent-loop.ipynb` and choose Run All. The setup cell walks parent folders until it finds `labs/common/client.py`, so the kernel may start in `labs/tutorial` or at the repo root.

        Scripted demo (no API call):

        ```bash
        DEMO_MODE=1 jupyter nbconvert --to notebook --execute labs/tutorial/3-agent-loop.ipynb --output /tmp/3-agent-loop-out.ipynb
        ```

        Live Chat Completions API:

        ```bash
        DEMO_MODE=0 jupyter nbconvert --to notebook --execute labs/tutorial/3-agent-loop.ipynb --output /tmp/3-agent-loop-out.ipynb
        ```

        `DEMO_MODE=0` needs `OPENAI_API_KEY` in the repo-root `.env`. `DEMO_MODE` unset uses the API when a key is present and the scripted demo when it is not. The notebook's first code cell can also set `DEMO_MODE` to `True` or `False`.

        This notebook is standalone. The cells include the working code from earlier tutorials and then add this lesson.

        Series map: [README.md](README.md).
