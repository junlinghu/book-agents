        # Tutorial 2. Shop data and files

        ## Purpose

        Give the concierge two sensors: shop markdown under the Chapter 2 path jail, and the Chapter 4 SQLite shelf. The model still only proposes calls. The notebook from tutorial 1 still runs, as a second question at the bottom.

        ## What you should learn

        - A file tool should refuse paths that leave the docs folder.
- A shelf tool can run SQL that the model never gets to write.
- One assistant turn may request more than one tool.
- Low stock means on_hand is at or below the reorder point. The gap to par is a separate number.

        ## How this maps to the book

        | Tutorial idea | Book chapter and lab |
        |---|---|
        | `read_file` path jail | Chapter 2, `labs/common/tools.py` and `labs/ch02-your-first-loop/docs` |
| Shelf rows and low stock | Chapter 4, `labs/ch04-tools-and-sensors/sql_tools.py` |

        The café in these files is fictional. Prices, hours, and the shelf match the Local Shop Concierge labs. Do not point the tools at a private document.

        ## How to run

        From the repository root, with the virtualenv from `labs/README.md` active:

        ```bash
        jupyter notebook labs/tutorial/2-data-and-files.ipynb
        ```

        In VS Code or Cursor, open `labs/tutorial/2-data-and-files.ipynb` and choose Run All. The setup cell walks parent folders until it finds `labs/common/client.py`, so the kernel may start in `labs/tutorial` or at the repo root.

        Scripted demo (no API call):

        ```bash
        DEMO_MODE=1 jupyter nbconvert --to notebook --execute labs/tutorial/2-data-and-files.ipynb --output /tmp/2-data-and-files-out.ipynb
        ```

        Live Chat Completions API:

        ```bash
        DEMO_MODE=0 jupyter nbconvert --to notebook --execute labs/tutorial/2-data-and-files.ipynb --output /tmp/2-data-and-files-out.ipynb
        ```

        `DEMO_MODE=0` needs `OPENAI_API_KEY` in the repo-root `.env`. `DEMO_MODE` unset uses the API when a key is present and the scripted demo when it is not. The notebook's first code cell can also set `DEMO_MODE` to `True` or `False`.

        This notebook is standalone. The cells include the working code from earlier tutorials and then add this lesson.

        Series map: [README.md](README.md).
