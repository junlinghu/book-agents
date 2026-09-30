        # Tutorial 14. Cost, latency, and a cache

        ## Purpose

        Ask for café hours twice in one loop. The first `read_shop_file` misses the cache. The second hits it. The ledger sums prompt tokens, completion tokens, latency, and an illustrative USD figure. `route_task` records which model class you would have picked. This lab still uses one model id.

        ## What you should learn

        - Usage belongs on the trace next to the answer, including failed or partial runs.
- A cache key is the tool name plus its arguments. Do not cache a ticket write.
- Routing is a decision you can log before you call a second model.
- The rates in the notebook are illustrative. They are not an invoice.

        ## How this maps to the book

        | Tutorial idea | Book chapter and lab |
        |---|---|
        | Honest totals, not a proxy that flatters the run | Chapter 14, `labs/ch14-production-signals-and-honest-metrics` |
| Cost, latency, and architecture choices | Chapter 24, `chapters/ch24-cost-latency-and-architecture` |

        The café in these files is fictional. Prices, hours, and the shelf match the Local Shop Concierge labs. Do not point the tools at a private document.

        ## How to run

        From the repository root, with the virtualenv from `labs/README.md` active:

        ```bash
        jupyter notebook labs/tutorial/14-cost-latency.ipynb
        ```

        In VS Code or Cursor, open `labs/tutorial/14-cost-latency.ipynb` and choose Run All. The setup cell walks parent folders until it finds `labs/common/client.py`, so the kernel may start in `labs/tutorial` or at the repo root.

        Scripted demo (no API call):

        ```bash
        DEMO_MODE=1 jupyter nbconvert --to notebook --execute labs/tutorial/14-cost-latency.ipynb --output /tmp/14-cost-latency-out.ipynb
        ```

        Live Chat Completions API:

        ```bash
        DEMO_MODE=0 jupyter nbconvert --to notebook --execute labs/tutorial/14-cost-latency.ipynb --output /tmp/14-cost-latency-out.ipynb
        ```

        `DEMO_MODE=0` needs `OPENAI_API_KEY` in the repo-root `.env`. `DEMO_MODE` unset uses the API when a key is present and the scripted demo when it is not. The notebook's first code cell can also set `DEMO_MODE` to `True` or `False`.

        This notebook is standalone. The cells include the working code from earlier tutorials and then add this lesson.

        Series map: [README.md](README.md).
