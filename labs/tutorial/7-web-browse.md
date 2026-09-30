        # Tutorial 7. The web as an untrusted sensor

        ## Purpose

        Treat a web page as a sensor, not as a manager. The only URL is a local Mill and Birch fixture. The page names a wholesale price and also tries to give orders. The answer may quote the price as untrusted. It may not obey the orders.

        ## What you should learn

        - Allow-list the URL. Everything else is an error.
- Wrap the text so a person can see the boundary.
- Page instructions are data. They do not add tools.
- The shelf count still comes from SQLite, not from the page.

        ## How this maps to the book

        | Tutorial idea | Book chapter and lab |
        |---|---|
        | Fetch a page, do not treat it as instructions | Chapter 8, `labs/ch08-browsing-the-web` |

        The café in these files is fictional. Prices, hours, and the shelf match the Local Shop Concierge labs. Do not point the tools at a private document.

        ## How to run

        From the repository root, with the virtualenv from `labs/README.md` active:

        ```bash
        jupyter notebook labs/tutorial/7-web-browse.ipynb
        ```

        In VS Code or Cursor, open `labs/tutorial/7-web-browse.ipynb` and choose Run All. The setup cell walks parent folders until it finds `labs/common/client.py`, so the kernel may start in `labs/tutorial` or at the repo root.

        Scripted demo (no API call):

        ```bash
        DEMO_MODE=1 jupyter nbconvert --to notebook --execute labs/tutorial/7-web-browse.ipynb --output /tmp/7-web-browse-out.ipynb
        ```

        Live Chat Completions API:

        ```bash
        DEMO_MODE=0 jupyter nbconvert --to notebook --execute labs/tutorial/7-web-browse.ipynb --output /tmp/7-web-browse-out.ipynb
        ```

        `DEMO_MODE=0` needs `OPENAI_API_KEY` in the repo-root `.env`. `DEMO_MODE` unset uses the API when a key is present and the scripted demo when it is not. The notebook's first code cell can also set `DEMO_MODE` to `True` or `False`.

        This notebook is standalone. The cells include the working code from earlier tutorials and then add this lesson.

        Series map: [README.md](README.md).
