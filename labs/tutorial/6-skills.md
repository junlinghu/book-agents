        # Tutorial 6. Skills as procedures

        ## Purpose

        Keep a procedure out of the system prompt until the question needs it. The recommend skill says to search memory and read the FAQ. Priya's allergy is already on disk from a previous shift. The FAQ, not the skill, lists the bun.

        ## What you should learn

        - A skill is a markdown procedure with a name. `load_skill` returns it.
- The skill must not become a second copy of the menu.
- Memory from tutorial 5 is an input to the procedure.
- If the FAQ lists no safe pastry, the answer says so and refuses a nut-free promise.

        ## How this maps to the book

        | Tutorial idea | Book chapter and lab |
        |---|---|
        | Skills as portable procedures | Chapter 7, `labs/ch07-skills-as-portable-procedures` |

        The café in these files is fictional. Prices, hours, and the shelf match the Local Shop Concierge labs. Do not point the tools at a private document.

        ## How to run

        From the repository root, with the virtualenv from `labs/README.md` active:

        ```bash
        jupyter notebook labs/tutorial/6-skills.ipynb
        ```

        In VS Code or Cursor, open `labs/tutorial/6-skills.ipynb` and choose Run All. The setup cell walks parent folders until it finds `labs/common/client.py`, so the kernel may start in `labs/tutorial` or at the repo root.

        Scripted demo (no API call):

        ```bash
        DEMO_MODE=1 jupyter nbconvert --to notebook --execute labs/tutorial/6-skills.ipynb --output /tmp/6-skills-out.ipynb
        ```

        Live Chat Completions API:

        ```bash
        DEMO_MODE=0 jupyter nbconvert --to notebook --execute labs/tutorial/6-skills.ipynb --output /tmp/6-skills-out.ipynb
        ```

        `DEMO_MODE=0` needs `OPENAI_API_KEY` in the repo-root `.env`. `DEMO_MODE` unset uses the API when a key is present and the scripted demo when it is not. The notebook's first code cell can also set `DEMO_MODE` to `True` or `False`.

        This notebook is standalone. The cells include the working code from earlier tutorials and then add this lesson.

        Series map: [README.md](README.md).
