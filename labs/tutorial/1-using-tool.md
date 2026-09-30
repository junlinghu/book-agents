        # Tutorial 1. Tool calling

        ## Purpose

        Show the Chat Completions tool-calling round trip on one Hearth Lane question. The model does not open `policy.md`. Your function does. The model only sees the tool result, then writes the answer.

        ## What you should learn

        - The tool schema is a JSON object with a name, a description, and parameters.
- An assistant message can contain `tool_calls` instead of a final answer.
- You execute the call, append a `role: tool` message, and call the model again.
- A shop rule in the answer should come from that tool result.

        ## How this maps to the book

        | Tutorial idea | Book chapter and lab |
        |---|---|
        | One completion, no tools, as the contrast | Chapter 1, `labs/ch01-what-an-agent-is/hello_concierge.py` |
| Tool result goes back into the thread | Chapter 2, `labs/common/loop.py` |
| Tools are how the agent touches the shop | Chapter 4, `labs/ch04-tools-and-sensors` |

        The café in these files is fictional. Prices, hours, and the shelf match the Local Shop Concierge labs. Do not point the tools at a private document.

        ## How to run

        From the repository root, with the virtualenv from `labs/README.md` active:

        ```bash
        jupyter notebook labs/tutorial/1-using-tool.ipynb
        ```

        In VS Code or Cursor, open `labs/tutorial/1-using-tool.ipynb` and choose Run All. The setup cell walks parent folders until it finds `labs/common/client.py`, so the kernel may start in `labs/tutorial` or at the repo root.

        Scripted demo (no API call):

        ```bash
        DEMO_MODE=1 jupyter nbconvert --to notebook --execute labs/tutorial/1-using-tool.ipynb --output /tmp/1-using-tool-out.ipynb
        ```

        Live Chat Completions API:

        ```bash
        DEMO_MODE=0 jupyter nbconvert --to notebook --execute labs/tutorial/1-using-tool.ipynb --output /tmp/1-using-tool-out.ipynb
        ```

        `DEMO_MODE=0` needs `OPENAI_API_KEY` in the repo-root `.env`. `DEMO_MODE` unset uses the API when a key is present and the scripted demo when it is not. The notebook's first code cell can also set `DEMO_MODE` to `True` or `False`.

        This notebook is standalone. The cells include the working code from earlier tutorials and then add this lesson.

        Series map: [README.md](README.md).
