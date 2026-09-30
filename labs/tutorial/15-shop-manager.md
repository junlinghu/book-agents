        # Tutorial 15. Shop manager capstone

        ## Purpose

        Compose the earlier tutorials into one restock. The run loads the restock skill, reads low stock, policy, the oat-milk note, and shop memory, fetches the supplier page as untrusted text, verifies the house-blend and oat-milk gaps, and waits to write tickets. A second run passes the two approval tokens and writes the files. No card is charged.

        ## What you should learn

        - A capstone is the same tools and gates, in one workflow, not a new framework.
- Quantity is the shelf gap: 14 bags of HB-12 and 13 cartons of OM-32 on this seed.
- Confirmation is per call. Two tickets, two tokens.
- The supplier note still cannot set the quantity, and the page still cannot grant a charge.

        ## How this maps to the book

        | Tutorial idea | Book chapter and lab |
        |---|---|
        | One recorded restock from plan to ticket | Chapter 26, `labs/ch26-capstone-cafe-restock` |
| The pieces above | Chapters 2, 4, 5, 6, 7, 8, 11, 12, 16, 21, 22, 23, and 14/24 |

        The café in these files is fictional. Prices, hours, and the shelf match the Local Shop Concierge labs. Do not point the tools at a private document.

        ## How to run

        From the repository root, with the virtualenv from `labs/README.md` active:

        ```bash
        jupyter notebook labs/tutorial/15-shop-manager.ipynb
        ```

        In VS Code or Cursor, open `labs/tutorial/15-shop-manager.ipynb` and choose Run All. The setup cell walks parent folders until it finds `labs/common/client.py`, so the kernel may start in `labs/tutorial` or at the repo root.

        Scripted demo (no API call):

        ```bash
        DEMO_MODE=1 jupyter nbconvert --to notebook --execute labs/tutorial/15-shop-manager.ipynb --output /tmp/15-shop-manager-out.ipynb
        ```

        Live Chat Completions API:

        ```bash
        DEMO_MODE=0 jupyter nbconvert --to notebook --execute labs/tutorial/15-shop-manager.ipynb --output /tmp/15-shop-manager-out.ipynb
        ```

        `DEMO_MODE=0` needs `OPENAI_API_KEY` in the repo-root `.env`. `DEMO_MODE` unset uses the API when a key is present and the scripted demo when it is not. The notebook's first code cell can also set `DEMO_MODE` to `True` or `False`.

        This notebook is standalone. The cells include the working code from earlier tutorials and then add this lesson.

        Series map: [README.md](README.md).
